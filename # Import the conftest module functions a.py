# Import the conftest module functions and fixtures
from conftest import (
    pytest_configure,
    pytest_runtest_makereport,
    create_temp_file,
    cleanup_temp_file,
    MockModule
)


class TestPytestConfiguration:
    """Test pytest configuration and setup functions."""
    
    @pytest.mark.unit
    def test_pytest_configure_adds_markers(self):
        """Test that pytest_configure adds custom markers."""
        mock_config = Mock()
        mock_config.addinivalue_line = Mock()
        
        pytest_configure(mock_config)
        
        # Verify markers were added
        expected_calls = [
            ('markers', 'verification: Tests for verification functions'),
            ('markers', 'mock_heavy: Tests that use extensive mocking')
        ]
        
        for call_args in expected_calls:
            mock_config.addinivalue_line.assert_any_call(*call_args)
        
        assert mock_config.addinivalue_line.call_count == 2

    @pytest.mark.unit
    def test_pytest_configure_with_none_config(self):
        """Test pytest_configure handles None config gracefully."""
        # This should not raise an exception
        try:
            pytest_configure(None)
            # If we get here, the function handled None gracefully
            # In real pytest, this wouldn't happen, but we test defensive coding
        except AttributeError:
            # Expected behavior when config is None
            pass

    @pytest.mark.verification
    def test_pytest_runtest_makereport_success(self, capsys):
        """Test pytest hook for successful verification tests."""
        # Create mock item and call objects
        mock_item = Mock()
        mock_item.name = "test_verification_example"
        mock_item.keywords = {"verification": Mock()}
        
        mock_call = Mock()
        mock_call.when = "call"
        mock_call.excinfo = None  # No exception = success
        
        pytest_runtest_makereport(mock_item, mock_call)
        
        captured = capsys.readouterr()
        assert "✅ Verification test passed: test_verification_example" in captured.out

    @pytest.mark.verification
    def test_pytest_runtest_makereport_failure(self, capsys):
        """Test pytest hook for failed verification tests."""
        mock_item = Mock()
        mock_item.name = "test_verification_failure"
        mock_item.keywords = {"verification": Mock()}
        
        mock_call = Mock()
        mock_call.when = "call"
        mock_call.excinfo = Exception("Test failed")  # Exception = failure
        
        pytest_runtest_makereport(mock_item, mock_call)
        
        captured = capsys.readouterr()
        assert "❌ Verification test failed: test_verification_failure" in captured.out

    @pytest.mark.unit
    def test_pytest_runtest_makereport_non_verification(self, capsys):
        """Test pytest hook ignores non-verification tests."""
        mock_item = Mock()
        mock_item.name = "test_regular_test"
        mock_item.keywords = {}  # No verification marker
        
        mock_call = Mock()
        mock_call.when = "call"
        mock_call.excinfo = None
        
        pytest_runtest_makereport(mock_item, mock_call)
        
        captured = capsys.readouterr()
        assert "Verification test" not in captured.out

    @pytest.mark.unit
    def test_pytest_runtest_makereport_different_phase(self, capsys):
        """Test pytest hook only acts during 'call' phase."""
        mock_item = Mock()
        mock_item.name = "test_setup_phase"
        mock_item.keywords = {"verification": Mock()}
        
        mock_call = Mock()
        mock_call.when = "setup"  # Not 'call' phase
        mock_call.excinfo = None
        
        pytest_runtest_makereport(mock_item, mock_call)
        
        captured = capsys.readouterr()
        assert "Verification test" not in captured.out


