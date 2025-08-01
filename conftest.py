"""
Pytest configuration and fixtures for verification tests
Provides common fixtures and test configuration
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pandas as pd
import numpy as np

# Test configuration
def pytest_configure(config):
    """Configure pytest for verification tests."""
    config.addinivalue_line(
        "markers", "verification: Tests for verification functions"
    )
    config.addinivalue_line(
        "markers", "mock_heavy: Tests that use extensive mocking"
    )

# Common fixtures
@pytest.fixture(scope="session")
def temp_project_dir():
    """Create temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        yield project_path

@pytest.fixture
def mock_pandas_dataframe():
    """Create mock pandas DataFrame for testing."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'value': [10.5, 20.3, 15.7, 30.1, 25.9],
        'category': ['A', 'B', 'A', 'C', 'B']
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_importlib():
    """Mock importlib for testing imports."""
    mock = Mock()
    mock.import_module = Mock()
    return mock

@pytest.fixture
def sample_python_file_content():
    """Sample Python file content for testing."""
    return '''
import pytest
import pandas as pd
from unittest.mock import Mock

class TestSample:
    """Sample test class."""
    
    def test_basic_operation(self):
        """Test basic operation."""
        assert 1 + 1 == 2
    
    def test_pandas_operation(self):
        """Test pandas operation."""
        df = pd.DataFrame({'a': [1, 2, 3]})
        assert len(df) == 3
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """Test slow operation."""
        import time
        time.sleep(0.1)
        assert True
'''

@pytest.fixture
def sample_pytest_ini_valid():
    """Valid pytest.ini content for testing."""
    return '''
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --strict-config
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
    --durations=10
    --maxfail=3
markers =
    unit: Unit tests
    integration: Integration tests
    database: Database tests
    slow: Slow running tests
    simulator: Driving simulator tests
    analytics: Data analytics tests
    performance: Performance tests
    real_time: Real-time processing tests
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
'''

@pytest.fixture
def sample_pytest_ini_invalid():
    """Invalid pytest.ini content for testing."""
    return '''
[tool:pytest]
# Missing required sections like testpaths and markers
addopts = -v
'''

@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess result."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "All tests passed successfully"
    mock_result.stderr = ""
    return mock_result

@pytest.fixture
def mock_subprocess_failure():
    """Mock failed subprocess result."""
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = "Test failed with errors"
    mock_result.stderr = "Error: test_function failed"
    return mock_result

# Test data generators
@pytest.fixture
def sample_sales_data():
    """Generate sample sales data for testing."""
    np.random.seed(42)
    
    data = {
        'order_id': [f'ORD_{i:06d}' for i in range(100)],
        'customer_id': [f'CUST_{i%20:04d}' for i in range(100)],
        'order_date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'product_name': np.random.choice(['Product A', 'Product B', 'Product C'], 100),
        'category': np.random.choice(['Electronics', 'Clothing', 'Books'], 100),
        'price': np.random.uniform(10, 100, 100),
        'quantity': np.random.randint(1, 5, 100),
        'total': np.random.uniform(10, 500, 100)
    }
    
    return pd.DataFrame(data)

# Mock classes for testing
class MockModule:
    """Mock module for testing imports."""
    
    def __init__(self, name):
        self.name = name
        self.__name__ = name
    
    def __getattr__(self, item):
        return Mock()

# Pytest hooks for better test reporting
def pytest_runtest_makereport(item, call):
    """Customize test reporting."""
    if "verification" in item.keywords:
        if call.when == "call":
            if call.excinfo is None:
                print(f"✅ Verification test passed: {item.name}")
            else:
                print(f"❌ Verification test failed: {item.name}")

# Helper functions for tests
def create_temp_file(content, suffix='.py'):
    """Create temporary file with content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name

def cleanup_temp_file(file_path):
    """Clean up temporary file."""
    try:
        os.unlink(file_path)
    except FileNotFoundError:
        pass

# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()

# Markers for better test organization
pytest.mark.verification = pytest.mark.mark("verification")
pytest.mark.mock_heavy = pytest.mark.mark("mock_heavy")