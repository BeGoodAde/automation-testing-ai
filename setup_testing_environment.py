"""
Setup Testing Environment
Installs all required dependencies and configures the testing environment
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def setup_testing_environment():
    """Set up the complete testing environment."""
    print("🚀 Setting up Testing Environment")
    print("=" * 50)
    
    # Required packages for testing
    required_packages = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=2.0.0",
        "requests>=2.28.0",
        "faker>=18.0.0"
    ]
    
    print("📦 Installing required packages...")
    failed_packages = []
    
    for package in required_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️ Failed to install: {failed_packages}")
        print("Please install these manually or check your internet connection")
        return False
    
    # Create pytest configuration
    create_pytest_config()
    
    # Create test directories
    create_test_structure()
    
    print("\n✅ Testing environment setup complete!")
    print("🧪 You can now run tests with: python -m pytest")
    return True

def create_pytest_config():
    """Create pytest.ini configuration file."""
    pytest_config = """[tool:pytest]
testpaths = tests .
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
markers =
    unit: Unit tests
    integration: Integration tests
    analytics: Analytics and SQL tests
    performance: Performance tests
    slow: Slow running tests
    database: Database related tests
    mock: Tests using mocks
    data_validation: Data validation tests
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
"""
    
    pytest_ini_path = Path(__file__).parent / "pytest.ini"
    with open(pytest_ini_path, 'w', encoding='utf-8') as f:
        f.write(pytest_config)
    
    print("✅ Created pytest.ini configuration")

def create_test_structure():
    """Create comprehensive test directory structure."""
    base_path = Path(__file__).parent
    
    test_dirs = [
        "tests",
        "tests/unit",
        "tests/integration", 
        "tests/data",
        "tests/sql",
        "tests/performance",
        "logs",
        "reports"
    ]
    
    for test_dir in test_dirs:
        dir_path = base_path / test_dir
        dir_path.mkdir(exist_ok=True)
        
        # Create __init__.py files for Python packages
        if test_dir.startswith("tests"):
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Created test directory structure")

if __name__ == "__main__":
    setup_testing_environment()