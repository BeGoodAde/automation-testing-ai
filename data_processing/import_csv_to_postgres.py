import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import numpy as np
from pathlib import Path
import sys
import logging
from datetime import datetime
import os
from sqlalchemy import create_engine
import warnings
import pytest
import subprocess
import json

# Suppress pandas warnings
warnings.filterwarnings('ignore')

class PostgreSQLDataImporter:
    """Handle CSV import to PostgreSQL with validation and error handling."""
    
    def __init__(self, db_config=None):
        """Initialize with database configuration."""
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'ecommerce_analytics_2025',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        self.connection = None
        self.engine = None
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration."""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'data_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_database(self):
        """Establish database connection."""
        try:
            # psycopg2 connection for direct SQL
            self.connection = psycopg2.connect(**self.db_config)
            
            # SQLAlchemy engine for pandas integration
            connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            self.engine = create_engine(connection_string)
            
            self.logger.info("✅ Database connection established")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def validate_csv_structure(self, df):
        """Validate CSV data structure and content."""
        self.logger.info("🔍 Validating CSV structure...")
        
        required_columns = ['OrderID', 'Product', 'Category', 'Quantity', 'Price', 'OrderDate', 'CustomerID', 'Country']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Data quality checks
        issues = []
        
        # Check for null values
        null_counts = df.isnull().sum()
        if null_counts.any():
            issues.append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
        
        # Check data types
        if not pd.api.types.is_numeric_dtype(df['Quantity']):
            issues.append("Quantity column is not numeric")
        
        if not pd.api.types.is_numeric_dtype(df['Price']):
            issues.append("Price column is not numeric")
        
        # Check for negative values
        if (df['Quantity'] <= 0).any():
            issues.append("Negative or zero quantities found")
        
        if (df['Price'] <= 0).any():
            issues.append("Negative or zero prices found")
        
        # Check date format
        try:
            pd.to_datetime(df['OrderDate'])
        except:
            issues.append("Invalid date format in OrderDate column")
        
        if issues:
            self.logger.warning(f"⚠️ Data quality issues found: {issues}")
        else:
            self.logger.info("✅ CSV structure validation passed")
        
        return issues
    
    def clean_data(self, df):
        """Clean and prepare data for import."""
        self.logger.info("🧹 Cleaning data...")
        
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Clean column names (remove extra spaces, standardize case)
        df_clean.columns = df_clean.columns.str.strip()
        
        # Handle missing values
        df_clean = df_clean.dropna()
        
        # Clean text columns
        text_columns = ['Product', 'Category', 'Country']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].str.strip().str.title()
        
        # Ensure proper data types
        df_clean['Quantity'] = pd.to_numeric(df_clean['Quantity'], errors='coerce')
        df_clean['Price'] = pd.to_numeric(df_clean['Price'], errors='coerce')
        df_clean['CustomerID'] = pd.to_numeric(df_clean['CustomerID'], errors='coerce')
        
        # Convert date
        df_clean['OrderDate'] = pd.to_datetime(df_clean['OrderDate'])
        
        # Remove invalid records
        df_clean = df_clean[
            (df_clean['Quantity'] > 0) & 
            (df_clean['Price'] > 0) & 
            (df_clean['CustomerID'] > 0)
        ]
        
        # Calculate total value if not present
        if 'TotalValue' not in df_clean.columns:
            df_clean['TotalValue'] = df_clean['Quantity'] * df_clean['Price']
        
        # Add customer segment if not present
        if 'CustomerSegment' not in df_clean.columns:
            # Simple segmentation based on total value
            df_clean['CustomerSegment'] = pd.cut(
                df_clean['TotalValue'], 
                bins=[0, 50, 200, float('inf')], 
                labels=['Bargain', 'Regular', 'Premium']
            )
        
        self.logger.info(f"✅ Data cleaned: {len(df)} -> {len(df_clean)} records")
        return df_clean
    
    def prepare_for_postgres(self, df):
        """Prepare DataFrame for PostgreSQL import."""
        self.logger.info("🔧 Preparing data for PostgreSQL...")
        
        # Rename columns to match database schema
        column_mapping = {
            'OrderID': 'order_id',
            'Product': 'product_name',
            'Category': 'category',
            'Quantity': 'quantity',
            'Price': 'unit_price',
            'TotalValue': 'total_value',
            'OrderDate': 'order_date',
            'CustomerID': 'customer_id',
            'Country': 'country',
            'CustomerSegment': 'customer_segment'
        }
        
        df_prepared = df.rename(columns=column_mapping)
        
        # Ensure we have all required columns
        required_columns = ['order_id', 'product_name', 'category', 'quantity', 'unit_price', 'total_value', 'order_date', 'customer_id', 'country', 'customer_segment']
        df_prepared = df_prepared[required_columns]
        
        # Format data types for PostgreSQL
        df_prepared['order_date'] = df_prepared['order_date'].dt.date
        df_prepared['unit_price'] = df_prepared['unit_price'].round(2)
        df_prepared['total_value'] = df_prepared['total_value'].round(2)
        
        self.logger.info("✅ Data prepared for PostgreSQL")
        return df_prepared
    
    def import_to_database(self, df, table_name='sales', batch_size=1000):
        """Import DataFrame to PostgreSQL database."""
        self.logger.info(f"📤 Importing {len(df)} records to {table_name} table...")
        
        try:
            # Clear existing data (optional)
            with self.engine.connect() as conn:
                conn.execute(f"TRUNCATE TABLE {table_name} CASCADE")
                conn.commit()
            
            # Import data in batches
            total_imported = 0
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]
                batch.to_sql(table_name, self.engine, if_exists='append', index=False, method='multi')
                total_imported += len(batch)
                
                if total_imported % 5000 == 0:
                    self.logger.info(f"   Imported {total_imported:,} records...")
            
            self.logger.info(f"✅ Successfully imported {total_imported:,} records")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Import failed: {e}")
            return False
    
    def update_aggregates(self):
        """Update customer and product aggregate tables."""
        self.logger.info("📊 Updating aggregate tables...")
        
        try:
            with self.connection.cursor() as cursor:
                # Update customer aggregates
                cursor.execute("SELECT update_customer_aggregates();")
                
                # Update product aggregates
                cursor.execute("SELECT update_product_aggregates();")
                
                self.connection.commit()
                
                self.logger.info("✅ Aggregate tables updated")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update aggregates: {e}")
            return False
    
    def generate_import_report(self):
        """Generate import summary report."""
        self.logger.info("📋 Generating import report...")
        
        try:
            with self.engine.connect() as conn:
                # Get basic stats
                result = conn.execute("SELECT COUNT(*) as total_records FROM sales").fetchone()
                total_records = result[0]
                
                result = conn.execute("SELECT SUM(total_value) as total_revenue FROM sales").fetchone()
                total_revenue = result[0]
                
                result = conn.execute("SELECT COUNT(DISTINCT customer_id) as unique_customers FROM sales").fetchone()
                unique_customers = result[0]
                
                result = conn.execute("SELECT COUNT(DISTINCT product_name) as unique_products FROM sales").fetchone()
                unique_products = result[0]
                
                result = conn.execute("SELECT MIN(order_date) as min_date, MAX(order_date) as max_date FROM sales").fetchone()
                min_date, max_date = result[0], result[1]
                
                # Category breakdown
                category_stats = pd.read_sql("""
                    SELECT category, 
                           COUNT(*) as orders,
                           SUM(total_value) as revenue,
                           AVG(total_value) as avg_order_value
                    FROM sales 
                    GROUP BY category 
                    ORDER BY revenue DESC
                """, conn)
                
                report = f"""
