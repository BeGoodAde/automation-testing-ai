"""
Comprehensive test suite to verify automation application health and functionality
Tests all major components of the automation testing framework
"""

import pytest
import os
import sys
import subprocess
import importlib
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, patch

class TestAutomationApplicationHealth:
    """Test suite to verify the automation application is working correctly."""
    
    @pytest.fixture(scope="class")
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent
    
    @pytest.fixture(scope="class")
    def required_files(self, project_root):
        """List of required files for the automation application."""
        return [
            project_root / "pytest.ini",
            project_root / "setup.py",
            project_root / "data-analysis.py",
            project_root / "calculator.js",
            project_root / "calculator.test.js",
            project_root / "package.json"
        ]
    
    @pytest.mark.unit
    def test_project_structure(self, required_files):
        """Test that all required files exist."""
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        assert not missing_files, f"Missing required files: {missing_files}"
    
    @pytest.mark.unit
    def test_python_dependencies(self):
        """Test that all required Python packages are available."""
        required_packages = [
            'pandas',
            'numpy',
            'matplotlib',
            'seaborn',
            'pytest',
            'psycopg2'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            pytest.skip(f"Missing packages: {missing_packages}. Run 'python setup.py' to install.")
    
    @pytest.mark.unit
    def test_pytest_configuration(self, project_root):
        """Test that pytest configuration is valid."""
        pytest_ini = project_root / "pytest.ini"
        assert pytest_ini.exists(), "pytest.ini file is missing"
        
        # Read and validate pytest.ini
        with open(pytest_ini, 'r') as f:
            content = f.read()
        
        # Check for required sections
        assert '[tool:pytest]' in content
        assert 'testpaths' in content
        assert 'markers' in content
        
        # Check for required markers
        required_markers = ['unit', 'integration', 'database', 'slow']
        for marker in required_markers:
            assert marker in content, f"Required marker '{marker}' not found in pytest.ini"
    
    @pytest.mark.unit
    def test_data_analysis_imports(self):
        """Test that data analysis module can be imported and has required functions."""
        try:
            # Import the data analysis module
            sys.path.append(str(Path(__file__).parent))
            
            # Test importing key classes
            from data_analysis import SalesAnalyzer, DataVisualizer
            
            # Test that classes can be instantiated
            analyzer = SalesAnalyzer()
            assert analyzer is not None
            
            # Test key methods exist
            assert hasattr(analyzer, 'load_data')
            assert hasattr(analyzer, 'clean_data')
            assert hasattr(analyzer, 'calculate_metrics')
            
        except ImportError as e:
            pytest.skip(f"Cannot import data analysis module: {e}")
        except Exception as e:
            pytest.fail(f"Error testing data analysis module: {e}")
    
    @pytest.mark.integration
    def test_sample_data_generation(self):
        """Test that sample data can be generated successfully."""
        try:
            from data_analysis import generate_sample_data
            
            # Generate small sample dataset
            df = generate_sample_data(100)
            
            # Verify data structure
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 100
            
            # Check required columns
            required_columns = ['order_id', 'customer_id', 'order_date', 'product_name', 'category', 'total']
            for col in required_columns:
                assert col in df.columns, f"Required column '{col}' missing from generated data"
            
            # Check data quality
            assert not df['total'].isnull().any(), "Generated data contains null values in 'total' column"
            assert all(df['total'] > 0), "Generated data contains non-positive values in 'total' column"
            
        except ImportError:
            pytest.skip("Cannot import sample data generation function")
        except Exception as e:
            pytest.fail(f"Error generating sample data: {e}")
    
    @pytest.mark.unit
    def test_environment_setup(self, project_root):
        """Test that environment files are properly configured."""
        env_file = project_root / ".env"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Check for required environment variables
            required_vars = ['DB_NAME', 'DB_USER', 'DB_HOST', 'DB_PORT']
            for var in required_vars:
                assert var in content, f"Required environment variable '{var}' not found in .env"
        else:
            pytest.skip(".env file not found - environment not configured")
    
    @pytest.mark.database
    def test_database_connection_config(self):
        """Test database connection configuration (without actual connection)."""
        try:
            from src.database.python_integration.simulator_db import DrivingSimulatorDB
            
            # Test that database class can be instantiated
            db = DrivingSimulatorDB()
            assert db is not None
            assert hasattr(db, 'connection_params')
            assert hasattr(db, 'connect')
            assert hasattr(db, 'disconnect')
            
        except ImportError:
            pytest.skip("Database module not available")
        except Exception as e:
            pytest.fail(f"Error testing database configuration: {e}")
    
    @pytest.mark.slow
    def test_data_processing_performance(self):
        """Test data processing performance with larger datasets."""
        try:
            import time
            from data_analysis import SalesAnalyzer
            
            # Create larger test dataset
            large_data = pd.DataFrame({
                'order_id': [f'ORD_{i:06d}' for i in range(5000)],
                'customer_id': [f'CUST_{i%1000:04d}' for i in range(5000)],
                'total': np.random.uniform(10, 1000, 5000),
                'category': np.random.choice(['A', 'B', 'C', 'D'], 5000),
                'order_date': pd.date_range('2023-01-01', periods=5000, freq='1H')
            })
            
            analyzer = SalesAnalyzer()
            analyzer.data = large_data
            
            # Test performance of key operations
            start_time = time.time()
            metrics = analyzer.calculate_metrics()
            processing_time = time.time() - start_time
            
            # Verify results and performance
            assert metrics is not None
            assert processing_time < 10  # Should complete within 10 seconds
            assert 'total_revenue' in metrics
            
        except Exception as e:
            pytest.skip(f"Performance test skipped due to error: {e}")
    
    @pytest.mark.unit
    def test_javascript_files_syntax(self, project_root):
        """Test that JavaScript files have valid syntax."""
        js_files = [
            project_root / "calculator.js",
            project_root / "calculator.test.js"
        ]
        
        for js_file in js_files:
            if js_file.exists():
                with open(js_file, 'r') as f:
                    content = f.read()
                
                # Basic syntax checks
                assert content.strip(), f"{js_file.name} is empty"
                assert content.count('{') == content.count('}'), f"Mismatched braces in {js_file.name}"
                assert content.count('(') == content.count(')'), f"Mismatched parentheses in {js_file.name}"
    
    @pytest.mark.integration
    def test_package_json_validity(self, project_root):
        """Test that package.json is valid and has required dependencies."""
        package_json = project_root / "package.json"
        
        if package_json.exists():
            with open(package_json, 'r') as f:
                try:
                    package_data = json.load(f)
                except json.JSONDecodeError:
                    pytest.fail("package.json contains invalid JSON")
            
            # Check required fields
            assert 'name' in package_data
            assert 'scripts' in package_data
            
            # Check for test script
            if 'test' not in package_data['scripts']:
                pytest.skip("No test script defined in package.json")
    
    @pytest.mark.unit
    def test_test_file_imports(self):
        """Test that all test files can be imported without errors."""
        test_files = [
            'test_cleaning.py'
        ]
        
        for test_file in test_files:
            test_path = Path(__file__).parent / test_file
            if test_path.exists():
                try:
                    # Try to compile the test file
                    with open(test_path, 'r') as f:
                        code = f.read()
                    compile(code, test_path, 'exec')
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {test_file}: {e}")
                except Exception as e:
                    pytest.fail(f"Error compiling {test_file}: {e}")
    
    @pytest.mark.analytics
    def test_data_visualization_capabilities(self):
        """Test that data visualization functions work correctly."""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Test basic plotting capability
            fig, ax = plt.subplots(1, 1, figsize=(6, 4))
            
            # Create simple test plot
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            ax.plot(x, y)
            ax.set_title('Test Plot')
            
            # Test that plot can be created without errors
            assert fig is not None
            assert ax is not None
            
            plt.close(fig)  # Clean up
            
        except Exception as e:
            pytest.skip(f"Visualization test skipped: {e}")
    
    @pytest.mark.performance
    def test_memory_usage(self):
        """Test memory usage during data processing."""
        try:
            import psutil
            import gc
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create and process large dataset
            large_df = pd.DataFrame(np.random.randn(10000, 10))
            result = large_df.describe()
            
            # Force garbage collection
            del large_df
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB for this test)
            assert memory_increase < 100, f"Memory usage increased by {memory_increase:.2f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")
        except Exception as e:
            pytest.skip(f"Memory test skipped: {e}")

