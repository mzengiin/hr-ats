#!/usr/bin/env python3
"""
Integration Test Runner
Runs all integration tests and generates a comprehensive report
"""
import subprocess
import sys
import os
import json
from datetime import datetime
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting CVFlow Integration Tests")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    test_results = {}
    
    # Test 1: Authentication Flow Tests
    print("\n📋 Running Authentication Flow Tests...")
    result = run_command("python -m pytest tests/test_integration_auth.py -v --tb=short")
    test_results['auth_flow'] = result
    if result['success']:
        print("✅ Authentication Flow Tests: PASSED")
    else:
        print("❌ Authentication Flow Tests: FAILED")
        print(f"Error: {result['stderr']}")
    
    # Test 2: Role-Based Access Control Tests
    print("\n🔐 Running Role-Based Access Control Tests...")
    result = run_command("python -m pytest tests/test_integration_rbac.py -v --tb=short")
    test_results['rbac'] = result
    if result['success']:
        print("✅ RBAC Tests: PASSED")
    else:
        print("❌ RBAC Tests: FAILED")
        print(f"Error: {result['stderr']}")
    
    # Test 3: Session Management Tests
    print("\n🔑 Running Session Management Tests...")
    result = run_command("python -m pytest tests/test_integration_session.py -v --tb=short")
    test_results['session_management'] = result
    if result['success']:
        print("✅ Session Management Tests: PASSED")
    else:
        print("❌ Session Management Tests: FAILED")
        print(f"Error: {result['stderr']}")
    
    # Test 4: Error Scenarios Tests
    print("\n⚠️ Running Error Scenarios Tests...")
    result = run_command("python -m pytest tests/test_integration_errors.py -v --tb=short")
    test_results['error_scenarios'] = result
    if result['success']:
        print("✅ Error Scenarios Tests: PASSED")
    else:
        print("❌ Error Scenarios Tests: FAILED")
        print(f"Error: {result['stderr']}")
    
    # Test 5: All Integration Tests Together
    print("\n🧪 Running All Integration Tests...")
    result = run_command("python -m pytest tests/test_integration_*.py -v --tb=short")
    test_results['all_integration'] = result
    if result['success']:
        print("✅ All Integration Tests: PASSED")
    else:
        print("❌ All Integration Tests: FAILED")
        print(f"Error: {result['stderr']}")
    
    # Test 6: Backend Unit Tests
    print("\n🔬 Running Backend Unit Tests...")
    result = run_command("python -m pytest tests/ -k 'not test_integration' -v --tb=short")
    test_results['unit_tests'] = result
    if result['success']:
        print("✅ Backend Unit Tests: PASSED")
    else:
        print("❌ Backend Unit Tests: FAILED")
        print(f"Error: {result['stderr']}")
    
    # Generate Report
    generate_report(test_results)
    
    # Return overall success
    all_passed = all(result['success'] for result in test_results.values())
    return all_passed

def generate_report(test_results):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST REPORT")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"\n📈 Summary:")
    print(f"   Total Test Suites: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        if not result['success'] and result['stderr']:
            print(f"      Error: {result['stderr'][:200]}...")
    
    # Save report to file
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100
        },
        'results': test_results
    }
    
    with open('integration_test_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: integration_test_report.json")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Please check the errors above.")
        return False
    else:
        print(f"\n🎉 All integration tests passed successfully!")
        return True

def main():
    """Main function"""
    print("CVFlow Integration Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app/main.py'):
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Run tests
    success = run_integration_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the report above.")
        sys.exit(1)

if __name__ == "__main__":
    main()








