"""
Enhanced setup script for the driving simulator database project
Handles common installation issues and provides multiple installation strategies
"""

import subprocess
import sys
import os
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("💡 Python 3.8+ is recommended for best compatibility")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def run_pip_command(command_args, show_output=False):
    """Run pip command with proper error handling"""
    try:
        if show_output:
            # Show output for debugging
            result = subprocess.run(command_args, check=True, text=True)
            return True
        else:
            # Suppress output for cleaner installation
            with open(os.devnull, 'w') as devnull:
                result = subprocess.run(command_args, 
                                      stdout=devnull, 
                                      stderr=subprocess.PIPE, 
                                      check=True, 
                                      text=True)
            return True
    except subprocess.CalledProcessError as e:
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   Error output: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"   Unexpected error: {e}")
        return False

def upgrade_pip_and_setuptools():
    """Upgrade pip and setuptools to latest versions"""
    print("🔧 Upgrading pip and setuptools...")
    
    # Upgrade pip first
    pip_success = run_pip_command([
        sys.executable, "-m", "pip", "install", "--upgrade", "pip"
    ])
    
    if pip_success:
        print("   ✅ pip upgraded successfully")
    else:
        print("   ⚠️ pip upgrade failed, continuing...")
    
    # Upgrade setuptools
    setuptools_success = run_pip_command([
        sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"
    ])
    
    if setuptools_success:
        print("   ✅ setuptools and wheel upgraded successfully")
    else:
        print("   ⚠️ setuptools upgrade failed, continuing...")
    
    return pip_success and setuptools_success

def install_packages_individually():
    """Install packages one by one with better error handling"""
    packages = [
        "psycopg2-binary==2.9.7",
        "pandas==2.0.3", 
        "numpy==1.24.3",
        "matplotlib==3.7.2",
        "seaborn==0.12.2",
        "python-dotenv==1.0.0",
        "openpyxl==3.1.2"
    ]
    
    print("🔧 Installing packages individually...")
    failed_packages = []
    successful_packages = []
    
    for package in packages:
        print(f"   Installing {package}...")
        
        success = run_pip_command([
            sys.executable, "-m", "pip", "install", package
        ])
        
        if success:
            print(f"   ✅ {package} installed successfully")
            successful_packages.append(package)
        else:
            print(f"   ❌ Failed to install {package}")
            failed_packages.append(package)
    
    print(f"\n📊 Installation Results:")
    print(f"   ✅ Successful: {len(successful_packages)}")
    print(f"   ❌ Failed: {len(failed_packages)}")
    
    if failed_packages:
        print(f"\n⚠️ Failed to install: {', '.join(failed_packages)}")
        print("💡 Try installing these manually:")
        for pkg in failed_packages:
            print(f"   python -m pip install {pkg}")
        return len(successful_packages) > len(failed_packages)  # Success if more than half installed
    
    print("✅ All packages installed successfully!")
    return True

def install_requirements_alternative():
    """Alternative installation method without requirements.txt"""
    print("🔧 Trying alternative installation method...")
    
    # First upgrade essential tools
    upgrade_success = upgrade_pip_and_setuptools()
    if not upgrade_success:
        print("⚠️ Proceeding without pip/setuptools upgrade...")
    
    # Install packages individually
    return install_packages_individually()

def install_requirements():
    """Install all required packages with fallback strategies"""
    print("🔧 Installing required packages...")
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("📝 requirements.txt not found, using alternative method...")
        return install_requirements_alternative()
    
    # Try upgrading pip and setuptools first
    upgrade_pip_and_setuptools()
    
    # Try installing from requirements.txt
    print("📦 Installing from requirements.txt...")
    success = run_pip_command([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
    ], show_output=True)
    
    if success:
        print("✅ All packages installed successfully!")
        return True
    else:
        print(f"❌ Error installing from requirements.txt")
        print("🔄 Trying alternative installation method...")
        return install_requirements_alternative()

def create_requirements_file():
    """Create requirements.txt if it doesn't exist"""
    requirements_content = """# Database connectivity
psycopg2-binary==2.9.7

# Data analysis and manipulation
pandas==2.0.3
numpy==1.24.3

# Visualization
matplotlib==3.7.2
seaborn==0.12.2

# Environment variables
python-dotenv==1.0.0

# Excel export
openpyxl==3.1.2
"""
    
    if not os.path.exists("requirements.txt"):
        print("📝 Creating requirements.txt...")
        with open("requirements.txt", 'w') as f:
            f.write(requirements_content)
        print("✅ Created requirements.txt")

def create_env_file():
    """Create a sample .env file if it doesn't exist"""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print("📝 Creating sample .env file...")
        
        env_content = """# Database Configuration
DB_NAME=driving_sim
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# Optional: Set to 'development' or 'production'
ENVIRONMENT=development
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file")
        print("💡 Please update the database credentials in .env file")
    else:
        print("✅ .env file already exists")

def create_run_script():
    """Create a convenient run script"""
    if platform.system() == "Windows":
        script_content = """@echo off
echo 🏎️ Starting Driving Simulator Database Analysis
echo.
cd /d "%~dp0"
python src/database/python_integration/simulator_db.py
pause
"""
        script_name = "run_analysis.bat"
    else:
        script_content = """#!/bin/bash
