import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from pathlib import Path
import tempfile
import os
import sys
import logging
from datetime import datetime, date
import json
from import_csv_to_postgres import PostgreSQLDataImporter
from import_csv_to_postgres import main
from import_csv_to_postgres import main
from import_csv_to_postgres import main
import time
import time
import time

# Add the parent directory to sys.path to import the module
sys.path.insert(0, str(Path(__file__).parent))


class TestPostgreSQLDataImporter:
    """Comprehensive test suite for PostgreSQLDataImporter."""
    
    @pytest.fixture
    def sample_clean_data(self):
        """Create sample clean e-commerce data for testing."""
        return pd.DataFrame({
            'OrderID': ['ORD_001', 'ORD_002', 'ORD_003', 'ORD_004', 'ORD_005'],
            'Product': ['Laptop Pro', 'Wireless Mouse', 'USB Cable', 'Monitor', 'Keyboard'],
            'Category': ['Electronics', 'Electronics', 'Accessories', 'Electronics', 'Accessories'],
            'Quantity': [1, 2, 3, 1, 1],
            'Price': [1299.99, 49.99, 19.99, 299.99, 79.99],
            'OrderDate': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
            'CustomerID': [1001, 1002, 1003, 1004, 1005],
            'Country': ['USA', 'Canada', 'UK', 'Germany', 'France']
        })
    
    @pytest.fixture
    def sample_dirty_data(self):
        """Create sample dirty data with quality issues."""
        return pd.DataFrame({
            'OrderID': ['ORD_001', 'ORD_002', '', 'ORD_004', None],
            'Product': ['Laptop Pro', '  Wireless Mouse  ', 'USB Cable', None, 'Keyboard'],
            'Category': ['electronics', 'ELECTRONICS', 'accessories', 'Electronics', 'accessories'],
            'Quantity': [1, -2, 3, 0, 'invalid'],
            'Price': [1299.99, 49.99, -19.99, 299.99, 0],
            'OrderDate': ['2024-01-15', '2024-13-45', '2024-01-17', None, 'invalid_date'],
            'CustomerID': [1001, 1002, 1003, -1004, None],
            'Country': ['USA', 'canada', '  UK  ', 'Germany', None]
        })
    
    @pytest.fixture
    def mock_db_config(self):
        """Create mock database configuration."""
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }
    
    @pytest.fixture
    def importer(self, mock_db_config):
        """Create PostgreSQLDataImporter instance with mocked logging."""
        with patch('import_csv_to_postgres.logging.basicConfig'):
            with patch('import_csv_to_postgres.logging.getLogger') as mock_logger:
                mock_logger.return_value = Mock()
                importer = PostgreSQLDataImporter(mock_db_config)
                return importer
    
    @pytest.fixture
    def temp_csv_file(self, sample_clean_data):
        """Create temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_clean_data.to_csv(f.name, index=False)
            yield f.name
        os.unlink(f.name)

    @pytest.mark.unit
    def test_init_with_default_config(self):
        """Test initialization with default database configuration."""
        with patch('import_csv_to_postgres.logging.basicConfig'):
            with patch('import_csv_to_postgres.logging.getLogger'):
                importer = PostgreSQLDataImporter()
                
                assert importer.db_config['host'] == 'localhost'
                assert importer.db_config['port'] == 5432
                assert importer.db_config['database'] == 'ecommerce_analytics_2025'
                assert importer.db_config['user'] == 'postgres'
                assert importer.connection is None
                assert importer.engine is None

    @pytest.mark.unit
    def test_init_with_custom_config(self, mock_db_config):
        """Test initialization with custom database configuration."""
        with patch('import_csv_to_postgres.logging.basicConfig'):
            with patch('import_csv_to_postgres.logging.getLogger'):
                importer = PostgreSQLDataImporter(mock_db_config)
                
                assert importer.db_config == mock_db_config
                assert importer.db_config['database'] == 'test_db'

    @pytest.mark.unit
    @patch('import_csv_to_postgres.Path')
    @patch('import_csv_to_postgres.logging.basicConfig')
    @patch('import_csv_to_postgres.logging.getLogger')
    def test_setup_logging(self, mock_get_logger, mock_basic_config, mock_path):
        """Test logging setup with directory creation."""
        mock_log_dir = Mock()
        mock_path.return_value.parent.parent.__truediv__.return_value = mock_log_dir
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        importer = PostgreSQLDataImporter()
        
        # Verify log directory creation
        mock_log_dir.mkdir.assert_called_once_with(exist_ok=True)
        
        # Verify logging configuration
        mock_basic_config.assert_called_once()
        mock_get_logger.assert_called_once_with('import_csv_to_postgres')
        
        assert importer.logger == mock_logger

    @pytest.mark.unit
    @patch('import_csv_to_postgres.psycopg2.connect')
    @patch('import_csv_to_postgres.create_engine')
    def test_connect_database_success(self, mock_create_engine, mock_connect, importer):
        """Test successful database connection."""
        mock_connection = Mock()
        mock_engine = Mock()
        mock_connect.return_value = mock_connection
        mock_create_engine.return_value = mock_engine
        
        result = importer.connect_database()
        
        assert result is True
        assert importer.connection == mock_connection
        assert importer.engine == mock_engine
        
        # Verify connection parameters
        mock_connect.assert_called_once_with(**importer.db_config)
        
        # Verify SQLAlchemy engine creation
        expected_connection_string = "postgresql://test_user:test_pass@localhost:5432/test_db"
        mock_create_engine.assert_called_once_with(expected_connection_string)

    @pytest.mark.unit
    @patch('import_csv_to_postgres.psycopg2.connect')
    def test_connect_database_failure(self, mock_connect, importer):
        """Test database connection failure."""
        mock_connect.side_effect = Exception("Connection failed")
        
        result = importer.connect_database()
        
        assert result is False
        assert importer.connection is None
        assert importer.engine is None
        importer.logger.error.assert_called_with("❌ Database connection failed: Connection failed")

    @pytest.mark.unit
    def test_validate_csv_structure_success(self, importer, sample_clean_data):
        """Test CSV structure validation with clean data."""
        issues = importer.validate_csv_structure(sample_clean_data)
        
        assert issues == []
        importer.logger.info.assert_any_call("🔍 Validating CSV structure...")
        importer.logger.info.assert_any_call("✅ CSV structure validation passed")

    @pytest.mark.unit
    def test_validate_csv_structure_missing_columns(self, importer):
        """Test CSV structure validation with missing required columns."""
        incomplete_df = pd.DataFrame({
            'OrderID': ['ORD_001'],
            'Product': ['Laptop']
            # Missing other required columns
        })
        
        with pytest.raises(ValueError) as exc_info:
            importer.validate_csv_structure(incomplete_df)
        
        assert "Missing required columns" in str(exc_info.value)

    @pytest.mark.unit
    def test_validate_csv_structure_data_quality_issues(self, importer):
        """Test CSV structure validation with data quality issues."""
        problematic_df = pd.DataFrame({
            'OrderID': ['ORD_001', 'ORD_002'],
            'Product': ['Laptop', None],  # Null value
            'Category': ['Electronics', 'Electronics'],
            'Quantity': [-1, 2],  # Negative quantity
            'Price': [1299.99, 0],  # Zero price
            'OrderDate': ['2024-01-15', 'invalid_date'],  # Invalid date
            'CustomerID': [1001, 1002],
            'Country': ['USA', 'Canada']
        })
        
        issues = importer.validate_csv_structure(problematic_df)
        
        assert len(issues) > 0
        assert any("Null values found" in issue for issue in issues)
        assert any("Negative or zero quantities" in issue for issue in issues)
        assert any("Negative or zero prices" in issue for issue in issues)
        assert any("Invalid date format" in issue for issue in issues)

    @pytest.mark.unit
    def test_clean_data_comprehensive(self, importer, sample_dirty_data):
        """Test comprehensive data cleaning functionality."""
        original_length = len(sample_dirty_data)
        
        result = importer.clean_data(sample_dirty_data)
        
        # Verify cleaning results
        assert len(result) < original_length  # Some rows should be removed
        assert not result.isnull().any().any()  # No null values
        assert (result['Quantity'] > 0).all()  # All quantities positive
        assert (result['Price'] > 0).all()  # All prices positive
        assert (result['CustomerID'] > 0).all()  # All customer IDs positive
        
        # Verify text cleaning
        assert not result['Product'].str.contains('  ').any()  # No extra spaces
        assert result['Category'].str.istitle().all()  # Title case
        
        # Verify calculated columns
        assert 'TotalValue' in result.columns
        assert np.isclose(result['TotalValue'], result['Quantity'] * result['Price']).all()
        
        assert 'CustomerSegment' in result.columns
        assert result['CustomerSegment'].notna().all()

    @pytest.mark.unit
    def test_clean_data_preserves_valid_data(self, importer, sample_clean_data):
        """Test that clean data is preserved during cleaning."""
        original_length = len(sample_clean_data)
        
        result = importer.clean_data(sample_clean_data)
        
        # Should preserve most or all valid data
        assert len(result) == original_length or len(result) == original_length - 1
        assert 'TotalValue' in result.columns
        assert 'CustomerSegment' in result.columns

    @pytest.mark.unit
    def test_prepare_for_postgres(self, importer, sample_clean_data):
        """Test data preparation for PostgreSQL import."""
        # Add required columns for cleaning
        sample_clean_data['TotalValue'] = sample_clean_data['Quantity'] * sample_clean_data['Price']
        sample_clean_data['CustomerSegment'] = 'Regular'
        
        result = importer.prepare_for_postgres(sample_clean_data)
        
        # Verify column mapping
        expected_columns = [
            'order_id', 'product_name', 'category', 'quantity', 'unit_price', 
            'total_value', 'order_date', 'customer_id', 'country', 'customer_segment'
        ]
        assert list(result.columns) == expected_columns
        
        # Verify data types
        assert result['unit_price'].dtype == float
        assert result['total_value'].dtype == float
        
        # Verify date conversion
        assert all(isinstance(d, date) for d in result['order_date'])

    @pytest.mark.unit
    @patch.object(PostgreSQLDataImporter, 'engine')
    def test_import_to_database_success(self, mock_engine, importer):
        """Test successful database import."""
        # Setup mock
        mock_conn = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_engine.connect.return_value.__exit__.return_value = None
        
        # Prepare test data
        test_df = pd.DataFrame({
            'order_id': ['ORD_001', 'ORD_002'],
            'product_name': ['Laptop', 'Mouse'],
            'category': ['Electronics', 'Electronics'],
            'quantity': [1, 2],
            'unit_price': [999.99, 49.99],
            'total_value': [999.99, 99.98],
            'order_date': [date(2024, 1, 15), date(2024, 1, 16)],
            'customer_id': [1001, 1002],
            'country': ['USA', 'Canada'],
            'customer_segment': ['Premium', 'Regular']
        })
        
        # Mock to_sql method
        with patch.object(test_df, 'to_sql') as mock_to_sql:
            result = importer.import_to_database(test_df)
        
        assert result is True
        
        # Verify truncate was called
        mock_conn.execute.assert_called_with("TRUNCATE TABLE sales CASCADE")
        mock_conn.commit.assert_called()
        
        # Verify to_sql was called
        mock_to_sql.assert_called()

    @pytest.mark.unit
    @patch.object(PostgreSQLDataImporter, 'engine')
    def test_import_to_database_failure(self, mock_engine, importer):
        """Test database import failure handling."""
        mock_engine.connect.side_effect = Exception("Database error")
        
        test_df = pd.DataFrame({'test': [1, 2, 3]})
        
        result = importer.import_to_database(test_df)
        
        assert result is False
        importer.logger.error.assert_called_with("❌ Import failed: Database error")

    @pytest.mark.unit
    def test_import_to_database_batch_processing(self, importer):
        """Test batch processing during import."""
        # Create large dataset to test batching
        large_df = pd.DataFrame({
            'order_id': [f'ORD_{i:06d}' for i in range(2500)],
            'product_name': ['Product'] * 2500,
            'category': ['Electronics'] * 2500,
            'quantity': [1] * 2500,
            'unit_price': [99.99] * 2500,
            'total_value': [99.99] * 2500,
            'order_date': [date(2024, 1, 15)] * 2500,
            'customer_id': list(range(1001, 3501)),
            'country': ['USA'] * 2500,
            'customer_segment': ['Regular'] * 2500
        })
        
        with patch.object(importer, 'engine') as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_engine.connect.return_value.__exit__.return_value = None
            
            with patch.object(large_df, 'to_sql') as mock_to_sql:
                result = importer.import_to_database(large_df, batch_size=1000)
            
            assert result is True
            # Should be called 3 times for 2500 records with batch_size=1000
            assert mock_to_sql.call_count == 3

    @pytest.mark.unit
    def test_update_aggregates_success(self, importer):
        """Test successful aggregate tables update."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.cursor.return_value.__exit__.return_value = None
        importer.connection = mock_connection
        
        result = importer.update_aggregates()
        
        assert result is True
        mock_cursor.execute.assert_any_call("SELECT update_customer_aggregates();")
        mock_cursor.execute.assert_any_call("SELECT update_product_aggregates();")
        mock_connection.commit.assert_called_once()

    @pytest.mark.unit
    def test_update_aggregates_failure(self, importer):
        """Test aggregate update failure handling."""
        mock_connection = Mock()
        mock_connection.cursor.side_effect = Exception("SQL error")
        importer.connection = mock_connection
        
        result = importer.update_aggregates()
        
        assert result is False
        importer.logger.error.assert_called_with("❌ Failed to update aggregates: SQL error")

    @pytest.mark.unit
    @patch('import_csv_to_postgres.pd.read_sql')
    def test_generate_import_report_success(self, mock_read_sql, importer):
        """Test successful import report generation."""
        # Mock engine and connection
        mock_engine = Mock()
        mock_conn = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_engine.connect.return_value.__exit__.return_value = None
        importer.engine = mock_engine
        
        # Mock SQL query results
        mock_conn.execute.return_value.fetchone.side_effect = [
            (1000,),  # total_records
            (50000.00,),  # total_revenue
            (200,),  # unique_customers
            (50,),  # unique_products
            (date(2024, 1, 1), date(2024, 12, 31))  # date range
        ]
        
        # Mock category stats
        mock_category_stats = pd.DataFrame({
            'category': ['Electronics', 'Accessories'],
            'orders': [600, 400],
            'revenue': [30000.00, 20000.00],
            'avg_order_value': [50.00, 50.00]
        })
        mock_read_sql.return_value = mock_category_stats
        
        # Mock file operations
        with patch('import_csv_to_postgres.Path') as mock_path:
            mock_report_dir = Mock()
            mock_path.return_value.parent.parent.__truediv__.return_value = mock_report_dir
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = importer.generate_import_report()
        
        assert result is not None
        assert "DATA IMPORT REPORT" in result
        assert "Total Records: 1,000" in result
        assert "Total Revenue: $50,000.00" in result
        
        # Verify file operations
        mock_report_dir.mkdir.assert_called_once_with(exist_ok=True)
        mock_file.assert_called_once()

    @pytest.mark.unit
    def test_generate_import_report_failure(self, importer):
        """Test import report generation failure."""
        mock_engine = Mock()
        mock_engine.connect.side_effect = Exception("Database error")
        importer.engine = mock_engine
        
        result = importer.generate_import_report()
        
        assert result is None
        importer.logger.error.assert_called_with("❌ Failed to generate report: Database error")

    @pytest.mark.unit
    def test_close_connections(self, importer):
        """Test closing database connections."""
        mock_connection = Mock()
        mock_engine = Mock()
        importer.connection = mock_connection
        importer.engine = mock_engine
        
        importer.close_connections()
        
        mock_connection.close.assert_called_once()
        mock_engine.dispose.assert_called_once()
        importer.logger.info.assert_called_with("🔌 Database connections closed")

    @pytest.mark.unit
    def test_close_connections_with_none_values(self, importer):
        """Test closing connections when they are None."""
        importer.connection = None
        importer.engine = None
        
        # Should not raise any exceptions
        importer.close_connections()
        
        importer.logger.info.assert_called_with("🔌 Database connections closed")