class TestFixtures:
    """Test all pytest fixtures defined in conftest.py."""
    
    @pytest.mark.unit
    def test_temp_project_dir_fixture(self, temp_project_dir):
        """Test temporary project directory fixture."""
        assert isinstance(temp_project_dir, Path)
        assert temp_project_dir.exists()
        assert temp_project_dir.is_dir()
        assert temp_project_dir.name == "test_project"

    @pytest.mark.unit
    def test_mock_pandas_dataframe_fixture(self, mock_pandas_dataframe):
        """Test mock pandas DataFrame fixture."""
        assert isinstance(mock_pandas_dataframe, pd.DataFrame)
        assert len(mock_pandas_dataframe) == 5
        assert list(mock_pandas_dataframe.columns) == ['id', 'name', 'value', 'category']
        assert mock_pandas_dataframe['id'].tolist() == [1, 2, 3, 4, 5]
        assert 'Alice' in mock_pandas_dataframe['name'].values

    @pytest.mark.unit
    def test_mock_importlib_fixture(self, mock_importlib):
        """Test mock importlib fixture."""
        assert hasattr(mock_importlib, 'import_module')
        assert isinstance(mock_importlib.import_module, Mock)
        
        # Test that it can be used as expected
        mock_importlib.import_module.return_value = Mock()
        result = mock_importlib.import_module('test_module')
        assert isinstance(result, Mock)

    @pytest.mark.unit
    def test_sample_python_file_content_fixture(self, sample_python_file_content):
        """Test sample Python file content fixture."""
        assert isinstance(sample_python_file_content, str)
        assert 'import pytest' in sample_python_file_content
        assert 'class TestSample:' in sample_python_file_content
        assert 'def test_basic_operation(self):' in sample_python_file_content
        assert '@pytest.mark.slow' in sample_python_file_content

    @pytest.mark.unit
    def test_sample_pytest_ini_valid_fixture(self, sample_pytest_ini_valid):
        """Test valid pytest.ini content fixture."""
        assert isinstance(sample_pytest_ini_valid, str)
        assert '[tool:pytest]' in sample_pytest_ini_valid
        assert 'testpaths = tests' in sample_pytest_ini_valid
        assert 'markers =' in sample_pytest_ini_valid
        assert 'unit: Unit tests' in sample_pytest_ini_valid

    @pytest.mark.unit
    def test_sample_pytest_ini_invalid_fixture(self, sample_pytest_ini_invalid):
        """Test invalid pytest.ini content fixture."""
        assert isinstance(sample_pytest_ini_invalid, str)
        assert '[tool:pytest]' in sample_pytest_ini_invalid
        assert 'testpaths' not in sample_pytest_ini_invalid
        assert 'markers' not in sample_pytest_ini_invalid

    @pytest.mark.unit
    def test_mock_subprocess_success_fixture(self, mock_subprocess_success):
        """Test successful subprocess mock fixture."""
        assert mock_subprocess_success.returncode == 0
        assert "All tests passed successfully" in mock_subprocess_success.stdout
        assert mock_subprocess_success.stderr == ""

    @pytest.mark.unit
    def test_mock_subprocess_failure_fixture(self, mock_subprocess_failure):
        """Test failed subprocess mock fixture."""
        assert mock_subprocess_failure.returncode == 1
        assert "Test failed with errors" in mock_subprocess_failure.stdout
        assert "Error: test_function failed" in mock_subprocess_failure.stderr

    @pytest.mark.unit
    def test_sample_sales_data_fixture(self, sample_sales_data):
        """Test sample sales data fixture."""
        assert isinstance(sample_sales_data, pd.DataFrame)
        assert len(sample_sales_data) == 100
        
        expected_columns = ['order_id', 'customer_id', 'order_date', 'product_name', 
                          'category', 'price', 'quantity', 'total']
        assert list(sample_sales_data.columns) == expected_columns
        
        # Test data types and patterns
        assert sample_sales_data['order_id'].str.startswith('ORD_').all()
        assert sample_sales_data['customer_id'].str.startswith('CUST_').all()
        assert pd.api.types.is_datetime64_any_dtype(sample_sales_data['order_date'])

    @pytest.mark.performance
    def test_performance_timer_fixture(self, performance_timer):
        """Test performance timer fixture."""
        assert hasattr(performance_timer, 'start')
        assert hasattr(performance_timer, 'stop')
        assert hasattr(performance_timer, 'duration')
        
        # Test timer functionality
        performance_timer.start()
        time.sleep(0.01)  # Small delay
        performance_timer.stop()
        
        assert performance_timer.duration is not None
        assert performance_timer.duration > 0
        assert performance_timer.duration < 1  # Should be very quick