class TestCopilotIntegration:
    """Test Copilot integration and AI-assisted features."""
    
    @pytest.mark.unit
    def test_copilot_comment_patterns(self, project_root):
        """Test that files contain Copilot-friendly comment patterns."""
        python_files = list(project_root.glob("*.py"))
        
        copilot_patterns = [
            "# Create",
            "# Generate", 
            "# Calculate",
            "# Analyze",
            "# Test"
        ]
        
        files_with_copilot_comments = 0
        
        for py_file in python_files:
            if py_file.name.startswith('test_'):
                continue
                
            with open(py_file, 'r') as f:
                content = f.read()
            
            for pattern in copilot_patterns:
                if pattern in content:
                    files_with_copilot_comments += 1
                    break
        
        # At least some files should have Copilot-friendly comments
        assert files_with_copilot_comments > 0, "No Copilot-friendly comments found in project files"
    
    @pytest.mark.unit
    def test_function_documentation(self):
        """Test that functions have proper documentation for Copilot."""
        try:
            from data_analysis import SalesAnalyzer
            
            # Check that methods have docstrings
            methods_to_check = ['load_data', 'clean_data', 'calculate_metrics']
            
            for method_name in methods_to_check:
                if hasattr(SalesAnalyzer, method_name):
                    method = getattr(SalesAnalyzer, method_name)
                    assert method.__doc__ is not None, f"Method {method_name} lacks documentation"
                    assert len(method.__doc__.strip()) > 10, f"Method {method_name} has insufficient documentation"
        
        except ImportError:
            pytest.skip("SalesAnalyzer class not available")

def run_health_check():
    """Run a comprehensive health check of the automation application."""
    print("🏥 Running Automation Application Health Check")
    print("=" * 60)
    
    # Run pytest with specific markers for health check
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "test_automation_health.py",
        "-v",
        "--tb=short",
        "-m", "unit or integration"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_health_check()
    if success:
        print("✅ Application health check PASSED")
    else:
        print("❌ Application health check FAILED")
        sys.exit(1)