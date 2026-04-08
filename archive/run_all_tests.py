#!/usr/bin/env python3
"""
Run all tests and generate a summary report
"""
import subprocess
import sys
from pathlib import Path

def run_all_tests():
    """Run all tests and return results"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--no-cov",
        "--tb=no",
        "-q",
        "--disable-warnings",
        "--collect-only"
    ]
    
    # First collect all tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("=== Test Collection ===")
    print(result.stdout.split('\n')[-5:-1])
    
    # Run non-integration tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--no-cov",
        "--tb=no",
        "-q",
        "--disable-warnings",
        "-m", "not integration"
    ]
    
    print("\n=== Running Non-Integration Tests ===")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    # Parse results
    lines = result.stdout.split('\n')
    for line in lines:
        if 'passed' in line or 'failed' in line or 'error' in line:
            print(line)
    
    print("\n=== Summary ===")
    print(f"Return code: {result.returncode}")
    
    # Count test results
    passed = 0
    failed = 0
    errors = 0
    
    for line in lines:
        if 'passed' in line:
            try:
                passed = int(line.split()[0])
            except:
                pass
        if 'failed' in line:
            try:
                failed = int([x for x in line.split() if 'failed' in x][0].replace(',', ''))
            except:
                pass
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
