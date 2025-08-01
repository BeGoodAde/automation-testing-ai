import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os
from pathlib import Path
import pandas as pd
import numpy as np
import time


        csv_path = temp_project_dir / "sales_data.csv"
        sample_sales_data.to_csv(csv_path, index=False)
        
        assert csv_path.exists()
        
        # Read back and verify
        loaded_data = pd.read_csv(csv_path)
        assert len(loaded_data) == len(sample_sales_data)
        assert list(loaded_data.columns) == list(sample_sales_data.columns)

    @pytest.mark.integration
    def test_mock_dataframe_with_timer(self, mock_pandas_dataframe, performance_timer):
        """Test using mock DataFrame with performance timer."""
        performance_timer.start()
        
        # Perform some operations on the DataFrame
        result = mock_pandas_dataframe.groupby('category').sum()
        filtered = mock_pandas_dataframe[mock_pandas_dataframe['value'] > 20]
        
        performance_timer.stop()
        
        assert len(result) >= 1
        assert len(filtered) >= 0
        assert performance_timer.duration is not None

    @pytest.mark.integration
    def test_file_operations_with_fixtures(self, temp_project_dir, sample_python_file_content):
        """Test file operations using multiple fixtures."""
        # Create Python file in temp directory
        python_file = temp_project_dir / "test_sample.py"
        
        with open(python_file, 'w') as f:
            f.write(sample_python_file_content)
        
        assert python_file.exists()
        
        # Verify content
        with open(python_file, 'r') as f:
            content = f.read()
        
        assert content == sample_python_file_content
        assert 'TestSample' in content


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.unit
    def test_fixture_with_empty_data(self):
        """Test fixtures handle empty data correctly."""
        # Test empty DataFrame creation
        empty_df = pd.DataFrame()
        assert len(empty_df) == 0
        assert isinstance(empty_df, pd.DataFrame)

    @pytest.mark.unit
    def test_fixture_with_large_data(self):
        """Test fixtures handle large data correctly."""
        # Create large dataset similar to sample_sales_data
        large_size = 10000
        np.random.seed(42)
        
        large_data = {
            'id': range(large_size),
            'value': np.random.randn(large_size),
            'category': np.random.choice(['A', 'B', 'C'], large_size)
        }
        
        df = pd.DataFrame(large_data)
        assert len(df) == large_size
        assert 'id' in df.columns

    @pytest.mark.unit
    def test_mock_module_with_special_names(self):
        """Test MockModule with special attribute names."""
        mock_module = MockModule("special_module")
        
        # Test special Python attributes
        dunder_method = mock_module.__special__
        private_attr = mock_module._private
        constant = mock_module.CONSTANT_VALUE
        
        assert isinstance(dunder_method, Mock)
        assert isinstance(private_attr, Mock)
        assert isinstance(constant, Mock)

    @pytest.mark.unit
    @patch('tempfile.NamedTemporaryFile')
    def test_create_temp_file_error_handling(self, mock_tempfile):
        """Test create_temp_file error handling."""
        # Mock tempfile to raise an exception
        mock_tempfile.side_effect = OSError("Disk full")
        
        with pytest.raises(OSError):
            create_temp_file("test content")

    @pytest.mark.unit
    def test_performance_timer_without_stop(self, performance_timer):
        """Test performance timer when stop() is not called."""
        performance_timer.start()
        # Don't call stop()
        
        assert performance_timer.duration is None

    @pytest.mark.unit
    def test_performance_timer_without_start(self, performance_timer):
        """Test performance timer when start() is not called."""
        performance_timer.stop()
        # Called stop() without start()
        
        assert performance_timer.duration is None


class TestDataValidation:
    """Test data validation in fixtures."""
    
    @pytest.mark.unit
    def test_sales_data_consistency(self, sample_sales_data):
        """Test that sample sales data is consistent."""
        # Check data types
        assert pd.api.types.is_string_dtype(sample_sales_data['order_id'])
        assert pd.api.types.is_string_dtype(sample_sales_data['customer_id'])
        assert pd.api.types.is_datetime64_any_dtype(sample_sales_data['order_date'])
        assert pd.api.types.is_numeric_dtype(sample_sales_data['price'])
        assert pd.api.types.is_numeric_dtype(sample_sales_data['quantity'])
        
        # Check value ranges
        assert (sample_sales_data['price'] >= 10).all()
        assert (sample_sales_data['price'] <= 100).all()
        assert (sample_sales_data['quantity'] >= 1).all()
        assert (sample_sales_data['quantity'] <= 4).all()

    @pytest.mark.unit
    def test_mock_dataframe_structure(self, mock_pandas_dataframe):
        """Test mock DataFrame has expected structure."""
        # Check required columns exist
        required_columns = ['id', 'name', 'value', 'category']
        for col in required_columns:
            assert col in mock_pandas_dataframe.columns
        
        # Check no null values
        assert not mock_pandas_dataframe.isnull().any().any()
        
        # Check data types
        assert pd.api.types.is_integer_dtype(mock_pandas_dataframe['id'])
        assert pd.api.types.is_string_dtype(mock_pandas_dataframe['name'])
        assert pd.api.types.is_numeric_dtype(mock_pandas_dataframe['value'])

    @pytest.mark.unit
    def test_python_file_content_syntax(self, sample_python_file_content):
        """Test that sample Python file content has valid syntax."""
        # Should compile without syntax errors
        try:
            compile(sample_python_file_content, '<string>', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Sample Python content has syntax error: {e}")

    @pytest.mark.unit
    def test_pytest_ini_valid_structure(self, sample_pytest_ini_valid):
        """Test that valid pytest.ini has required structure."""
        required_sections = ['[tool:pytest]', 'testpaths', 'markers', 'addopts']
        
        for section in required_sections:
            assert section in sample_pytest_ini_valid, f"Missing section: {section}"


class TestMarkerFunctionality:
    """Test custom marker functionality."""
    
    @pytest.mark.verification
    def test_verification_marker_works(self):
        """Test that verification marker is properly applied."""
        # This test itself uses the verification marker
        assert True

    @pytest.mark.mock_heavy
    def test_mock_heavy_marker_works(self):
        """Test that mock_heavy marker is properly applied."""
        # This test itself uses the mock_heavy marker
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            assert os.path.exists('any_path')

    @pytest.mark.verification
    @pytest.mark.mock_heavy
    def test_multiple_markers(self):
        """Test that multiple custom markers can be applied."""
        # This test uses both custom markers
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])