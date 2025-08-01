"""
Comprehensive test runner for the automation testing project
Runs all tests and generates detailed reports
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import json

class TestRunner:
    """Comprehensive test runner for automation testing project."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {}
        
    def run_test_suite(self, test_name, pytest_args):
        """Run a specific test suite and capture results."""
        print(f"\n🧪 Running {test_name}...")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest"] + pytest_args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            self.results[test_name] = {
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            if result.returncode == 0:
                print(f"✅ {test_name} PASSED ({duration:.2f}s)")
            else:
                print(f"❌ {test_name} FAILED ({duration:.2f}s)")
                if result.stdout:
                    print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                if result.stderr:
                    print("STDERR:", result.stderr[-500:])
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} TIMEOUT (exceeded 5 minutes)")
            self.results[test_name] = {
                'success': False,
                'duration': 300,
                'stdout': '',
                'stderr': 'Test timed out',
                'returncode': -1
            }
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            self.results[test_name] = {
                'success': False,
                'duration': 0,
                'stdout': '',
                'stderr': str(e),
                'returncode': -2
            }
    
    def run_all_tests(self):
        """Run all test suites in the project."""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        # Test configurations
        test_suites = [
            {
                'name': 'Unit Tests',
                'args': ['-m', 'unit', '-v', '--tb=short']
            },
            {
                'name': 'Integration Tests', 
                'args': ['-m', 'integration', '-v', '--tb=short']
            },
            {
                'name': 'Data Cleaning Tests',
                'args': ['test_cleaning.py', '-v']
            },
            {
                'name': 'Application Health Check',
                'args': ['test_automation_health.py', '-v', '--tb=short']
            },
            {
                'name': 'Database Tests (if available)',
                'args': ['-m', 'database', '-v', '--tb=short']
            },
            {
                'name': 'Performance Tests',
                'args': ['-m', 'slow', '-v', '--tb=short']
            },
            {
                'name': 'Analytics Tests',
                'args': ['-m', 'analytics', '-v', '--tb=short']
            }
        ]
        
        # Run each test suite
        for suite in test_suites:
            self.run_test_suite(suite['name'], suite['args'])
        
        # Generate summary report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n📊 Test Results Summary")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['success'])
        failed_tests = total_tests - passed_tests
        total_duration = sum(r['duration'] for r in self.results.values())
        
        print(f"Total Test Suites: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        
        print(f"\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {test_name}: {status} ({result['duration']:.2f}s)")
        
        # Save detailed report to file
        self.save_report_to_file()
        
        return passed_tests == total_tests
    
    def save_report_to_file(self):
        """Save detailed test report to JSON file."""
        report_file = self.project_root / 'test_report.json'
        
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_suites': len(self.results),
                'passed': sum(1 for r in self.results.values() if r['success']),
                'failed': sum(1 for r in self.results.values() if not r['success']),
                'total_duration': sum(r['duration'] for r in self.results.values())
            },
            'results': self.results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def check_prerequisites(self):
        """Check that all prerequisites are met before running tests."""
        print("🔍 Checking Prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            print(f"⚠️ Python {python_version.major}.{python_version.minor} detected. Python 3.8+ recommended.")
        else:
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check required packages
        required_packages = ['pytest', 'pandas', 'numpy']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} - Missing")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️ Missing packages: {missing_packages}")
            print("💡 Run 'python setup.py' to install missing packages")
            return False
        
        # Check test files exist
        required_files = ['pytest.ini', 'test_cleaning.py', 'test_automation_health.py']
        missing_files = []
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"✅ {file_name}")
            else:
                print(f"❌ {file_name} - Missing")
                missing_files.append(file_name)
        
        if missing_files:
            print(f"\n⚠️ Missing files: {missing_files}")
            return False
        
        print("✅ All prerequisites met!")
        return True

def main():
    """Main function to run all tests."""
    runner = TestRunner()
    
    # Check prerequisites first
    if not runner.check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix issues and try again.")
        return False
    
    # Run all tests
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Your automation application is working correctly.")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the results above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)