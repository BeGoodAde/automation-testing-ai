import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch


@pytest.fixture
def sample_sales_data():
    """Sample sales data for testing"""
    return pd.DataFrame({
        'order_id': range(1, 101),
        'customer_id': np.random.randint(1, 21, 100),
        'product_id': np.random.randint(1, 11, 100),
        'amount': np.random.uniform(10.0, 500.0, 100),
        'order_date': pd.date_range('2023-01-01', periods=100, freq='D')
    })


@pytest.fixture
def mock_database():
    """Mock database connection for testing"""
    mock_db = Mock()
    mock_db.connect.return_value = True
    mock_db.execute.return_value = True
    return mock_db


@pytest.fixture
def mock_postgresql_config():
    """Mock PostgreSQL configuration"""
    return {
        'host': 'localhost',
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_pass',
        'port': 5432
    }