📊 DATA IMPORT REPORT
==========================================
✅ Import Status: SUCCESS
📅 Import Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 SUMMARY STATISTICS:
- Total Records: {total_records:,}
- Total Revenue: ${total_revenue:,.2f}
- Unique Customers: {unique_customers:,}
- Unique Products: {unique_products:,}
- Date Range: {min_date} to {max_date}
- Average Order Value: ${total_revenue/total_records:.2f}

📊 CATEGORY BREAKDOWN:
{category_stats.to_string(index=False)}

🎯 NEXT STEPS:
1. Run analysis queries
2. Create visualizations
3. Generate insights report
4. Update documentation
==========================================
"""
                
                self.logger.info(report)
                
                # Save report to file
                report_dir = Path(__file__).parent.parent / 'reports'
                report_dir.mkdir(exist_ok=True)
                
                with open(report_dir / f'import_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w') as f:
                    f.write(report)
                
                return report
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate report: {e}")
            return None
    
    def close_connections(self):
        """Close database connections."""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.logger.info("🔌 Database connections closed")


def main():
    """Main import process."""
    print("🚀 CSV to PostgreSQL Import Pipeline")
    print("=" * 50)
    
    # Initialize importer
    importer = PostgreSQLDataImporter()
    
    # Connect to database
    if not importer.connect_database():
        print("❌ Failed to connect to database")
        return False
    
    try:
        # Load CSV data
        data_file = Path(__file__).parent.parent / 'data' / 'online_retail_2025.csv'
        
        if not data_file.exists():
            print(f"❌ Data file not found: {data_file}")
            print("Please run the data generation script first:")
            print("python data_generation/generate_ecommerce_data.py")
            return False
        
        print(f"📂 Loading data from: {data_file}")
        df = pd.read_csv(data_file)
        print(f"📊 Loaded {len(df):,} records")
        
        # Validate data
        issues = importer.validate_csv_structure(df)
        if issues:
            print("⚠️ Data quality issues found but continuing with cleaning...")
        
        # Clean data
        df_clean = importer.clean_data(df)
        
        # Prepare for PostgreSQL
        df_prepared = importer.prepare_for_postgres(df_clean)
        
        # Import to database
        if importer.import_to_database(df_prepared):
            print("✅ Data import successful")
            
            # Update aggregates
            importer.update_aggregates()
            
            # Generate report
            report = importer.generate_import_report()
            
            print("\n🎉 Import process completed successfully!")
            return True
        else:
            print("❌ Data import failed")
            return False
    
    except Exception as e:
        print(f"💥 Import process failed: {e}")
        return False
    
    finally:
        importer.close_connections()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

class ProjectVerificationSuite:
    """Comprehensive verification suite for the automation testing project."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.test_results = {}
        
    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps and color coding."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[36m",
            "SUCCESS": "\033[32m", 
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
            "HEADER": "\033[95m"
        }
        reset = "\033[0m"
        print(f"[{timestamp}] {colors.get(level, '')}{level}: {message}{reset}")

    def verify_project_structure(self):
        """Verify that all required project files and directories exist."""
        self.log("🔍 Verifying Project Structure", "HEADER")
        
        required_files = [
            # Core project files
            "README.md",
            "pytest.ini", 
            "conftest.py",
            "package.json",
            ".gitignore",
            
            # Python analysis files
            "data-analysis.py",
            "verify_fixes.py",
            "test_automation_health.py",
            "test_cleaning.py",
            
            # JavaScript files
            "data-analysis.js",
            "calculator.js",
            "calculator.test.js",
            
            # Data files
            "sample_sales_data.csv",
            
            # SQL files
            "sql/02_advanced_analytics.sql",
            
            # Docker and CI/CD
            "docker-compose.yml",
            ".pre-commit-config.yaml"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                self.log(f"❌ Missing: {file_path}", "ERROR")
            else:
                self.log(f"✅ Found: {file_path}", "SUCCESS")
        
        if missing_files:
            self.errors.append(f"Missing project files: {missing_files}")
        
        return len(missing_files) == 0

    def verify_data_integrity(self):
        """Verify the sample sales data is properly formatted and complete."""
        self.log("📊 Verifying Data Integrity", "HEADER")
        
        try:
            csv_path = self.project_root / "sample_sales_data.csv"
            if not csv_path.exists():
                self.errors.append("sample_sales_data.csv not found")
                return False
            
            # Load and validate data
            df = pd.read_csv(csv_path)
            
            # Check data structure
            expected_columns = [
                'order_id', 'customer_id', 'order_date', 'product_name',
                'category', 'price', 'quantity', 'total', 'month', 'day_of_week'
            ]
            
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                self.errors.append(f"Missing columns in CSV: {missing_columns}")
                return False
            
            # Data quality checks
            checks = {
                "Non-empty dataset": len(df) > 0,
                "No null order_ids": df['order_id'].notna().all(),
                "Valid dates": pd.to_datetime(df['order_date'], errors='coerce').notna().all(),
                "Positive prices": (df['price'] > 0).all(),
                "Positive quantities": (df['quantity'] > 0).all(),
                "Valid totals": np.isclose(df['total'], df['price'] * df['quantity'], rtol=0.01).all()
            }
            
            failed_checks = []
            for check_name, result in checks.items():
                if result:
                    self.log(f"✅ {check_name}", "SUCCESS")
                else:
                    self.log(f"❌ {check_name}", "ERROR")
                    failed_checks.append(check_name)
            
            if failed_checks:
                self.errors.append(f"Data quality issues: {failed_checks}")
            
            # Summary statistics
            self.log(f"📈 Dataset Summary:", "INFO")
            self.log(f"   Records: {len(df):,}", "INFO")
            self.log(f"   Date range: {df['order_date'].min()} to {df['order_date'].max()}", "INFO")
            self.log(f"   Total revenue: ${df['total'].sum():,.2f}", "INFO")
            self.log(f"   Categories: {df['category'].nunique()}", "INFO")
            self.log(f"   Products: {df['product_name'].nunique()}", "INFO")
            self.log(f"   Customers: {df['customer_id'].nunique()}", "INFO")
            
            return len(failed_checks) == 0
            
        except Exception as e:
            self.errors.append(f"Data verification error: {e}")
            self.log(f"❌ Data verification failed: {e}", "ERROR")
            return False

    def verify_sql_analytics(self):
        """Verify SQL analytics queries are syntactically correct."""
        self.log("🗃️ Verifying SQL Analytics", "HEADER")
        
        try:
            sql_path = self.project_root / "sql" / "02_advanced_analytics.sql"
            if not sql_path.exists():
                self.errors.append("SQL analytics file not found")
                return False
            
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Basic SQL syntax checks
            sql_checks = {
                "Contains SELECT statements": "SELECT" in sql_content.upper(),
                "Contains analytics sections": "-- SECTION" in sql_content,
                "Has RFM analysis": "RFM" in sql_content.upper(),
                "Has cohort analysis": "cohort" in sql_content.lower(),
                "Has time series analysis": "time series" in sql_content.lower(),
                "Has customer segmentation": "customer.*segment" in sql_content.lower()
            }
            
            failed_sql_checks = []
            for check_name, result in sql_checks.items():
                if result:
                    self.log(f"✅ {check_name}", "SUCCESS")
                else:
                    self.log(f"❌ {check_name}", "ERROR")
                    failed_sql_checks.append(check_name)
            
            # Count query sections
            sections = sql_content.count("-- SECTION")
            self.log(f"📊 Found {sections} analytics sections", "INFO")
            
            if failed_sql_checks:
                self.errors.append(f"SQL analysis issues: {failed_sql_checks}")
            
            return len(failed_sql_checks) == 0
            
        except Exception as e:
            self.errors.append(f"SQL verification error: {e}")
            return False

    def verify_python_environment(self):
        """Verify Python environment and dependencies."""
        self.log("🐍 Verifying Python Environment", "HEADER")
        
        required_packages = [
            'pandas', 'numpy', 'matplotlib', 'seaborn', 
            'pytest', 'requests', 'pathlib'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                self.log(f"✅ {package} installed", "SUCCESS")
            except ImportError:
                self.log(f"❌ {package} missing", "ERROR")
                missing_packages.append(package)
        
        if missing_packages:
            self.errors.append(f"Missing Python packages: {missing_packages}")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            self.log(f"✅ Python {python_version.major}.{python_version.minor} is supported", "SUCCESS")
        else:
            self.warnings.append(f"Python {python_version.major}.{python_version.minor} may have compatibility issues")
        
        return len(missing_packages) == 0

    def verify_javascript_environment(self):
        """Verify JavaScript/Node.js environment."""
        self.log("📦 Verifying JavaScript Environment", "HEADER")
        
        try:
            # Check if Node.js is installed
            node_result = subprocess.run(['node', '--version'], 
                                       capture_output=True, text=True)
            if node_result.returncode == 0:
                self.log(f"✅ Node.js {node_result.stdout.strip()} installed", "SUCCESS")
            else:
                self.warnings.append("Node.js not found")
                return False
            
            # Check if npm is installed
            npm_result = subprocess.run(['npm', '--version'], 
                                      capture_output=True, text=True)
            if npm_result.returncode == 0:
                self.log(f"✅ npm {npm_result.stdout.strip()} installed", "SUCCESS")
            else:
                self.warnings.append("npm not found")
                return False
            
            # Check package.json
            package_json_path = self.project_root / "package.json"
            if package_json_path.exists():
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                if 'scripts' in package_data:
                    self.log("✅ npm scripts configured", "SUCCESS")
                if 'dependencies' in package_data or 'devDependencies' in package_data:
                    self.log("✅ Dependencies defined", "SUCCESS")
            
            return True
            
        except FileNotFoundError:
            self.warnings.append("Node.js/npm not found - JavaScript tests may not work")
            return False
        except Exception as e:
            self.warnings.append(f"JavaScript environment check failed: {e}")
            return False

    def run_test_suite(self):
        """Run the actual test suite to verify functionality."""
        self.log("🧪 Running Test Suite", "HEADER")
        
        try:
            # Run pytest with verbose output
            pytest_result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                '--tb=short', '-v', '--maxfail=5'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if pytest_result.returncode == 0:
                self.log("✅ All Python tests passed", "SUCCESS")
                test_success = True
            else:
                self.log("❌ Some Python tests failed", "ERROR")
                self.log(f"Test output: {pytest_result.stdout[-500:]}", "INFO")
                test_success = False
            
            # Run JavaScript tests if available
            if (self.project_root / "package.json").exists():
                try:
                    npm_test_result = subprocess.run([
                        'npm', 'test'
                    ], capture_output=True, text=True, cwd=self.project_root)
                    
                    if npm_test_result.returncode == 0:
                        self.log("✅ JavaScript tests passed", "SUCCESS")
                    else:
                        self.log("❌ JavaScript tests failed", "WARNING")
                        
                except Exception as e:
                    self.log(f"⚠️ Could not run JavaScript tests: {e}", "WARNING")
            
            return test_success
            
        except Exception as e:
            self.errors.append(f"Test execution error: {e}")
            return False

    def verify_data_analysis_functionality(self):
        """Test the data analysis functionality."""
        self.log("📊 Verifying Data Analysis Functionality", "HEADER")
        
        try:
            # Import the data analysis module
            sys.path.append(str(self.project_root))
            
            # Test data generation
            from data_analysis import generate_sample_data, SalesAnalyzer
            
            # Generate small test dataset
            test_df = generate_sample_data(100)
            
            if len(test_df) == 100:
                self.log("✅ Data generation works", "SUCCESS")
            else:
                self.log("❌ Data generation failed", "ERROR")
                return False
            
            # Test analyzer
            analyzer = SalesAnalyzer()
            analyzer.data = test_df
            
            # Test basic metrics
            metrics = analyzer.calculate_metrics()
            if metrics and len(metrics) > 0:
                self.log("✅ Metrics calculation works", "SUCCESS")
            else:
                self.log("❌ Metrics calculation failed", "ERROR")
                return False
            
            # Test product analysis
            product_analysis = analyzer.product_analysis()
            if product_analysis is not None:
                self.log("✅ Product analysis works", "SUCCESS")
            else:
                self.log("❌ Product analysis failed", "ERROR")
                return False
            
            return True
            
        except ImportError as e:
            self.errors.append(f"Could not import data analysis module: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Data analysis verification error: {e}")
            return False

    def run(self):
        """Run the full verification suite."""
        self.log("🚀 Starting Project Verification Suite", "HEADER")
        
        # Step 1: Verify project structure
        structure_ok = self.verify_project_structure()
        
        # Step 2: Verify data integrity
        data_integrity_ok = self.verify_data_integrity()
        
        # Step 3: Verify SQL analytics
        sql_analytics_ok = self.verify_sql_analytics()
        
        # Step 4: Verify Python environment
        python_env_ok = self.verify_python_environment()
        
        # Step 5: Verify JavaScript environment
        javascript_env_ok = self.verify_javascript_environment()
        
        # Step 6: Run test suite
        test_suite_ok = self.run_test_suite()
        
        # Step 7: Verify data analysis functionality
        data_analysis_ok = self.verify_data_analysis_functionality()
        
        # Compile results
        self.test_results = {
            "Project Structure": structure_ok,
            "Data Integrity": data_integrity_ok,
            "SQL Analytics": sql_analytics_ok,
            "Python Environment": python_env_ok,
            "JavaScript Environment": javascript_env_ok,
            "Test Suite": test_suite_ok,
            "Data Analysis Functionality": data_analysis_ok
        }
        
        # Log summary
        self.log("\n📋 Verification Summary:", "HEADER")
        for test, result in self.test_results.items():
            status = "✅ Passed" if result else "❌ Failed"
            self.log(f" - {test}: {status}", "INFO")
        
        if self.errors:
            self.log("\n❌ Errors:", "ERROR")
            for error in self.errors:
                self.log(f" - {error}", "ERROR")
        
        if self.warnings:
            self.log("\n⚠️ Warnings:", "WARNING")
            for warning in self.warnings:
                self.log(f" - {warning}", "WARNING")
        
        self.log("\n✅ Verification suite completed", "SUCCESS")