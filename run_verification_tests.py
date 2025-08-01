"""
Test runner specifically for verification function tests
Provides detailed reporting on test verification capabilities
"""

import subprocess
import sys
import time
from pathlib import Path

def run_verification_tests():
    """Run all verification tests with detailed reporting."""
    print("🧪 Running Verification Function Tests")
    print("=" * 60)
    
    test_categories = [
        {
            'name': 'Python Import Tests',
            'pattern': 'test_verify_fixes.py::TestCheckPythonImports',
            'description': 'Tests for Python package import verification'
        },
        {
            'name': 'Test File Syntax Tests',
            'pattern': 'test_verify_fixes.py::TestCheckTestFiles',
            'description': 'Tests for test file syntax validation'
        },
        {
            'name': 'Pytest Config Tests',
            'pattern': 'test_verify_fixes.py::TestCheckPytestConfig',
            'description': 'Tests for pytest configuration validation'
        },
        {
            'name': 'Sample Data Generation Tests',
            'pattern': 'test_verify_fixes.py::TestCheckSampleDataGeneration',
            'description': 'Tests for sample data generation functionality'
        },
        {
            'name': 'Quick Test Execution Tests',
            'pattern': 'test_verify_fixes.py::TestRunQuickTest',
            'description': 'Tests for quick test execution functionality'
        },
        {
            'name': 'Main Function Integration Tests',
            'pattern': 'test_verify_fixes.py::TestMainFunction',
            'description': 'Tests for main verification workflow'
        },
        {
            'name': 'Integration Scenario Tests',
            'pattern': 'test_verify_fixes.py::TestIntegrationScenarios',
            'description': 'End-to-end integration scenario tests'
        },
        {
            'name': 'Edge Case Tests',
            'pattern': 'test_verify_fixes.py::TestEdgeCases',
            'description': 'Tests for edge cases and error conditions'
        },
        {
            'name': 'Performance Tests',
            'pattern': 'test_verify_fixes.py::TestPerformanceAndStress',
            'description': 'Performance and stress tests'
        }
    ]
    
    results = {}
    total_duration = 0
    
    for category in test_categories:
        print(f"\n🔍 {category['name']}")
        print(f"   {category['description']}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                category['pattern'],
                "-v",
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, timeout=120)
            
            duration = time.time() - start_time
            total_duration += duration
            
            if result.returncode == 0:
                print(f"   ✅ PASSED ({duration:.2f}s)")
                results[category['name']] = True
            else:
                print(f"   ❌ FAILED ({duration:.2f}s)")
                results[category['name']] = False
                if result.stdout:
                    print(f"   Output: {result.stdout[-300:]}")
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ TIMEOUT (>120s)")
            results[category['name']] = False
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results[category['name']] = False
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"Total Categories: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Total Duration: {total_duration:.2f}s")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    for category, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {category}: {status}")
    
    if passed == total:
        print(f"\n🎉 All verification tests passed!")
        print("Your verification functions are working correctly!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test categories failed.")
        print("Some verification functions may have issues.")
        return False

def run_specific_test_type(test_type):
    """Run specific type of verification tests."""
    test_markers = {
        'unit': 'unit',
        'integration': 'integration', 
        'performance': 'slow or performance',
        'edge-cases': 'TestEdgeCases'
    }
    
    if test_type not in test_markers:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available types: {list(test_markers.keys())}")
        return False
    
    print(f"🧪 Running {test_type.title()} Verification Tests")
    print("=" * 50)
    
    marker = test_markers[test_type]
    
    if test_type == 'edge-cases':
        # Run specific class
        cmd = [
            sys.executable, "-m", "pytest",
            f"test_verify_fixes.py::{marker}",
            "-v", "--tb=short"
        ]
    else:
        # Run by marker
        cmd = [
            sys.executable, "-m", "pytest",
            "test_verify_fixes.py",
            "-m", marker,
            "-v", "--tb=short"
        ]
    
    try:
        result = subprocess.run(cmd, timeout=180)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Tests timed out")
        return False
    except Exception as e:
        print(f"💥 Error running tests: {e}")
        return False

def main():
    """Main function with command line options."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        success = run_specific_test_type(test_type)
    else:
        success = run_verification_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)