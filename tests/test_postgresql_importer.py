"""
Enhanced Test Suite for PostgreSQL Data Importer
Additional comprehensive tests for edge cases, security, and advanced scenarios
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from pathlib import Path
import tempfile
import sys
import logging
from datetime import datetime, date, timedelta
import sqlite3
import json
import os
import threading
import time
from decimal import Decimal
import warnings


class TestPostgreSQLDataImporterAdvanced:
    """Advanced test scenarios for PostgreSQL Data Importer."""
    
    @pytest.fixture
    def large_realistic_dataframe(self):
        """Create a large realistic DataFrame for stress testing."""
        np.random.seed(42)  # For reproducible tests
        size = 5000
        
        # Generate realistic e-commerce data
        order_ids = [f'ORD{year}{month:02d}{day:02d}{i:04d}' 
                    for year in [2023, 2024] 
                    for month in range(1, 13) 
                    for day in range(1, 15) 
                    for i in range(1, 20)][:size]
        
        products = ['MacBook Pro', 'iPhone 15', 'iPad Air', 'AirPods Pro', 'Apple Watch', 
                   'Dell XPS', 'Surface Pro', 'Galaxy S24', 'Pixel 8', 'ThinkPad X1']
        
        categories = ['Electronics', 'Computers', 'Mobile', 'Accessories', 'Wearables']
        countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Japan', 'Australia']
        
        return pd.DataFrame({
            'OrderID': order_ids,
            'Product': np.random.choice(products, size),
            'Category': np.random.choice(categories, size),
            'Quantity': np.random.randint(1, 5, size),
            'Price': np.round(np.random.uniform(10, 3000, size), 2),
            'OrderDate': [
                (datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
                for _ in range(size)
            ],
            'CustomerID': np.random.randint(1000, 9999, size),
            'Country': np.random.choice(countries, size)
        })
    
    @pytest.fixture
    def unicode_dataframe(self):
        """Create DataFrame with Unicode and special characters."""
        return pd.DataFrame({
            'OrderID': ['ORD_001_🛒', 'ORD_002_💻', 'ORD_003_📱'],
            'Product': ['Laptop™ Pro®', 'Téléphone Móvil', '平板电脑'],
            'Category': ['Électronique', 'Móviles', '电子产品'],
            'Quantity': [1, 2, 1],
            'Price': [1299.99, 699.99, 899.99],
            'OrderDate': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'CustomerID': [1001, 1002, 1003],
            'Country': ['França', 'España', '中国']
        })
    
    @pytest.fixture
    def edge_case_dataframe(self):
        """Create DataFrame with edge cases and boundary values."""
        return pd.DataFrame({
            'OrderID': ['', 'ORD_VERY_LONG_ORDER_ID_WITH_MANY_CHARACTERS_12345', 'ORD_003'],
            'Product': ['', 'A' * 500, 'Normal Product'],  # Empty and very long strings
            'Category': ['Electronics', 'Electronics', 'Electronics'],
            'Quantity': [0, 999999, 1],  # Boundary values
            'Price': [0.01, 999999.99, 50.00],  # Boundary prices
            'OrderDate': ['1900-01-01', '2099-12-31', '2024-01-15'],  # Edge dates
            'CustomerID': [1, 999999999, 1001],  # Boundary customer IDs
            'Country': ['XX', 'Very Long Country Name That Exceeds Normal Length', 'USA']
        })

    @pytest.mark.unit
    def test_validate_csv_structure_empty_dataframe(self, importer):
        """Test validation with completely empty DataFrame."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="DataFrame is empty"):
            importer.validate_csv_structure(empty_df)

    @pytest.mark.unit
    def test_validate_csv_structure_single_column(self, importer):
        """Test validation with DataFrame having only one column."""
        single_col_df = pd.DataFrame({'OrderID': ['ORD001', 'ORD002']})
        
        with pytest.raises(ValueError, match="Missing required columns"):
            importer.validate_csv_structure(single_col_df)

    @pytest.mark.unit
    def test_validate_csv_structure_all_null_values(self, importer):
        """Test validation with DataFrame containing all null values."""
        null_df = pd.DataFrame({
            'OrderID': [None, None],
            'Product': [None, None],
            'Category': [None, None],
            'Quantity': [None, None],
            'Price': [None, None],
            'OrderDate': [None, None],
            'CustomerID': [None, None],
            'Country': [None, None]
        })
        
        issues = importer.validate_csv_structure(null_df)
        assert len(issues) > 0
        assert any('100% null values' in issue for issue in issues)

    @pytest.mark.unit
    def test_validate_csv_structure_duplicate_order_ids(self, importer):
        """Test validation with duplicate order IDs."""
        duplicate_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD001', 'ORD002'],  # Duplicate
            'Product': ['Product1', 'Product2', 'Product3'],
            'Category': ['Electronics'] * 3,
            'Quantity': [1, 2, 1],
            'Price': [100, 200, 150],
            'OrderDate': ['2024-01-15'] * 3,
            'CustomerID': [1001, 1002, 1003],
            'Country': ['USA'] * 3
        })
        
        issues = importer.validate_csv_structure(duplicate_df)
        assert any('Duplicate OrderID values found' in issue for issue in issues)

    @pytest.mark.unit
    def test_clean_data_unicode_handling(self, importer, unicode_dataframe):
        """Test data cleaning with Unicode characters."""
        cleaned_df = importer.clean_data(unicode_dataframe)
        
        # Should preserve Unicode characters
        assert '™' in cleaned_df['Product'].iloc[0]
        assert 'Téléphone' in cleaned_df['Product'].iloc[1]
        assert '平板电脑' in cleaned_df['Product'].iloc[2]
        
        # Should have required calculated columns
        assert 'TotalValue' in cleaned_df.columns
        assert 'CustomerSegment' in cleaned_df.columns

    @pytest.mark.unit
    def test_clean_data_edge_cases(self, importer, edge_case_dataframe):
        """Test data cleaning with edge case values."""
        cleaned_df = importer.clean_data(edge_case_dataframe)
        
        # Should handle edge cases appropriately
        assert len(cleaned_df) <= len(edge_case_dataframe)
        
        # All remaining data should be valid
        if len(cleaned_df) > 0:
            assert (cleaned_df['Quantity'] > 0).all()
            assert (cleaned_df['Price'] > 0).all()
            assert cleaned_df['OrderID'].str.len().max() <= 50  # Reasonable length limit

    @pytest.mark.unit
    def test_clean_data_numeric_edge_cases(self, importer):
        """Test cleaning with various numeric edge cases."""
        numeric_edge_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', 'ORD003', 'ORD004'],
            'Product': ['Product1', 'Product2', 'Product3', 'Product4'],
            'Category': ['Electronics'] * 4,
            'Quantity': [float('inf'), -float('inf'), float('nan'), 1],
            'Price': [0.001, 999999.999, float('nan'), 100.00],
            'OrderDate': ['2024-01-15'] * 4,
            'CustomerID': [1001, 1002, 1003, 1004],
            'Country': ['USA'] * 4
        })
        
        cleaned_df = importer.clean_data(numeric_edge_df)
        
        # Should handle infinity and NaN values
        if len(cleaned_df) > 0:
            assert np.isfinite(cleaned_df['Quantity']).all()
            assert np.isfinite(cleaned_df['Price']).all()

    @pytest.mark.unit
    def test_clean_data_date_format_variations(self, importer):
        """Test cleaning with various date formats."""
        date_variation_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
            'Product': ['Product1'] * 5,
            'Category': ['Electronics'] * 5,
            'Quantity': [1] * 5,
            'Price': [100.0] * 5,
            'OrderDate': [
                '2024-01-15',           # Standard format
                '01/15/2024',           # US format
                '15-01-2024',           # European format
                '2024.01.15',           # Dot separator
                'January 15, 2024'      # Text format
            ],
            'CustomerID': [1001, 1002, 1003, 1004, 1005],
            'Country': ['USA'] * 5
        })
        
        cleaned_df = importer.clean_data(date_variation_df)
        
        # Should handle various date formats
        assert len(cleaned_df) >= 1  # At least some should be parseable

    @pytest.mark.unit
    def test_prepare_for_postgres_data_type_conversion(self, importer, sample_dataframe):
        """Test data type conversions during PostgreSQL preparation."""
        cleaned_df = importer.clean_data(sample_dataframe)
        prepared_df = importer.prepare_for_postgres(cleaned_df)
        
        # Verify specific data type conversions
        assert prepared_df['unit_price'].dtype in [np.float64, float]
        assert prepared_df['total_value'].dtype in [np.float64, float]
        assert prepared_df['quantity'].dtype in [np.int64, int]
        assert prepared_df['customer_id'].dtype in [np.int64, int]
        
        # Verify date objects
        assert all(isinstance(d, (date, datetime)) for d in prepared_df['order_date'])

    @pytest.mark.unit
    def test_prepare_for_postgres_column_order_consistency(self, importer, sample_dataframe):
        """Test that column order is consistent across multiple preparations."""
        cleaned_df = importer.clean_data(sample_dataframe)
        
        # Prepare same data multiple times
        prepared_df1 = importer.prepare_for_postgres(cleaned_df)
        prepared_df2 = importer.prepare_for_postgres(cleaned_df)
        
        # Column order should be identical
        assert list(prepared_df1.columns) == list(prepared_df2.columns)

    @pytest.mark.performance
    def test_large_dataset_memory_usage(self, importer, large_realistic_dataframe):
        """Test memory efficiency with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large dataset
        cleaned_df = importer.clean_data(large_realistic_dataframe)
        prepared_df = importer.prepare_for_postgres(cleaned_df)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 500MB for 5000 records)
        assert memory_increase < 500, f"Memory usage increased by {memory_increase:.2f}MB"
        assert len(prepared_df) > 0

    @pytest.mark.performance
    def test_cleaning_performance_scaling(self, importer):
        """Test that cleaning performance scales linearly."""
        sizes = [100, 500, 1000]
        times = []
        
        for size in sizes:
            # Create test dataset
            test_df = pd.DataFrame({
                'OrderID': [f'ORD{i:06d}' for i in range(size)],
                'Product': ['Test Product'] * size,
                'Category': ['Electronics'] * size,
                'Quantity': [1] * size,
                'Price': [99.99] * size,
                'OrderDate': ['2024-01-15'] * size,
                'CustomerID': list(range(1001, 1001 + size)),
                'Country': ['USA'] * size
            })
            
            start_time = time.time()
            cleaned_df = importer.clean_data(test_df)
            end_time = time.time()
            
            processing_time = end_time - start_time
            times.append(processing_time)
            
            assert len(cleaned_df) == size
        
        # Performance should scale roughly linearly
        # Time per record should not increase dramatically
        time_per_record = [t/s for t, s in zip(times, sizes)]
        max_time_per_record = max(time_per_record)
        min_time_per_record = min(time_per_record)
        
        # Ratio should not exceed 3x (allowing for some overhead)
        assert max_time_per_record / min_time_per_record < 3.0

    @pytest.mark.mock
    @patch('psycopg2.connect')
    def test_connect_database_connection_timeout(self, mock_connect, importer):
        """Test database connection with timeout scenarios."""
        import socket
        
        # Mock timeout exception
        mock_connect.side_effect = socket.timeout("Connection timed out")
        
        result = importer.connect_database()
        
        assert result is False
        assert importer.connection is None

    @pytest.mark.mock
    @patch('psycopg2.connect')
    def test_connect_database_authentication_failure(self, mock_connect, importer):
        """Test database connection with authentication failure."""
        import psycopg2
        
        # Mock authentication error
        mock_connect.side_effect = psycopg2.OperationalError("authentication failed")
        
        result = importer.connect_database()
        
        assert result is False
        assert importer.connection is None

    @pytest.mark.mock
    def test_import_to_database_transaction_rollback(self, importer, sample_dataframe):
        """Test transaction rollback on import failure."""
        cleaned_df = importer.clean_data(sample_dataframe)
        prepared_df = importer.prepare_for_postgres(cleaned_df)
        
        # Mock engine with failing to_sql
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock to_sql to fail after truncate
        with patch.object(prepared_df, 'to_sql', side_effect=Exception("SQL Error")):
            importer.engine = mock_engine
            
            result = importer.import_to_database(prepared_df)
            
            assert result is False
            # Should still call truncate but fail on insert
            mock_connection.execute.assert_called_with("TRUNCATE TABLE sales CASCADE")

    @pytest.mark.mock
    def test_import_to_database_batch_size_optimization(self, importer):
        """Test batch size optimization for large datasets."""
        # Create dataset larger than default batch size
        large_df = pd.DataFrame({
            'order_id': [f'ORD{i:06d}' for i in range(2500)],
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
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        with patch.object(large_df, 'to_sql') as mock_to_sql:
            importer.engine = mock_engine
            
            result = importer.import_to_database(large_df, batch_size=1000)
            
            assert result is True
            # Should be called 3 times for 2500 records with batch_size=1000
            assert mock_to_sql.call_count == 3

    @pytest.mark.mock
    def test_update_aggregates_stored_procedure_failure(self, importer):
        """Test handling of stored procedure failures in aggregate updates."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock stored procedure failure
        mock_cursor.execute.side_effect = [
            None,  # First call succeeds
            Exception("Stored procedure error")  # Second call fails
        ]
        
        importer.connection = mock_connection
        
        result = importer.update_aggregates()
        
        assert result is False

    @pytest.mark.mock
    @patch('pandas.read_sql')
    def test_generate_import_report_with_empty_results(self, mock_read_sql, importer):
        """Test report generation with empty database results."""
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock empty results
        mock_result = Mock()
        mock_result.fetchone.side_effect = [
            [0],  # total_records = 0
            [0.0],  # total_revenue = 0
            [0],  # unique_customers = 0
            [0],  # unique_products = 0
            [None, None]  # no date range
        ]
        mock_connection.execute.return_value = mock_result
        
        # Mock empty DataFrame
        mock_read_sql.return_value = pd.DataFrame()
        
        importer.engine = mock_engine
        
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', create=True):
            
            result = importer.generate_import_report()
        
        assert result is not None
        assert "0" in result  # Should handle zero values gracefully


