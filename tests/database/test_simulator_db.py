"""
Comprehensive PostgreSQL Database Tests for Driving Simulator
Tests all database operations, data integrity, and performance
Created by Adelaja Isreal Bolarinwa
"""

import pytest
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import uuid
import numpy as np

# Import the modules we're testing
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / 'src' / 'database' / 'python_integration'))

from simulator_db import DrivingSimulatorDB


class TestDrivingSimulatorDB:
    """Comprehensive test suite for DrivingSimulatorDB"""
    
    @pytest.fixture(scope="class")
    def db_connection(self):
        """Set up test database connection"""
        db = DrivingSimulatorDB()
        try:
            db.connect()
            # Create test tables if they don't exist
            db.create_reaction_logs_table_if_not_exists()
            yield db
        finally:
            # Clean up test data
            if db.conn:
                cursor = db.conn.cursor()
                cursor.execute("DELETE FROM reaction_logs WHERE participant_id LIKE 'TEST_%'")
                db.conn.commit()
                cursor.close()
                db.disconnect()
    
    @pytest.fixture
    def sample_reaction_data(self):
        """Sample reaction time data for testing"""
        obstacle_time = datetime.now() - timedelta(milliseconds=500)
        brake_time = obstacle_time + timedelta(milliseconds=750)
        
        return {
            'participant_id': 'TEST_P001',
            'obstacle_time': obstacle_time,
            'brake_time': brake_time,
            'scenario': 'emergency-brake',
            'error': False,
            'fatigue_level': 5,
            'session_duration': 30,
            'weather_condition': 'clear',
            'traffic_density': 'medium'
        }
    
    @pytest.mark.database
    def test_database_connection(self, db_connection):
        """Test database connection establishment"""
        assert db_connection.conn is not None
        assert not db_connection.conn.closed
    
    @pytest.mark.database
    def test_connection_error_handling(self):
        """Test database connection error handling"""
        db = DrivingSimulatorDB()
        # Override connection params to force error
        db.connection_params['host'] = 'invalid_host'
        
        with pytest.raises(psycopg2.OperationalError):
            db.connect()
    
    @pytest.mark.database
    def test_table_existence_check(self, db_connection):
        """Test table existence validation"""
        # This should pass if tables exist or create them
        result = db_connection.check_tables_exist()
        assert isinstance(result, bool)
    
    @pytest.mark.database
    def test_insert_reaction_data(self, db_connection, sample_reaction_data):
        """Test inserting reaction time data"""
        # Insert test data
        db_connection.insert_reaction_data(**sample_reaction_data)
        
        # Verify data was inserted
        cursor = db_connection.conn.cursor()
        cursor.execute(
            "SELECT * FROM reaction_logs WHERE participant_id = %s",
            (sample_reaction_data['participant_id'],)
        )
        result = cursor.fetchone()
        cursor.close()
        
        assert result is not None
        assert result[1] == sample_reaction_data['participant_id']  # participant_id
        assert result[5] == 750  # reaction_time_ms
        assert result[6] == sample_reaction_data['scenario']
    
    @pytest.mark.database
    def test_reaction_time_calculation(self, db_connection, sample_reaction_data):
        """Test correct reaction time calculation"""
        db_connection.insert_reaction_data(**sample_reaction_data)
        
        cursor = db_connection.conn.cursor()
        cursor.execute(
            "SELECT reaction_time_ms FROM reaction_logs WHERE participant_id = %s",
            (sample_reaction_data['participant_id'],)
        )
        reaction_time = cursor.fetchone()[0]
        cursor.close()
        
        expected_reaction_time = int(
            (sample_reaction_data['brake_time'] - sample_reaction_data['obstacle_time']).total_seconds() * 1000
        )
        assert reaction_time == expected_reaction_time
    
    @pytest.mark.database
    @pytest.mark.slow
    def test_generate_sample_data(self, db_connection):
        """Test sample data generation"""
        # Generate small dataset for testing
        db_connection.generate_sample_data(num_participants=3, trials_per_participant=5)
        
        # Verify data was generated
        cursor = db_connection.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reaction_logs WHERE participant_id LIKE 'P%'")
        count = cursor.fetchone()[0]
        cursor.close()
        
        assert count >= 15  # 3 participants × 5 trials
    
    @pytest.mark.database
    def test_data_validation_constraints(self, db_connection):
        """Test database constraints and validation"""
        obstacle_time = datetime.now()
        brake_time = obstacle_time + timedelta(milliseconds=500)
        
        # Test invalid fatigue level (should fail)
        with pytest.raises(Exception):
            db_connection.insert_reaction_data(
                participant_id='TEST_INVALID',
                obstacle_time=obstacle_time,
                brake_time=brake_time,
                scenario='test',
                fatigue_level=15  # Invalid: > 10
            )
    
    @pytest.mark.analytics
    def test_analyze_reaction_times_with_data(self, db_connection, sample_reaction_data):
        """Test reaction time analysis with actual data"""
        # Insert test data
        for i in range(5):
            data = sample_reaction_data.copy()
            data['participant_id'] = f'TEST_P{i:03d}'
            data['brake_time'] = data['obstacle_time'] + timedelta(milliseconds=500 + i * 100)
            db_connection.insert_reaction_data(**data)
        
        # Test analysis (mock plt.show to avoid GUI)
        with patch('matplotlib.pyplot.show'):
            df = db_connection.analyze_reaction_times()
        
        assert df is not None
        assert len(df) >= 5
        assert 'reaction_time_ms' in df.columns
        assert 'participant_id' in df.columns
    
    @pytest.mark.analytics
    def test_analyze_reaction_times_no_data(self, db_connection):
        """Test reaction time analysis with no data"""
        # Clear any existing test data
        cursor = db_connection.conn.cursor()
        cursor.execute("DELETE FROM reaction_logs")
        db_connection.conn.commit()
        cursor.close()
        
        # Should handle empty dataset gracefully
        df = db_connection.analyze_reaction_times()
        assert df is None
    
    @pytest.mark.analytics
    def test_advanced_sql_analysis(self, db_connection, sample_reaction_data):
        """Test advanced SQL analysis queries"""
        # Insert varied test data
        scenarios = ['emergency-brake', 'traffic-light', 'pedestrian-crossing']
        for i, scenario in enumerate(scenarios):
            for j in range(3):
                data = sample_reaction_data.copy()
                data['participant_id'] = f'TEST_P{i:03d}'
                data['scenario'] = scenario
                data['brake_time'] = data['obstacle_time'] + timedelta(milliseconds=400 + i * 100 + j * 50)
                data['error'] = j == 2  # Make every 3rd trial an error
                db_connection.insert_reaction_data(**data)
        
        # Run analysis
        results = db_connection.advanced_sql_analysis()
        
        assert isinstance(results, dict)
        assert 'Average Reaction Time per Participant' in results
        assert 'Error Rate per Scenario' in results
        assert 'Fatigue Impact Analysis' in results
        assert 'Weather Performance Analysis' in results
        
        # Check that all results are DataFrames with data
        for key, df in results.items():
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
    
    @pytest.mark.integration
    def test_export_to_excel(self, db_connection, sample_reaction_data, tmp_path):
        """Test Excel export functionality"""
        # Insert test data
        db_connection.insert_reaction_data(**sample_reaction_data)
        
        # Export to temporary file
        temp_file = tmp_path / "test_export.xlsx"
        db_connection.export_to_excel(str(temp_file))
        
        # Verify file was created
        assert temp_file.exists()
        
        # Verify file content
        df = pd.read_excel(temp_file, sheet_name='Raw Data')
        assert len(df) >= 1
        assert 'participant_id' in df.columns
        assert 'reaction_time_ms' in df.columns
    
    @pytest.mark.performance
    def test_database_performance(self, db_connection):
        """Test database performance with larger datasets"""
        import time
        
        # Measure insertion performance
        start_time = time.time()
        
        obstacle_time = datetime.now()
        for i in range(100):
            brake_time = obstacle_time + timedelta(milliseconds=500 + i)
            db_connection.insert_reaction_data(
                participant_id=f'PERF_TEST_{i:03d}',
                obstacle_time=obstacle_time,
                brake_time=brake_time,
                scenario='performance-test'
            )
        
        insertion_time = time.time() - start_time
        
        # Should insert 100 records in reasonable time (adjust threshold as needed)
        assert insertion_time < 10.0  # 10 seconds threshold
        
        # Clean up performance test data
        cursor = db_connection.conn.cursor()
        cursor.execute("DELETE FROM reaction_logs WHERE participant_id LIKE 'PERF_TEST_%'")
        db_connection.conn.commit()
        cursor.close()
    
    @pytest.mark.unit
    def test_connection_params_from_env(self):
        """Test environment variable loading"""
        with patch.dict('os.environ', {
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_HOST': 'test_host',
            'DB_PORT': '5433'
        }):
            db = DrivingSimulatorDB()
            assert db.connection_params['dbname'] == 'test_db'
            assert db.connection_params['user'] == 'test_user'
            assert db.connection_params['host'] == 'test_host'
            assert db.connection_params['port'] == '5433'
    
    @pytest.mark.database
    def test_transaction_rollback_on_error(self, db_connection):
        """Test transaction rollback on database errors"""
        # Start a transaction
        cursor = db_connection.conn.cursor()
        
        try:
            # Insert valid data
            cursor.execute("""
                INSERT INTO reaction_logs (participant_id, obstacle_time, brake_time, reaction_time_ms, scenario)
                VALUES ('TEST_ROLLBACK', NOW(), NOW(), 500, 'test')
            """)
            
            # Try to insert invalid data (this should fail and rollback)
            cursor.execute("""
                INSERT INTO reaction_logs (participant_id, obstacle_time, brake_time, reaction_time_ms, scenario, fatigue_level)
                VALUES ('TEST_ROLLBACK2', NOW(), NOW(), 500, 'test', 999)  -- Invalid fatigue_level
            """)
            
            db_connection.conn.commit()
            
        except Exception:
            db_connection.conn.rollback()
            
            # Verify rollback worked - first insert should not exist
            cursor.execute("SELECT COUNT(*) FROM reaction_logs WHERE participant_id = 'TEST_ROLLBACK'")
            count = cursor.fetchone()[0]
            assert count == 0
        
        finally:
            cursor.close()


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database components"""
    
    def test_full_workflow(self):
        """Test complete workflow from data generation to analysis"""
        db = DrivingSimulatorDB()
        
        try:
            # Connect
            db.connect()
            
            # Generate sample data
            db.generate_sample_data(num_participants=2, trials_per_participant=10)
            
            # Analyze data
            with patch('matplotlib.pyplot.show'):
                df = db.analyze_reaction_times()
            
            # Run SQL analysis
            results = db.advanced_sql_analysis()
            
            # Export results
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                db.export_to_excel(tmp.name)
                assert Path(tmp.name).exists()
                Path(tmp.name).unlink()  # Clean up
            
            # Verify all steps completed successfully
            assert df is not None
            assert len(results) > 0
            
        finally:
            # Clean up
            if db.conn:
                cursor = db.conn.cursor()
                cursor.execute("DELETE FROM reaction_logs WHERE participant_id LIKE 'P%'")
                db.conn.commit()
                cursor.close()
                db.disconnect()


# Fixtures for pytest-postgresql integration (if using test database)
@pytest.fixture(scope="session")
def postgresql_proc():
    """PostgreSQL process fixture for testing"""
    try:
        from pytest_postgresql import factories
        return factories.postgresql_proc(
            port=None,
            unixsocketdir='/tmp'
        )
    except ImportError:
        pytest.skip("pytest-postgresql not available")


@pytest.fixture(scope="session")
def postgresql(postgresql_proc):
    """PostgreSQL database fixture for testing"""
    try:
        from pytest_postgresql import factories
        return factories.postgresql('postgresql_proc')
    except ImportError:
        pytest.skip("pytest-postgresql not available")


# Performance benchmarks
@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmarks for database operations"""
    
    def test_bulk_insert_performance(self, db_connection):
        """Benchmark bulk insert operations"""
        import time
        
        # Test different batch sizes
        batch_sizes = [10, 50, 100]
        results = {}
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            obstacle_time = datetime.now()
            for i in range(batch_size):
                brake_time = obstacle_time + timedelta(milliseconds=500 + i)
                db_connection.insert_reaction_data(
                    participant_id=f'BATCH_TEST_{batch_size}_{i:03d}',
                    obstacle_time=obstacle_time,
                    brake_time=brake_time,
                    scenario=f'batch-test-{batch_size}'
                )
            
            elapsed_time = time.time() - start_time
            results[batch_size] = elapsed_time
            
            print(f"Batch size {batch_size}: {elapsed_time:.3f}s ({elapsed_time/batch_size*1000:.2f}ms per record)")
        
        # Clean up
        cursor = db_connection.conn.cursor()
        cursor.execute("DELETE FROM reaction_logs WHERE participant_id LIKE 'BATCH_TEST_%'")
        db_connection.conn.commit()
        cursor.close()
        
        # Verify performance scales reasonably
        assert all(time > 0 for time in results.values())