echo "🏎️ Starting Driving Simulator Database Analysis"
echo
cd "$(dirname "$0")"
python src/database/python_integration/simulator_db.py
read -p "Press Enter to continue..."
"""
        script_name = "run_analysis.sh"
    
    if not os.path.exists(script_name):
        print(f"📝 Creating {script_name}...")
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        if platform.system() != "Windows":
            os.chmod(script_name, 0o755)  # Make executable on Unix-like systems
        
        print(f"✅ Created {script_name}")

def verify_installation():
    """Verify that all packages are installed correctly"""
    print("🔍 Verifying installation...")
    
    packages_to_test = [
        ("psycopg2", "PostgreSQL adapter"),
        ("pandas", "Data analysis library"),
        ("numpy", "Numerical computing"),
        ("matplotlib", "Plotting library"),
        ("seaborn", "Statistical visualization"),
        ("dotenv", "Environment variables"),
        ("openpyxl", "Excel support")
    ]
    
    failed_imports = []
    successful_imports = []
    
    for package, description in packages_to_test:
        try:
            if package == "dotenv":
                import dotenv
            else:
                __import__(package)
            print(f"   ✅ {description}")
            successful_imports.append(package)
        except ImportError as e:
            print(f"   ❌ {description} - Import failed: {e}")
            failed_imports.append(package)
    
    print(f"\n📊 Verification Results:")
    print(f"   ✅ Working: {len(successful_imports)}")
    print(f"   ❌ Failed: {len(failed_imports)}")
    
    if failed_imports:
        print(f"\n⚠️ Some packages failed to import: {', '.join(failed_imports)}")
        print("💡 You may need to install them manually or restart your environment")
        return len(successful_imports) > len(failed_imports)  # Success if more than half work
    
    print("✅ All packages verified successfully!")
    return True

def create_simple_test_script():
    """Create a simple test script to verify everything works"""
    test_script_content = '''"""
Simple test script to verify installation
Run this to check if everything is working
"""

def test_imports():
    """Test that all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    try:
        import pandas as pd
        print("   ✅ pandas")
    except ImportError as e:
        print(f"   ❌ pandas: {e}")
    
    try:
        import numpy as np
        print("   ✅ numpy")
    except ImportError as e:
        print(f"   ❌ numpy: {e}")
    
    try:
        import matplotlib.pyplot as plt
        print("   ✅ matplotlib")
    except ImportError as e:
        print(f"   ❌ matplotlib: {e}")
    
    try:
        import seaborn as sns
        print("   ✅ seaborn")
    except ImportError as e:
        print(f"   ❌ seaborn: {e}")
    
    try:
        from dotenv import load_dotenv
        print("   ✅ python-dotenv")
    except ImportError as e:
        print(f"   ❌ python-dotenv: {e}")
    
    try:
        import openpyxl
        print("   ✅ openpyxl")
    except ImportError as e:
        print(f"   ❌ openpyxl: {e}")
    
    try:
        import psycopg2
        print("   ✅ psycopg2")
    except ImportError as e:
        print(f"   ❌ psycopg2: {e}")

def test_data_analysis():
    """Test basic data analysis functionality"""
    print("\\n📊 Testing data analysis functionality...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Create sample data
        data = {
            'numbers': np.random.randn(100),
            'categories': np.random.choice(['A', 'B', 'C'], 100)
        }
        df = pd.DataFrame(data)
        
        # Basic operations
        mean_val = df['numbers'].mean()
        print(f"   ✅ Sample data created and analyzed. Mean: {mean_val:.2f}")
        
    except Exception as e:
        print(f"   ❌ Data analysis test failed: {e}")

if __name__ == "__main__":
    print("🚀 Installation Verification Test")
    print("=" * 40)
    
    test_imports()
    test_data_analysis()
    
    print("\\n✅ Test completed!")
    print("If you see ❌ errors above, those packages need to be reinstalled.")
'''
    
    test_file = "test_installation.py"
    if not os.path.exists(test_file):
        print(f"📝 Creating {test_file}...")
        with open(test_file, 'w') as f:
            f.write(test_script_content)
        print(f"✅ Created {test_file}")
        print(f"💡 Run 'python {test_file}' to test your installation")

def main():
    """Main setup function"""
    print("🚀 Setting up Driving Simulator Database Project")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("⚠️ Proceeding anyway, but some packages might not work correctly")
    
    # Create requirements file
    create_requirements_file()
    
    # Install packages
    installation_success = install_requirements()
    
    if installation_success:
        # Verify installation
        verification_success = verify_installation()
        
        # Create additional files
        create_env_file()
        create_run_script()
        create_simple_test_script()
        
        if verification_success:
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n⚠️ Setup completed with some issues")
        
        print("\n📋 Next steps:")
        print("1. Test installation: python test_installation.py")
        print("2. Update database credentials in .env file")
        print("3. Ensure PostgreSQL is running")
        print("4. Run the analysis:")
        
        if platform.system() == "Windows":
            print("   - Double-click run_analysis.bat, or")
        else:
            print("   - Run ./run_analysis.sh, or")
        
        print("   - Run: python data-analysis.py")
        
        print("\n💡 Troubleshooting:")
        print("   - If you get import errors, run: python test_installation.py")
        print("   - For database connection errors, check PostgreSQL is running")
        print("   - Update .env file with correct database credentials")
        
    else:
        print("\n❌ Setup failed")
        print("💡 Manual installation steps:")
        print("1. Upgrade pip: python -m pip install --upgrade pip")
        print("2. Install setuptools: python -m pip install --upgrade setuptools wheel")
        print("3. Install packages individually:")
        print("   python -m pip install psycopg2-binary")
        print("   python -m pip install pandas numpy matplotlib seaborn")
        print("   python -m pip install python-dotenv openpyxl")
        print("4. Test with: python test_installation.py")

if __name__ == "__main__":
    main()