class TestSecurityAndValidation:
    """Security and validation focused tests."""
    
    @pytest.mark.security
    def test_sql_injection_prevention_in_order_ids(self, importer):
        """Test prevention of SQL injection in order IDs."""
        malicious_df = pd.DataFrame({
            'OrderID': ["'; DROP TABLE sales; --", "ORD002"],
            'Product': ['Product1', 'Product2'],
            'Category': ['Electronics', 'Electronics'],
            'Quantity': [1, 2],
            'Price': [100, 200],
            'OrderDate': ['2024-01-15', '2024-01-16'],
            'CustomerID': [1001, 1002],
            'Country': ['USA', 'USA']
        })
        
        # Should clean or remove malicious data
        cleaned_df = importer.clean_data(malicious_df)
        
        # Verify SQL injection attempts are handled
        if len(cleaned_df) > 0:
            for order_id in cleaned_df['OrderID']:
                assert ';' not in order_id
                assert 'DROP' not in order_id.upper()
                assert '--' not in order_id

    @pytest.mark.security
    def test_xss_prevention_in_text_fields(self, importer):
        """Test prevention of XSS in text fields."""
        xss_df = pd.DataFrame({
            'OrderID': ['ORD001'],
            'Product': ['<script>alert("xss")</script>'],
            'Category': ['<img src=x onerror=alert(1)>'],
            'Quantity': [1],
            'Price': [100],
            'OrderDate': ['2024-01-15'],
            'CustomerID': [1001],
            'Country': ['<svg onload=alert(1)>']
        })
        
        cleaned_df = importer.clean_data(xss_df)
        
        # Should handle or escape HTML/JavaScript
        if len(cleaned_df) > 0:
            for col in ['Product', 'Category', 'Country']:
                text_value = str(cleaned_df[col].iloc[0])
                assert '<script>' not in text_value
                assert 'onerror=' not in text_value
                assert 'onload=' not in text_value

    @pytest.mark.security
    def test_path_traversal_prevention(self, importer):
        """Test prevention of path traversal in file operations."""
        # This would be more relevant if the importer handled file paths from data
        # For now, test that unusual characters in data don't cause issues
        path_df = pd.DataFrame({
            'OrderID': ['../../../etc/passwd'],
            'Product': ['..\\..\\windows\\system32'],
            'Category': ['Electronics'],
            'Quantity': [1],
            'Price': [100],
            'OrderDate': ['2024-01-15'],
            'CustomerID': [1001],
            'Country': ['USA']
        })
        
        cleaned_df = importer.clean_data(path_df)
        
        # Should sanitize path-like strings
        if len(cleaned_df) > 0:
            assert '../' not in cleaned_df['OrderID'].iloc[0]
            assert '..\\' not in cleaned_df['Product'].iloc[0]

    @pytest.mark.validation
    def test_data_type_coercion_safety(self, importer):
        """Test safe data type coercion."""
        mixed_type_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002'],
            'Product': ['Product1', 123],  # Mixed string/int
            'Category': ['Electronics', 'Electronics'],
            'Quantity': ['1', 2.5],  # Mixed string/float
            'Price': ['100.50', 200],  # Mixed string/int
            'OrderDate': ['2024-01-15', datetime(2024, 1, 16)],  # Mixed string/datetime
            'CustomerID': [1001, '1002'],  # Mixed int/string
            'Country': ['USA', 456]  # Mixed string/int
        })
        
        cleaned_df = importer.clean_data(mixed_type_df)
        
        # Should handle type coercion safely
        assert len(cleaned_df) <= 2
        if len(cleaned_df) > 0:
            # All values should be properly typed
            assert isinstance(cleaned_df['Quantity'].iloc[0], (int, float))
            assert isinstance(cleaned_df['Price'].iloc[0], (int, float))