class TestPostgreSQLDataImporterIntegration:
    """Integration tests for PostgreSQLDataImporter."""
    
    @pytest.mark.integration
    def test_full_pipeline_with_clean_data(self, sample_clean_data):
        """Test complete data import pipeline with clean data."""
        with patch('import_csv_to_postgres.logging.basicConfig'):
            with patch('import_csv_to_postgres.logging.getLogger'):
                importer = PostgreSQLDataImporter()
        
        # Mock all external dependencies
        with patch.object(importer, 'connect_database', return_value=True):
            with patch.object(importer, 'import_to_database', return_value=True):
                with patch.object(importer, 'update_aggregates', return_value=True):
                    with patch.object(importer, 'generate_import_report', return_value="Report"):
                        
                        # Test the pipeline
                        issues = importer.validate_csv_structure(sample_clean_data)
                        assert issues == []
                        
                        cleaned_data = importer.clean_data(sample_clean_data)
                        assert len(cleaned_data) > 0
                        
                        prepared_data = importer.prepare_for_postgres(cleaned_data)
                        assert 'order_id' in prepared_data.columns
                        
                        import_success = importer.import_to_database(prepared_data)
                        assert import_success is True

    @pytest.mark.integration
    def test_full_pipeline_with_dirty_data(self, sample_dirty_data):
        """Test complete data import pipeline with dirty data."""
        with patch('import_csv_to_postgres.logging.basicConfig'):
            with patch('import_csv_to_postgres.logging.getLogger'):
                importer = PostgreSQLDataImporter()
        
        # This should raise an exception due to data quality issues
        with pytest.raises(ValueError):
            importer.validate_csv_structure(sample_dirty_data)

    @pytest.mark.integration
    def test_pipeline_with_data_cleaning_recovery(self, sample_dirty_data):
        """Test pipeline recovery through data cleaning after validation issues."""
        with patch('import_csv_to_postgres.logging.basicConfig'):
            with patch('import_csv_to_postgres.logging.getLogger'):
                importer = PostgreSQLDataImporter()
        
        # Skip validation and go straight to cleaning
        cleaned_data = importer.clean_data(sample_dirty_data)
        
        # After cleaning, data should be valid
        assert len(cleaned_data) > 0
        assert not cleaned_data.isnull().any().any()
        
        # Should be able to prepare for PostgreSQL
        prepared_data = importer.prepare_for_postgres(cleaned_data)
        assert len(prepared_data) > 0
        assert 'order_id' in prepared_data.columns

    @pytest.mark.integration
    @patch('import_csv_to_postgres.pd.read_csv')
    @patch('import_csv_to_postgres.Path')
    def test_main_function_success(self, mock_path, mock_read_csv, sample_clean_data):
        """Test main function with successful execution."""
        
        # Setup mocks
        mock_data_file = Mock()
        mock_data_file.exists.return_value = True
        mock_path.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value = mock_data_file
        mock_read_csv.return_value = sample_clean_data
        
        with patch('import_csv_to_postgres.PostgreSQLDataImporter') as mock_importer_class:
            mock_importer = Mock()
            mock_importer_class.return_value = mock_importer
            mock_importer.connect_database.return_value = True
            mock_importer.validate_csv_structure.return_value = []
            mock_importer.clean_data.return_value = sample_clean_data
            mock_importer.prepare_for_postgres.return_value = sample_clean_data
            mock_importer.import_to_database.return_value = True
            mock_importer.update_aggregates.return_value = True
            mock_importer.generate_import_report.return_value = "Success report"
            
            result = main()
            
            assert result is True

    @pytest.mark.integration
    @patch('import_csv_to_postgres.Path')
    def test_main_function_missing_file(self, mock_path):
        """Test main function with missing data file."""
        
        mock_data_file = Mock()
        mock_data_file.exists.return_value = False
        mock_path.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value = mock_data_file
        
        result = main()
        
        assert result is False

    @pytest.mark.integration
    def test_main_function_database_connection_failure(self):
        """Test main function with database connection failure."""
        
        with patch('import_csv_to_postgres.PostgreSQLDataImporter') as mock_importer_class:
            mock_importer = Mock()
            mock_importer_class.return_value = mock_importer
            mock_importer.connect_database.return_value = False
            
            result = main()
            
            assert result is False


