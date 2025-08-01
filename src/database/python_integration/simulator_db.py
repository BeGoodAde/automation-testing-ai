"""
Enhanced PostgreSQL Integration for Driving Simulator
Combines your original requirements with advanced analytics
Created by Adelaja Isreal Bolarinwa
"""

import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import uuid
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv
    load_dotenv()

class DrivingSimulatorDB:
    """Enhanced PostgreSQL integration for driving simulator data analysis"""
    
    def __init__(self):
        """Initialize database connection"""
        self.connection_params = {
            'dbname': os.getenv('DB_NAME', 'driving_sim'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        self.conn = None
        
    def connect(self):
        """Establish database connection with better error handling"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            print("✅ Connected to PostgreSQL database successfully!")
            return self.conn
        except psycopg2.OperationalError as e:
            print(f"❌ Failed to connect to database: {e}")
            print("💡 Please ensure:")
            print("   1. PostgreSQL is running")
            print("   2. Database 'driving_sim' exists")
            print("   3. Credentials in .env file are correct")
            raise
        except Exception as e:
            print(f"❌ Unexpected error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("🔌 Database connection closed")
    
    def check_tables_exist(self):
        """Check if required tables exist in the database"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('reaction_logs', 'simulator_sessions', 'performance_metrics')
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            required_tables = ['reaction_logs', 'simulator_sessions', 'performance_metrics']
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                print(f"⚠️ Missing tables: {missing_tables}")
                print("💡 Please run the database schema setup:")
                print("   npm run db:setup")
                print("   or manually run the SQL schema file")
                return False
            
            print("✅ All required tables exist")
            return True
            
        except Exception as e:
            print(f"❌ Error checking tables: {e}")
            return False
        finally:
            cursor.close()
    
    def create_reaction_logs_table_if_not_exists(self):
        """Create reaction_logs table if it doesn't exist (fallback)"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reaction_logs (
                    id SERIAL PRIMARY KEY,
                    participant_id VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    obstacle_time TIMESTAMP NOT NULL,
                    brake_time TIMESTAMP NOT NULL,
                    reaction_time_ms INTEGER NOT NULL,
                    scenario VARCHAR(100) NOT NULL,
                    error BOOLEAN DEFAULT FALSE,
                    fatigue_level INTEGER CHECK (fatigue_level BETWEEN 1 AND 10),
                    session_duration INTEGER,
                    weather_condition VARCHAR(50),
                    traffic_density VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            print("✅ Created reaction_logs table")
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            self.conn.rollback()
            raise
        finally:
            cursor.close()
    
    def insert_reaction_data(self, participant_id, obstacle_time, brake_time, 
                           scenario, error=False, fatigue_level=5, session_duration=30,
                           weather_condition="clear", traffic_density="medium"):
        """
        Insert reaction time data with better error handling
        
        Args:
            participant_id (str): Participant identifier
            obstacle_time (datetime): When obstacle appeared
            brake_time (datetime): When participant braked
            scenario (str): Driving scenario
            error (bool): Whether an error occurred
            fatigue_level (int): Fatigue level 1-10
            session_duration (int): Session duration in minutes
            weather_condition (str): Weather condition
            traffic_density (str): Traffic density level
        """
        if not self.conn:
            self.connect()
        
        # Ensure table exists
        if not self.check_tables_exist():
            self.create_reaction_logs_table_if_not_exists()
        
        reaction_time_ms = int((brake_time - obstacle_time).total_seconds() * 1000)
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO reaction_logs 
                (participant_id, obstacle_time, brake_time, reaction_time_ms, 
                 scenario, error, fatigue_level, session_duration, 
                 weather_condition, traffic_density)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (participant_id, obstacle_time, brake_time, reaction_time_ms,
                  scenario, error, fatigue_level, session_duration,
                  weather_condition, traffic_density))
            
            self.conn.commit()
            print(f"✅ Inserted reaction data for {participant_id}: {reaction_time_ms}ms")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error inserting data: {e}")
            raise
        finally:
            cursor.close()
    
    def generate_sample_data(self, num_participants=10, trials_per_participant=50):
        """Generate realistic test data for simulation"""
        print(f"🎲 Generating sample data for {num_participants} participants...")
        
        scenarios = [
            "pedestrian-crossing", "vehicle-merge", "traffic-light", 
            "emergency-brake", "obstacle-avoidance", "lane-change",
            "intersection-stop", "highway-exit"
        ]
        
        weather_conditions = ["clear", "rainy", "foggy", "snowy"]
        traffic_densities = ["light", "medium", "heavy"]
        
        try:
            for participant_num in range(1, num_participants + 1):
                participant_id = f"P{participant_num:03d}"
                
                for trial in range(trials_per_participant):
                    # Simulate realistic reaction times (200-1500ms)
                    base_reaction = np.random.normal(550, 150)
                    
                    # Add scenario difficulty
                    scenario = np.random.choice(scenarios)
                    if scenario in ["emergency-brake", "obstacle-avoidance"]:
                        base_reaction += np.random.normal(100, 50)
                    
                    # Add fatigue effect
                    fatigue_level = np.random.randint(1, 11)
                    fatigue_penalty = (fatigue_level - 5) * 20
                    base_reaction += fatigue_penalty
                    
                    # Ensure realistic bounds
                    reaction_time_ms = max(200, min(1500, int(base_reaction)))
                    
                    # Calculate error probability
                    error_prob = 0.05 + (reaction_time_ms - 200) / 5000  # Higher for slower reactions
                    error = np.random.random() < error_prob
                    
                    # Generate timestamps
                    obstacle_time = datetime.now() - timedelta(
                        days=np.random.randint(0, 30),
                        hours=np.random.randint(0, 24),
                        minutes=np.random.randint(0, 60)
                    )
                    brake_time = obstacle_time + timedelta(milliseconds=reaction_time_ms)
                    
                    self.insert_reaction_data(
                        participant_id=participant_id,
                        obstacle_time=obstacle_time,
                        brake_time=brake_time,
                        scenario=scenario,
                        error=error,
                        fatigue_level=fatigue_level,
                        session_duration=np.random.randint(15, 60),
                        weather_condition=np.random.choice(weather_conditions),
                        traffic_density=np.random.choice(traffic_densities)
                    )
                
                if participant_num % 5 == 0:  # Progress indicator
                    print(f"   Generated data for {participant_num}/{num_participants} participants")
        
        except Exception as e:
            print(f"❌ Error generating sample data: {e}")
            raise
        
        print("✅ Sample data generation completed!")
    
    def analyze_reaction_times(self):
        """Analyze reaction times with enhanced visualizations"""
        if not self.conn:
            self.connect()
        
        try:
            # Load data
            query = """
            SELECT participant_id, reaction_time_ms, scenario, error, 
                   fatigue_level, weather_condition, traffic_density, timestamp
            FROM reaction_logs
            ORDER BY timestamp DESC
            """
            
            df = pd.read_sql(query, self.conn)
            
            if df.empty:
                print("⚠️ No data found in reaction_logs table")
                print("💡 Run 'npm run simulator:generate-data' to create sample data")
                return None
            
            print(f"📊 Loaded {len(df)} reaction time records")
            
            # Create comprehensive analysis plots
            plt.style.use('default')  # Use default style instead of deprecated seaborn
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('🏎️ Driving Simulator Reaction Time Analysis', fontsize=16, fontweight='bold')
            
            # 1. Overall reaction time distribution
            sns.histplot(data=df, x='reaction_time_ms', bins=30, kde=True, ax=axes[0,0])
            axes[0,0].set_title('Reaction Time Distribution')
            axes[0,0].set_xlabel('Reaction Time (ms)')
            
            # 2. Reaction time by scenario
            sns.boxplot(data=df, x='scenario', y='reaction_time_ms', ax=axes[0,1])
            axes[0,1].set_title('Reaction Time by Scenario')
            axes[0,1].tick_params(axis='x', rotation=45)
            
            # 3. Fatigue effect
            sns.scatterplot(data=df, x='fatigue_level', y='reaction_time_ms', 
                           hue='error', ax=axes[0,2])
            axes[0,2].set_title('Fatigue Level vs Reaction Time')
            
            # 4. Weather impact
            sns.boxplot(data=df, x='weather_condition', y='reaction_time_ms', ax=axes[1,0])
            axes[1,0].set_title('Weather Impact on Reaction Time')
            
            # 5. Traffic density effect
            sns.boxplot(data=df, x='traffic_density', y='reaction_time_ms', ax=axes[1,1])
            axes[1,1].set_title('Traffic Density Impact')
            
            # 6. Error rate by participant
            error_rates = df.groupby('participant_id')['error'].mean().reset_index()
            sns.barplot(data=error_rates.head(10), x='participant_id', y='error', ax=axes[1,2])
            axes[1,2].set_title('Error Rate by Participant (Top 10)')
            axes[1,2].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save plot
            output_path = project_root / 'reaction_time_analysis.png'
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"📊 Analysis plot saved to: {output_path}")
            plt.show()
            
            return df
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            raise
    
    def advanced_sql_analysis(self):
        """Run advanced SQL queries for insights"""
        if not self.conn:
            self.connect()
        
        queries = {
            "Average Reaction Time per Participant": """
                SELECT participant_id, 
                       ROUND(AVG(reaction_time_ms), 2) as avg_rt,
                       COUNT(*) as total_trials,
                       SUM(CASE WHEN error THEN 1 ELSE 0 END) as errors
                FROM reaction_logs
                GROUP BY participant_id
                ORDER BY avg_rt
                LIMIT 10;
            """,
            
            "Error Rate per Scenario": """
                SELECT scenario, 
                       COUNT(*) as total_trials, 
                       SUM(CASE WHEN error THEN 1 ELSE 0 END) as errors,
                       ROUND((SUM(CASE WHEN error THEN 1 ELSE 0 END)::float / COUNT(*) * 100), 2) as error_rate
                FROM reaction_logs
                GROUP BY scenario
                ORDER BY error_rate DESC;
            """,
            
            "Fatigue Impact Analysis": """
                SELECT fatigue_level,
                       ROUND(AVG(reaction_time_ms), 2) as avg_reaction_time,
                       COUNT(*) as trials,
                       ROUND((SUM(CASE WHEN error THEN 1 ELSE 0 END)::float / COUNT(*) * 100), 2) as error_rate
                FROM reaction_logs
                GROUP BY fatigue_level
                ORDER BY fatigue_level;
            """,
            
            "Weather Performance Analysis": """
                SELECT weather_condition,
                       ROUND(AVG(reaction_time_ms), 2) as avg_reaction_time,
                       ROUND(STDDEV(reaction_time_ms), 2) as reaction_time_variance,
                       COUNT(*) as trials
                FROM reaction_logs
                GROUP BY weather_condition
                ORDER BY avg_reaction_time DESC;
            """
        }
        
        results = {}
        try:
            for query_name, query in queries.items():
                print(f"\n📊 {query_name}:")
                print("=" * 50)
                df = pd.read_sql(query, self.conn)
                print(df.to_string(index=False))
                results[query_name] = df
        
        except Exception as e:
            print(f"❌ Error running SQL analysis: {e}")
            raise
        
        return results
    
    def export_to_excel(self, filename="driving_simulator_analysis.xlsx"):
        """Export analysis results to Excel"""
        if not self.conn:
            self.connect()
        
        try:
            output_path = project_root / filename
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Raw data
                df_raw = pd.read_sql("SELECT * FROM reaction_logs ORDER BY timestamp DESC", self.conn)
                df_raw.to_excel(writer, sheet_name='Raw Data', index=False)
                
                # Try to get views if they exist
                try:
                    df_performance = pd.read_sql("SELECT * FROM participant_performance ORDER BY avg_reaction_time", self.conn)
                    df_performance.to_excel(writer, sheet_name='Participant Performance', index=False)
                except:
                    print("⚠️ participant_performance view not found, skipping...")
                
                try:
                    df_scenarios = pd.read_sql("SELECT * FROM scenario_analysis", self.conn)
                    df_scenarios.to_excel(writer, sheet_name='Scenario Analysis', index=False)
                except:
                    print("⚠️ scenario_analysis view not found, skipping...")
            
            print(f"📊 Analysis exported to {output_path}")
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            raise

# Usage example and testing
def main():
    """Main function to demonstrate the enhanced database integration"""
    print("🏎️ Starting Enhanced Driving Simulator Database Analysis")
    print("=" * 60)
    
    # Initialize database
    db = DrivingSimulatorDB()
    
    try:
        # Connect to database
        db.connect()
        
        # Check if we have data
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reaction_logs")
        record_count = cursor.fetchone()[0]
        cursor.close()
        
        if record_count == 0:
            print("📝 No data found. Generating sample data...")
            db.generate_sample_data(num_participants=15, trials_per_participant=40)
        else:
            print(f"📊 Found {record_count} existing records")
        
        # Perform analysis
        print("\n📊 Analyzing reaction times...")
        df = db.analyze_reaction_times()
        
        if df is not None:
            print(f"\n📈 Dataset Summary:")
            print(f"   Total records: {len(df)}")
            print(f"   Participants: {df['participant_id'].nunique()}")
            print(f"   Scenarios: {df['scenario'].nunique()}")
            print(f"   Average reaction time: {df['reaction_time_ms'].mean():.2f}ms")
            print(f"   Error rate: {(df['error'].sum() / len(df) * 100):.2f}%")
            
            # Run advanced SQL analysis
            print("\n🔍 Running advanced SQL analysis...")
            results = db.advanced_sql_analysis()
            
            # Export to Excel
            print("\n📊 Exporting results to Excel...")
            db.export_to_excel()
            
            print("\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()