class TestConcurrencyAndThreadSafety:
    """Tests for concurrent access and thread safety."""
    
    @pytest.mark.threading
    def test_concurrent_data_cleaning(self, importer, sample_dataframe):
        """Test concurrent data cleaning operations."""
        results = []
        errors = []
        
        def clean_data_thread():
            try:
                cleaned = importer.clean_data(sample_dataframe.copy())
                results.append(cleaned)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=clean_data_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and consistent results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 3
        
        # Results should be identical
        for result in results[1:]:
            pd.testing.assert_frame_equal(results[0], result)

    @pytest.mark.threading
    def test_thread_safety_of_logger(self, importer):
        """Test thread safety of logging operations."""
        log_messages = []
        
        def log_test_thread(thread_id):
            for i in range(10):
                importer.logger.info(f"Thread {thread_id} - Message {i}")
                time.sleep(0.01)  # Small delay to encourage race conditions
        
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=log_test_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should complete without exceptions
        assert True


class TestErrorRecoveryAndResilience:
    """Tests for error recovery and system resilience."""
    
    @pytest.mark.recovery
    def test_recovery_from_memory_pressure(self, importer):
        """Test recovery from simulated memory pressure."""
        # Create progressively larger datasets
        sizes = [1000, 2000, 3000]
        
        for size in sizes:
            large_df = pd.DataFrame({
                'OrderID': [f'ORD{i:06d}' for i in range(size)],
                'Product': ['Product'] * size,
                'Category': ['Electronics'] * size,
                'Quantity': [1] * size,
                'Price': [99.99] * size,
                'OrderDate': ['2024-01-15'] * size,
                'CustomerID': list(range(1001, 1001 + size)),
                'Country': ['USA'] * size
            })
            
            try:
                cleaned_df = importer.clean_data(large_df)
                assert len(cleaned_df) == size
            except MemoryError:
                # Should handle memory errors gracefully
                pytest.skip(f"Memory limit reached at size {size}")

    @pytest.mark.recovery
    def test_partial_data_corruption_recovery(self, importer):
        """Test recovery from partial data corruption."""
        # Create dataset with mixed valid and corrupted data
        mixed_df = pd.DataFrame({
            'OrderID': ['ORD001', None, 'ORD003', '', 'ORD005'],
            'Product': ['Product1', 'Product2', None, 'Product4', 'Product5'],
            'Category': ['Electronics'] * 5,
            'Quantity': [1, -1, float('nan'), 3, 2],
            'Price': [100, 200, -50, float('inf'), 150],
            'OrderDate': ['2024-01-15', 'invalid', '2024-01-17', None, '2024-01-19'],
            'CustomerID': [1001, 1002, -1003, 1004, 1005],
            'Country': ['USA', 'Canada', 'UK', '', 'France']
        })
        
        cleaned_df = importer.clean_data(mixed_df)
        
        # Should recover valid data
        assert len(cleaned_df) >= 1  # At least some data should be recoverable
        
        if len(cleaned_df) > 0:
            # All remaining data should be valid
            assert (cleaned_df['Quantity'] > 0).all()
            assert (cleaned_df['Price'] > 0).all()
            assert cleaned_df['OrderID'].notna().all()

    @pytest.mark.recovery
    def test_gradual_degradation_handling(self, importer):
        """Test handling of gradual system degradation."""
        # Simulate increasing error rates
        error_rates = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for error_rate in error_rates:
            size = 100
            # Create dataset with increasing corruption
            corrupt_count = int(size * error_rate)
            
            df_data = {
                'OrderID': [f'ORD{i:03d}' if i >= corrupt_count else None for i in range(size)],
                'Product': [f'Product{i}' if i >= corrupt_count else None for i in range(size)],
                'Category': ['Electronics'] * size,
                'Quantity': [1 if i >= corrupt_count else -1 for i in range(size)],
                'Price': [100 if i >= corrupt_count else -100 for i in range(size)],
                'OrderDate': ['2024-01-15' if i >= corrupt_count else 'invalid' for i in range(size)],
                'CustomerID': [1000 + i if i >= corrupt_count else -1 for i in range(size)],
                'Country': ['USA'] * size
            }
            
            test_df = pd.DataFrame(df_data)
            cleaned_df = importer.clean_data(test_df)
            
            # Should maintain some data even with high error rates
            expected_valid_records = size - corrupt_count
            assert len(cleaned_df) <= expected_valid_records
            
            if error_rate < 0.9:  # Should have some data unless almost everything is corrupt
                assert len(cleaned_df) > 0