class TestPostgreSQLDataImporterEdgeCases:
    """Edge case tests for PostgreSQLDataImporter."""
    
    @pytest.mark.unit
    def test_empty_dataframe_handling(self, importer):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        
        # Should handle empty DataFrame gracefully
        with pytest.raises(ValueError):
            importer.validate_csv_structure(empty_df)

    @pytest.mark.unit
    def test_single_row_dataframe(self, importer):
        """Test handling of single row DataFrame."""
        single_row_df = pd.DataFrame({
            'OrderID': ['ORD_001'],
            'Product': ['Laptop'],
            'Category': ['Electronics'],
            'Quantity': [1],
            'Price': [999.99],
            'OrderDate': ['2024-01-15'],
            'CustomerID': [1001],
            'Country': ['USA']
        })
        
        issues = importer.validate_csv_structure(single_row_df)
        assert issues == []
        
        cleaned = importer.clean_data(single_row_df)
        assert len(cleaned) == 1

    @pytest.mark.unit
    def test_unicode_data_handling(self, importer):
        """Test handling of Unicode characters in data."""
        unicode_df = pd.DataFrame({
            'OrderID': ['ORD_001'],
            'Product': ['Laptop Pro™'],
            'Category': ['Électroniques'],
            'Quantity': [1],
            'Price': [999.99],
            'OrderDate': ['2024-01-15'],
            'CustomerID': [1001],
            'Country': ['España']
        })
        
        issues = importer.validate_csv_structure(unicode_df)
        assert issues == []
        
        cleaned = importer.clean_data(unicode_df)
        assert len(cleaned) == 1
        assert 'Laptop Pro™' in cleaned['Product'].values

    @pytest.mark.unit
    def test_large_numbers_handling(self, importer):
        """Test handling of very large numbers."""
        large_numbers_df = pd.DataFrame({
            'OrderID': ['ORD_001'],
            'Product': ['Expensive Item'],
            'Category': ['Luxury'],
            'Quantity': [1],
            'Price': [999999.99],  # Very large price
            'OrderDate': ['2024-01-15'],
            'CustomerID': [999999999],  # Very large customer ID
            'Country': ['USA']
        })
        
        issues = importer.validate_csv_structure(large_numbers_df)
        assert issues == []
        
        cleaned = importer.clean_data(large_numbers_df)
        assert len(cleaned) == 1

    @pytest.mark.unit
    def test_date_edge_cases(self, importer):
        """Test handling of various date formats."""
        date_df = pd.DataFrame({
            'OrderID': ['ORD_001', 'ORD_002', 'ORD_003'],
            'Product': ['Item1', 'Item2', 'Item3'],
            'Category': ['Cat1', 'Cat2', 'Cat3'],
            'Quantity': [1, 1, 1],
            'Price': [10.00, 20.00, 30.00],
            'OrderDate': ['2024-01-15', '2024/01/16', '01-17-2024'],  # Different formats
            'CustomerID': [1001, 1002, 1003],
            'Country': ['USA', 'USA', 'USA']
        })
        
        cleaned = importer.clean_data(date_df)
        
        # Should handle different date formats
        assert len(cleaned) >= 1  # At least some dates should be parseable

    @pytest.mark.unit
    def test_memory_efficient_processing(self, importer):
        """Test memory efficiency with large datasets."""
        # Create a moderately large dataset
        large_df = pd.DataFrame({
            'OrderID': [f'ORD_{i:06d}' for i in range(10000)],
            'Product': ['Product'] * 10000,
            'Category': ['Electronics'] * 10000,
            'Quantity': [1] * 10000,
            'Price': [99.99] * 10000,
            'OrderDate': ['2024-01-15'] * 10000,
            'CustomerID': list(range(1001, 11001)),
            'Country': ['USA'] * 10000
        })
        
        start_time = time.time()
        
        # Should process without memory issues
        cleaned = importer.clean_data(large_df)
        prepared = importer.prepare_for_postgres(cleaned)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert len(prepared) == 10000
        assert processing_time < 10  # Should complete within 10 seconds

    @pytest.mark.unit
    def test_concurrent_access_safety(self, importer):
        """Test thread safety considerations."""
        # This is a basic test - in production you'd need more sophisticated concurrent testing
        test_df = pd.DataFrame({
            'OrderID': ['ORD_001'],
            'Product': ['Test Product'],
            'Category': ['Test'],
            'Quantity': [1],
            'Price': [10.00],
            'OrderDate': ['2024-01-15'],
            'CustomerID': [1001],
            'Country': ['USA']
        })
        
        # Multiple operations should not interfere with each other
        result1 = importer.clean_data(test_df)
        result2 = importer.clean_data(test_df)
        
        assert len(result1) == len(result2)
        pd.testing.assert_frame_equal(result1, result2)


