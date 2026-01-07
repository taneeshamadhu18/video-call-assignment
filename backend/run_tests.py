#!/usr/bin/env python3
"""
Test runner script for the backend API tests.
This script runs all tests and provides comprehensive coverage reporting.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    """Main test runner function."""
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🧪 AiRoHire Backend Test Suite")
    print("="*60)
    
    # Check if pytest is installed
    try:
        subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pytest is not installed. Please install requirements first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    all_passed = True
    
    # Test configurations
    test_configs = [
        {
            "command": f"{sys.executable} -m pytest tests/ -v",
            "description": "Basic Test Suite"
        },
        {
            "command": f"{sys.executable} -m pytest tests/ -v --tb=short",
            "description": "Test Suite with Short Traceback"
        },
        {
            "command": f"{sys.executable} -m pytest tests/ --cov=. --cov-report=term-missing",
            "description": "Test Suite with Coverage Report"
        },
        {
            "command": f"{sys.executable} -m pytest tests/ --cov=. --cov-report=html",
            "description": "Test Suite with HTML Coverage Report"
        }
    ]
    
    # Run individual test files first
    test_files = [
        "tests/test_api_comprehensive.py",
        "tests/test_models_comprehensive.py"
    ]
    
    print("\n📋 Running Individual Test Files:")
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_command(
                f"{sys.executable} -m pytest {test_file} -v",
                f"Running {test_file}"
            )
            if not success:
                all_passed = False
        else:
            print(f"⚠️  Test file {test_file} not found, skipping...")
    
    # Run comprehensive test suites
    print("\n📋 Running Comprehensive Test Suites:")
    for config in test_configs:
        success = run_command(config["command"], config["description"])
        if not success:
            all_passed = False
    
    # Additional useful commands
    additional_commands = [
        {
            "command": f"{sys.executable} -m pytest tests/ --durations=10",
            "description": "Test Performance Analysis (Top 10 Slowest)"
        },
        {
            "command": f"{sys.executable} -m pytest tests/ --collect-only",
            "description": "Test Collection Verification"
        }
    ]
    
    print("\n📊 Additional Test Analysis:")
    for config in additional_commands:
        run_command(config["command"], config["description"])
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if all_passed:
        print("🎉 All tests completed successfully!")
        print("📁 Coverage reports generated:")
        print("   - Terminal: See above output")
        print("   - HTML: Open 'htmlcov/index.html' in your browser")
        print("\n✅ Backend test suite passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        print("🔍 Tips for debugging:")
        print("   - Check database connections")
        print("   - Ensure all dependencies are installed")
        print("   - Review failing test output")
        sys.exit(1)

if __name__ == "__main__":
    main()