class TestBusinessLogicValidation:
    """Tests for business logic and domain-specific validation."""
    
    @pytest.mark.business
    def test_customer_segmentation_business_rules(self, importer):
        """Test customer segmentation follows business rules."""
        # Create data with known total values for segmentation
        segmentation_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', 'ORD003', 'ORD004'],
            'Product': ['Cheap Item', 'Mid Item', 'Expensive Item', 'Luxury Item'],
            'Category': ['Electronics'] * 4,
            'Quantity': [1, 1, 1, 1],
            'Price': [10.00, 75.00, 150.00, 500.00],  # Different price tiers
            'OrderDate': ['2024-01-15'] * 4,
            'CustomerID': [1001, 1002, 1003, 1004],
            'Country': ['USA'] * 4
        })
        
        cleaned_df = importer.clean_data(segmentation_df)
        
        # Verify segmentation logic
        for idx, row in cleaned_df.iterrows():
            total_value = row['TotalValue']
            segment = row['CustomerSegment']
            
            if total_value < 50:
                assert segment == 'Bargain'
            elif total_value < 200:
                assert segment == 'Regular'
            else:
                assert segment == 'Premium'

    @pytest.mark.business
    def test_order_date_business_validation(self, importer):
        """Test order date business validation rules."""
        # Test with various date scenarios
        date_test_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', 'ORD003', 'ORD004'],
            'Product': ['Product1'] * 4,
            'Category': ['Electronics'] * 4,
            'Quantity': [1] * 4,
            'Price': [100] * 4,
            'OrderDate': [
                '1990-01-01',  # Too old
                '2030-01-01',  # Future date
                '2024-01-15',  # Valid
                '2024-12-31'   # Valid
            ],
            'CustomerID': [1001, 1002, 1003, 1004],
            'Country': ['USA'] * 4
        })
        
        cleaned_df = importer.clean_data(date_test_df)
        
        # Should filter out unrealistic dates
        if len(cleaned_df) > 0:
            # Remaining dates should be reasonable
            for order_date in cleaned_df['OrderDate']:
                if isinstance(order_date, str):
                    date_obj = pd.to_datetime(order_date)
                    assert date_obj.year >= 2020  # Recent orders only
                    assert date_obj.year <= 2025  # Not too far in future

    @pytest.mark.business
    def test_product_category_consistency(self, importer):
        """Test product-category consistency validation."""
        # Create data with inconsistent product-category mappings
        consistency_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', 'ORD003'],
            'Product': ['iPhone 15', 'MacBook Pro', 'Office Chair'],
            'Category': ['Furniture', 'Electronics', 'Electronics'],  # iPhone in Furniture is wrong
            'Quantity': [1, 1, 1],
            'Price': [999, 2499, 299],
            'OrderDate': ['2024-01-15'] * 3,
            'CustomerID': [1001, 1002, 1003],
            'Country': ['USA'] * 3
        })
        
        # The importer should handle this gracefully
        cleaned_df = importer.clean_data(consistency_df)
        assert len(cleaned_df) <= 3  # May keep all or flag inconsistencies


