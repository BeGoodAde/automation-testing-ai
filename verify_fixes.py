"""
Quick verification script to check if common issues are fixed
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_imports():
    """Check that all Python modules can be imported."""
    print("🐍 Checking Python Imports...")
    
    imports_to_test = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('seaborn', 'sns'),
        ('pytest', None),
        ('pathlib', 'Path'),
        ('unittest.mock', 'Mock')
    ]
    
    failed_imports = []
    
    for module_name, alias in imports_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    return len(failed_imports) == 0

def check_test_files():
    """Check that test files have correct syntax."""
    print("\n🧪 Checking Test File Syntax...")
    
    test_files = [
        'test_cleaning.py',
        'test_automation_health.py'
    ]
    
    project_root = Path(__file__).parent
    syntax_errors = []
    
    for test_file in test_files:
        file_path = project_root / test_file
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                compile(code, file_path, 'exec')
                print(f"  ✅ {test_file}")
            except SyntaxError as e:
                print(f"  ❌ {test_file}: Syntax error at line {e.lineno}")
                syntax_errors.append(test_file)
            except Exception as e:
                print(f"  ❌ {test_file}: {e}")
                syntax_errors.append(test_file)
        else:
            print(f"  ⚠️ {test_file}: File not found")
    
    return len(syntax_errors) == 0

def check_pytest_config():
    """Check pytest configuration."""
    print("\n⚙️ Checking Pytest Configuration...")
    
    pytest_ini = Path(__file__).parent / 'pytest.ini'
    
    if not pytest_ini.exists():
        print("  ❌ pytest.ini not found")
        return False
    
    try:
        with open(pytest_ini, 'r') as f:
            content = f.read()
        
        required_sections = ['[tool:pytest]', 'testpaths', 'markers']
        missing_sections = []
        
        for section in required_sections:
            if section in content:
                print(f"  ✅ {section}")
            else:
                print(f"  ❌ {section}")
                missing_sections.append(section)
        
        return len(missing_sections) == 0
        
    except Exception as e:
        print(f"  ❌ Error reading pytest.ini: {e}")
        return False

def check_sample_data_generation():
    """Test sample data generation."""
    print("\n📊 Testing Sample Data Generation...")
    
    try:
        # Try to import and run sample data generation
        sys.path.append(str(Path(__file__).parent))
        from data_analysis import generate_sample_data
        
        # Generate small test dataset
        df = generate_sample_data(10)
        
        if df is not None and len(df) == 10:
            print("  ✅ Sample data generation works")
            return True
        else:
            print("  ❌ Sample data generation failed")
            return False
            
    except ImportError as e:
        print(f"  ❌ Cannot import data_analysis module: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error generating sample data: {e}")
        return False

def run_quick_test():
    """Run a quick pytest test to verify setup."""
    print("\n🏃 Running Quick Test...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'test_cleaning.py::TestDataCleaning::test_remove_null_values',
            '-v'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Quick test passed")
            return True
        else:
            print("  ❌ Quick test failed")
            if result.stdout:
                print(f"    Output: {result.stdout[-200:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⏰ Quick test timed out")
        return False
    except Exception as e:
        print(f"  ❌ Error running quick test: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🔍 Running Automation Application Verification")
    print("=" * 50)
    
    checks = [
        ("Python Imports", check_python_imports),
        ("Test File Syntax", check_test_files),
        ("Pytest Configuration", check_pytest_config),
        ("Sample Data Generation", check_sample_data_generation),
        ("Quick Test Run", run_quick_test)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n💥 Error in {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print("\n📋 Verification Summary")
    print("-" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All verification checks passed!")
        print("Your automation application is working correctly!")
        return True
    else:
        print(f"\n⚠️ {total - passed} checks failed.")
        print("Please review the issues above and run 'python setup.py' if needed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)