class TestHelperFunctions:
    """Test helper functions from conftest.py."""
    
    @pytest.mark.unit
    def test_create_temp_file_default_suffix(self):
        """Test creating temporary file with default .py suffix."""
        content = "print('Hello, World!')"
        file_path = create_temp_file(content)
        
        try:
            assert os.path.exists(file_path)
            assert file_path.endswith('.py')
            
            with open(file_path, 'r') as f:
                assert f.read() == content
        finally:
            cleanup_temp_file(file_path)

    @pytest.mark.unit
    def test_create_temp_file_custom_suffix(self):
        """Test creating temporary file with custom suffix."""
        content = "Test content"
        file_path = create_temp_file(content, suffix='.txt')
        
        try:
            assert os.path.exists(file_path)
            assert file_path.endswith('.txt')
            
            with open(file_path, 'r') as f:
                assert f.read() == content
        finally:
            cleanup_temp_file(file_path)

    @pytest.mark.unit
    def test_create_temp_file_empty_content(self):
        """Test creating temporary file with empty content."""
        content = ""
        file_path = create_temp_file(content)
        
        try:
            assert os.path.exists(file_path)
            
            with open(file_path, 'r') as f:
                assert f.read() == ""
        finally:
            cleanup_temp_file(file_path)

    @pytest.mark.unit
    def test_create_temp_file_unicode_content(self):
        """Test creating temporary file with Unicode content."""
        content = "Hello, 世界! 🌍"
        file_path = create_temp_file(content)
        
        try:
            assert os.path.exists(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                assert f.read() == content
        finally:
            cleanup_temp_file(file_path)

    @pytest.mark.unit
    def test_cleanup_temp_file_existing(self):
        """Test cleanup of existing temporary file."""
        content = "Temporary content"
        file_path = create_temp_file(content)
        
        assert os.path.exists(file_path)
        cleanup_temp_file(file_path)
        assert not os.path.exists(file_path)

    @pytest.mark.unit
    def test_cleanup_temp_file_nonexistent(self):
        """Test cleanup of non-existent file (should not raise error)."""
        non_existent_path = "/tmp/definitely_does_not_exist_12345.txt"
        
        # Should not raise FileNotFoundError
        cleanup_temp_file(non_existent_path)
        
        # Function should complete without error
        assert True

    @pytest.mark.unit
    def test_cleanup_temp_file_none_path(self):
        """Test cleanup with None path."""
        # Should handle None gracefully
        try:
            cleanup_temp_file(None)
        except (TypeError, AttributeError):
            # Expected behavior for None input
            pass


class TestMockClasses:
    """Test mock classes defined in conftest.py."""
    
    @pytest.mark.unit
    def test_mock_module_initialization(self):
        """Test MockModule initialization."""
        mock_module = MockModule("test_module")
        
        assert mock_module.name == "test_module"
        assert mock_module.__name__ == "test_module"

    @pytest.mark.unit
    def test_mock_module_getattr(self):
        """Test MockModule __getattr__ returns Mock objects."""
        mock_module = MockModule("test_module")
        
        # Accessing any attribute should return a Mock
        attr1 = mock_module.some_function
        attr2 = mock_module.some_class
        attr3 = mock_module.some_variable
        
        assert isinstance(attr1, Mock)
        assert isinstance(attr2, Mock)
        assert isinstance(attr3, Mock)

    @pytest.mark.unit
    def test_mock_module_multiple_attributes(self):
        """Test MockModule can handle multiple attribute access."""
        mock_module = MockModule("complex_module")
        
        # Test chained attribute access
        result = mock_module.submodule.function.call()
        assert isinstance(result, Mock)
        
        # Test that same attribute returns same mock
        func1 = mock_module.test_function
        func2 = mock_module.test_function
        assert func1 is func2  # Should be the same Mock object


class TestFixtureIntegration:
    """Integration tests for fixture combinations."""
    
    @pytest.mark.integration
    def test_temp_dir_with_sample_data(self, temp_project_dir, sample_sales_data):
        """Test using temporary directory with sample data."""
        # Save sample data to temp directory