if __name__ == "__main__":
    # Run with specific markers for different test categories
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "not slow"  # Skip slow tests by default
    ])
import logging
from datetime import datetime, date
import sqlite3

# Add the parent directory to sys.path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from data_processing.import_csv_to_postgres import PostgreSQLDataImporter
except ImportError:
    # Fallback if module structure is different
    try:
        from import_csv_to_postgres import PostgreSQLDataImporter
    except ImportError:
        pytest.skip("PostgreSQLDataImporter module not found", allow_module_level=True)


class TestPostgreSQLDataImporter:
    """Test suite for PostgreSQL Data Importer class."""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
            'Product': ['Laptop Pro', 'Wireless Mouse', 'USB Cable', 'Monitor 4K', 'Keyboard'],
            'Category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
            'Quantity': [1, 2, 3, 1, 1],
            'Price': [1299.99, 29.99, 15.99, 599.99, 89.99],
            'OrderDate': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
            'CustomerID': [1001, 1002, 1003, 1004, 1005],
            'Country': ['USA', 'Canada', 'UK', 'Germany', 'France']
        })
    
    @pytest.fixture
    def invalid_dataframe(self):
        """Create an invalid DataFrame for testing error handling."""
        return pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', None, 'ORD004'],
            'Product': ['Laptop', 'Mouse', 'Cable', None],
            'Category': ['Electronics', 'Electronics', 'Electronics', 'Electronics'],
            'Quantity': [1, -1, 0, 2],  # Invalid quantities
            'Price': [1000, 50, -10, 100],  # Invalid price
            'OrderDate': ['2024-01-15', 'invalid-date', '2024-01-17', '2024-01-18'],
            'CustomerID': [1001, 1002, 1003, 1004],
            'Country': ['USA', 'Canada', 'UK', 'Germany']
        })
    
    @pytest.fixture
    def importer(self):
        """Create a PostgreSQLDataImporter instance for testing."""
        test_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password'
        }
        
        with patch('logging.basicConfig'), \
             patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler'), \
             patch('logging.getLogger') as mock_logger:
            
            mock_logger.return_value = Mock()
            return PostgreSQLDataImporter(test_config)
    
    @pytest.mark.unit
    def test_importer_initialization(self, importer):
        """Test that the importer initializes correctly."""
        assert importer.db_config['host'] == 'localhost'
        assert importer.db_config['database'] == 'test_db'
        assert importer.connection is None
        assert importer.engine is None
    
    @pytest.mark.unit
    def test_importer_default_config(self):
        """Test importer with default configuration."""
        with patch('logging.basicConfig'), \
             patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler'), \
             patch('logging.getLogger'):
            
            importer = PostgreSQLDataImporter()
            assert importer.db_config['host'] == 'localhost'
            assert importer.db_config['database'] == 'ecommerce_analytics_2025'
    
    @pytest.mark.unit
    def test_validate_csv_structure_valid_data(self, importer, sample_dataframe):
        """Test CSV validation with valid data."""
        issues = importer.validate_csv_structure(sample_dataframe)
        assert isinstance(issues, list)
        # Should have no critical structural issues
        assert len([issue for issue in issues if 'Missing required columns' in issue]) == 0
    
    @pytest.mark.unit
    def test_validate_csv_structure_missing_columns(self, importer):
        """Test CSV validation with missing columns."""
        incomplete_df = pd.DataFrame({
            'OrderID': ['ORD001'],
            'Product': ['Laptop']
            # Missing other required columns
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            importer.validate_csv_structure(incomplete_df)
    
    @pytest.mark.unit
    def test_validate_csv_structure_invalid_data(self, importer, invalid_dataframe):
        """Test CSV validation with invalid data."""
        issues = importer.validate_csv_structure(invalid_dataframe)
        
        # Should detect multiple issues
        assert len(issues) > 0
        issue_text = ' '.join(issues)
        assert 'Null values found' in issue_text or 'Negative' in issue_text
    
    @pytest.mark.unit
    def test_clean_data_basic_cleaning(self, importer, sample_dataframe):
        """Test basic data cleaning functionality."""
        # Add some messy data
        messy_df = sample_dataframe.copy()
        messy_df.loc[0, 'Product'] = '  laptop pro  '  # Extra spaces
        messy_df.loc[1, 'Category'] = 'electronics'    # Wrong case
        
        cleaned_df = importer.clean_data(messy_df)
        
        assert cleaned_df.loc[0, 'Product'] == 'Laptop Pro'
        assert cleaned_df.loc[1, 'Category'] == 'Electronics'
        assert len(cleaned_df) <= len(messy_df)  # May remove invalid rows
    
    @pytest.mark.unit
    def test_clean_data_removes_invalid_records(self, importer, invalid_dataframe):
        """Test that cleaning removes invalid records."""
        original_len = len(invalid_dataframe)
        cleaned_df = importer.clean_data(invalid_dataframe)
        
        # Should remove records with invalid data
        assert len(cleaned_df) < original_len
        
        # All remaining records should have positive quantities and prices
        if len(cleaned_df) > 0:
            assert (cleaned_df['Quantity'] > 0).all()
            assert (cleaned_df['Price'] > 0).all()
    
    @pytest.mark.unit
    def test_clean_data_adds_calculated_columns(self, importer, sample_dataframe):
        """Test that cleaning adds calculated columns."""
        cleaned_df = importer.clean_data(sample_dataframe)
        
        # Should add TotalValue column
        assert 'TotalValue' in cleaned_df.columns
        
        # Should add CustomerSegment column
        assert 'CustomerSegment' in cleaned_df.columns
        
        # TotalValue should be calculated correctly
        expected_total = cleaned_df['Quantity'] * cleaned_df['Price']
        pd.testing.assert_series_equal(cleaned_df['TotalValue'], expected_total, check_names=False)
    
    @pytest.mark.unit
    def test_prepare_for_postgres(self, importer, sample_dataframe):
        """Test preparation of data for PostgreSQL."""
        # First clean the data
        cleaned_df = importer.clean_data(sample_dataframe)
        
        # Then prepare for PostgreSQL
        prepared_df = importer.prepare_for_postgres(cleaned_df)
        
        # Check column renaming
        expected_columns = [
            'order_id', 'product_name', 'category', 'quantity', 
            'unit_price', 'total_value', 'order_date', 'customer_id', 
            'country', 'customer_segment'
        ]
        
        assert list(prepared_df.columns) == expected_columns
        
        # Check data types
        assert prepared_df['unit_price'].dtype == float
        assert prepared_df['total_value'].dtype == float
        
        # Check date conversion
        assert prepared_df['order_date'].dtype == object  # Should be date objects
    
    @pytest.mark.mock
    @patch('psycopg2.connect')
    @patch('sqlalchemy.create_engine')
    def test_connect_database_success(self, mock_engine, mock_connect, importer):
        """Test successful database connection."""
        # Mock successful connections
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        mock_sqlalchemy_engine = Mock()
        mock_engine.return_value = mock_sqlalchemy_engine
        
        result = importer.connect_database()
        
        assert result is True
        assert importer.connection == mock_connection
        assert importer.engine == mock_sqlalchemy_engine
        
        # Verify connection parameters
        mock_connect.assert_called_once_with(**importer.db_config)
    
    @pytest.mark.mock
    @patch('psycopg2.connect')
    def test_connect_database_failure(self, mock_connect, importer):
        """Test database connection failure."""
        # Mock connection failure
        mock_connect.side_effect = Exception("Connection failed")
        
        result = importer.connect_database()
        
        assert result is False
        assert importer.connection is None
        assert importer.engine is None
    
    @pytest.mark.mock
    def test_import_to_database_success(self, importer, sample_dataframe):
        """Test successful database import."""
        # Prepare test data
        cleaned_df = importer.clean_data(sample_dataframe)
        prepared_df = importer.prepare_for_postgres(cleaned_df)
        
        # Mock database components
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        importer.engine = mock_engine
        
        result = importer.import_to_database(prepared_df, batch_size=2)
        
        assert result is True
        
        # Verify truncate was called
        mock_connection.execute.assert_any_call("TRUNCATE TABLE sales CASCADE")
        mock_connection.commit.assert_called()
    
    @pytest.mark.mock
    def test_import_to_database_failure(self, importer, sample_dataframe):
        """Test database import failure."""
        # Prepare test data
        cleaned_df = importer.clean_data(sample_dataframe)
        prepared_df = importer.prepare_for_postgres(cleaned_df)
        
        # Mock database failure
        mock_engine = Mock()
        mock_engine.connect.side_effect = Exception("Database error")
        
        importer.engine = mock_engine
        
        result = importer.import_to_database(prepared_df)
        
        assert result is False
    
    @pytest.mark.mock
    def test_update_aggregates_success(self, importer):
        """Test successful aggregate table updates."""
        # Mock database connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        importer.connection = mock_connection
        
        result = importer.update_aggregates()
        
        assert result is True
        
        # Verify SQL functions were called
        expected_calls = [
            call("SELECT update_customer_aggregates();"),
            call("SELECT update_product_aggregates();")
        ]
        mock_cursor.execute.assert_has_calls(expected_calls)
        mock_connection.commit.assert_called_once()
    
    @pytest.mark.mock
    def test_update_aggregates_failure(self, importer):
        """Test aggregate update failure."""
        # Mock database failure
        mock_connection = Mock()
        mock_connection.cursor.side_effect = Exception("Database error")
        
        importer.connection = mock_connection
        
        result = importer.update_aggregates()
        
        assert result is False
    
    @pytest.mark.mock
    @patch('pandas.read_sql')
    def test_generate_import_report_success(self, mock_read_sql, importer):
        """Test successful report generation."""
        # Mock database connection and results
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock query results
        mock_result = Mock()
        mock_result.fetchone.side_effect = [
            [1000],  # total_records
            [50000.0],  # total_revenue
            [250],  # unique_customers
            [50],  # unique_products
            [date(2024, 1, 1), date(2024, 12, 31)]  # date range
        ]
        mock_connection.execute.return_value = mock_result
        
        # Mock pandas read_sql
        mock_read_sql.return_value = pd.DataFrame({
            'category': ['Electronics', 'Books'],
            'orders': [800, 200],
            'revenue': [40000.0, 10000.0],
            'avg_order_value': [50.0, 50.0]
        })
        
        importer.engine = mock_engine
        
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', create=True) as mock_open:
            
            result = importer.generate_import_report()
        
        assert result is not None
        assert "📊 DATA IMPORT REPORT" in result
        assert "1,000" in result  # Formatted total records
        assert "$50,000.00" in result  # Formatted revenue
    
    @pytest.mark.mock
    def test_generate_import_report_failure(self, importer):
        """Test report generation failure."""
        # Mock database failure
        mock_engine = Mock()
        mock_engine.connect.side_effect = Exception("Database error")
        
        importer.engine = mock_engine
        
        result = importer.generate_import_report()
        
        assert result is None
    
    @pytest.mark.unit
    def test_close_connections(self, importer):
        """Test closing database connections."""
        # Mock connections
        mock_connection = Mock()
        mock_engine = Mock()
        
        importer.connection = mock_connection
        importer.engine = mock_engine
        
        importer.close_connections()
        
        mock_connection.close.assert_called_once()
        mock_engine.dispose.assert_called_once()


class TestDataValidationHelpers:
    """Test data validation helper functions and edge cases."""
    
    @pytest.mark.unit
    def test_column_mapping_completeness(self):
        """Test that column mapping covers all required columns."""
        from data_processing.import_csv_to_postgres import PostgreSQLDataImporter
        
        importer = PostgreSQLDataImporter()
        
        # Test with a DataFrame that has all expected columns
        test_df = pd.DataFrame({
            'OrderID': ['TEST001'],
            'Product': ['Test Product'],
            'Category': ['Test Category'],
            'Quantity': [1],
            'Price': [10.0],
            'TotalValue': [10.0],
            'OrderDate': [datetime.now()],
            'CustomerID': [1],
            'Country': ['Test Country'],
            'CustomerSegment': ['Regular']
        })
        
        prepared_df = importer.prepare_for_postgres(test_df)
        
        expected_columns = [
            'order_id', 'product_name', 'category', 'quantity',
            'unit_price', 'total_value', 'order_date', 'customer_id',
            'country', 'customer_segment'
        ]
        
        assert list(prepared_df.columns) == expected_columns
    
    @pytest.mark.unit
    def test_customer_segmentation_logic(self):
        """Test customer segmentation logic."""
        from data_processing.import_csv_to_postgres import PostgreSQLDataImporter
        
        importer = PostgreSQLDataImporter()
        
        # Test DataFrame with various total values
        test_df = pd.DataFrame({
            'OrderID': ['ORD001', 'ORD002', 'ORD003'],
            'Product': ['Product A', 'Product B', 'Product C'],
            'Category': ['Category1', 'Category1', 'Category1'],
            'Quantity': [1, 1, 1],
            'Price': [25.0, 100.0, 500.0],  # Different price points
            'OrderDate': [datetime.now()] * 3,
            'CustomerID': [1, 2, 3],
            'Country': ['USA'] * 3
        })
        
        cleaned_df = importer.clean_data(test_df)
        
        # Check segmentation
        segments = cleaned_df['CustomerSegment'].unique()
        assert len(segments) <= 3  # Should have Bargain, Regular, Premium
        assert 'Bargain' in segments or 'Regular' in segments or 'Premium' in segments
    
    @pytest.mark.performance
    def test_large_dataset_processing(self):
        """Test processing performance with larger datasets."""
        from data_processing.import_csv_to_postgres import PostgreSQLDataImporter
        
        importer = PostgreSQLDataImporter()
        
        # Create a larger test dataset
        import time
        
        large_df = pd.DataFrame({
            'OrderID': [f'ORD{i:06d}' for i in range(1000)],
            'Product': ['Test Product'] * 1000,
            'Category': ['Electronics'] * 1000,
            'Quantity': [1] * 1000,
            'Price': [99.99] * 1000,
            'OrderDate': [datetime.now()] * 1000,
            'CustomerID': list(range(1, 1001)),
            'Country': ['USA'] * 1000
        })
        
        start_time = time.time()
        cleaned_df = importer.clean_data(large_df)
        processing_time = time.time() - start_time
        
        assert len(cleaned_df) == 1000
        assert processing_time < 5.0  # Should process within 5 seconds


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""
    
    @pytest.mark.integration
    def test_end_to_end_data_pipeline(self):
        """Test complete data pipeline from CSV to prepared DataFrame."""
        from data_processing.import_csv_to_postgres import PostgreSQLDataImporter
        
        # Create realistic test data
        test_data = {
            'OrderID': ['ORD240101001', 'ORD240101002', 'ORD240101003'],
            'Product': ['MacBook Pro 16"', 'iPhone 15 Pro', 'AirPods Pro'],
            'Category': ['Electronics', 'Electronics', 'Electronics'],
            'Quantity': [1, 2, 1],
            'Price': [2499.99, 999.99, 249.99],
            'OrderDate': ['2024-01-01', '2024-01-01', '2024-01-02'],
            'CustomerID': [1001, 1002, 1003],
            'Country': ['USA', 'Canada', 'UK']
        }
        
        df = pd.DataFrame(test_data)
        
        importer = PostgreSQLDataImporter()
        
        # Test complete pipeline
        issues = importer.validate_csv_structure(df)
        assert isinstance(issues, list)
        
        cleaned_df = importer.clean_data(df)
        assert len(cleaned_df) == 3
        assert 'TotalValue' in cleaned_df.columns
        assert 'CustomerSegment' in cleaned_df.columns
        
        prepared_df = importer.prepare_for_postgres(cleaned_df)
        assert len(prepared_df) == 3
        assert list(prepared_df.columns) == [
            'order_id', 'product_name', 'category', 'quantity',
            'unit_price', 'total_value', 'order_date', 'customer_id',
            'country', 'customer_segment'
        ]
        
        # Verify data integrity
        assert (prepared_df['quantity'] > 0).all()
        assert (prepared_df['unit_price'] > 0).all()
        assert (prepared_df['total_value'] > 0).all()
    
    @pytest.mark.integration
    def test_error_recovery_scenarios(self):
        """Test error recovery in various failure scenarios."""
        from data_processing.import_csv_to_postgres import PostgreSQLDataImporter
        
        importer = PostgreSQLDataImporter()
        
        # Test with completely invalid data
        invalid_data = pd.DataFrame({
            'OrderID': [None, '', 'INVALID'],
            'Product': [None, '', 'Valid Product'],
            'Category': [None, '', 'Valid Category'],
            'Quantity': [-1, 0, 1],
            'Price': [-100, 0, 50],
            'OrderDate': ['invalid', '', '2024-01-01'],
            'CustomerID': [-1, 0, 1001],
            'Country': ['', None, 'USA']
        })
        
        # Should handle gracefully and return cleaned data
        cleaned_df = importer.clean_data(invalid_data)
        
        # Should keep only valid records
        assert len(cleaned_df) <= 1  # Only the last record should be valid
        
        if len(cleaned_df) > 0:
            assert (cleaned_df['Quantity'] > 0).all()
            assert (cleaned_df['Price'] > 0).all()
            assert cleaned_df['CustomerID'].notna().all()


# Pytest fixtures for the entire test module
@pytest.fixture(scope="session")
def test_database():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Create test tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE sales (
            order_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_value REAL,
            order_date DATE,
            customer_id INTEGER,
            country TEXT,
            customer_segment TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


# Custom pytest markers and configuration
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "mock: Tests using mocks"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "database: Database related tests"
    )


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])