class TestPostgreSQLDataImporterPerformance:
    """Performance tests for PostgreSQLDataImporter."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_cleaning_performance(self, importer):
        """Test data cleaning performance with various dataset sizes."""
        sizes = [100, 1000, 5000]
        
        for size in sizes:
            # Create test dataset
            test_df = pd.DataFrame({
                'OrderID': [f'ORD_{i:06d}' for i in range(size)],
                'Product': ['Product'] * size,
                'Category': ['Electronics'] * size,
                'Quantity': [1] * size,
                'Price': [99.99] * size,
                'OrderDate': ['2024-01-15'] * size,
                'CustomerID': list(range(1001, 1001 + size)),
                'Country': ['USA'] * size
            })
            
            start_time = time.time()
            
            cleaned = importer.clean_data(test_df)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Performance assertions
            assert len(cleaned) == size
            assert processing_time < (size / 1000 + 1)  # Linear scaling expectation

    @pytest.mark.performance
    def test_validation_performance(self, importer):
        """Test validation performance."""
        # Create dataset with known issues for validation
        size = 1000
        test_df = pd.DataFrame({
            'OrderID': [f'ORD_{i:06d}' for i in range(size)],
            'Product': ['Product'] * size,
            'Category': ['Electronics'] * size,
            'Quantity': [1] * size,
            'Price': [99.99] * size,
            'OrderDate': ['2024-01-15'] * size,
            'CustomerID': list(range(1001, 1001 + size)),
            'Country': ['USA'] * size
        })
        
        start_time = time.time()
        
        issues = importer.validate_csv_structure(test_df)
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        assert validation_time < 5  # Should validate quickly
        assert issues == []  # Clean data should have no issues


if __name__ == "__main__":
    pytest.main([__file__, "-v"])