#!/usr/bin/env python3
"""
Test Runner for Crowd Due Dill
Simple script to run tests from different categories.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_test(test_path: str) -> bool:
    """Run a single test file and return success status"""
    try:
        print(f"\n🧪 Running: {test_path}")
        print("=" * 60)
        
        # Run the test from the project root directory
        project_root = Path(__file__).parent.parent
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=project_root,
            capture_output=False
        )
        
        success = result.returncode == 0
        if success:
            print(f"✅ PASSED: {test_path}")
        else:
            print(f"❌ FAILED: {test_path}")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR running {test_path}: {e}")
        return False

def find_tests(test_dir: str) -> list:
    """Find all test files in a directory"""
    test_files = []
    test_path = Path(__file__).parent / test_dir
    
    if test_path.exists():
        for file in test_path.glob("test_*.py"):
            test_files.append(str(file.relative_to(Path(__file__).parent.parent)))
    
    return test_files

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Run tests for Crowd Due Dill")
    parser.add_argument("category", nargs="?", choices=["unit", "integration", "all", "article22"], 
                       default="all", help="Test category to run")
    
    args = parser.parse_args()
    
    print("🚀 Crowd Due Dill Test Runner")
    print("=" * 60)
    
    all_tests = []
    
    if args.category == "unit" or args.category == "all":
        unit_tests = find_tests("unit")
        all_tests.extend(unit_tests)
        print(f"📦 Found {len(unit_tests)} unit tests")
    
    if args.category == "integration" or args.category == "all":
        integration_tests = find_tests("integration")
        all_tests.extend(integration_tests)
        print(f"🔗 Found {len(integration_tests)} integration tests")
    
    if args.category == "article22":
        # Special case for Article 22 test
        article22_test = "tests/integration/test_article22.py"
        if Path(article22_test).exists():
            all_tests = [article22_test]
            print(f"🎯 Running Article 22 hybrid retrieval test")
        else:
            print(f"❌ Article 22 test not found: {article22_test}")
            return 1
    
    # Add any tests in the main tests directory
    if args.category == "all":
        main_tests = []
        for file in Path(__file__).parent.glob("test_*.py"):
            if file.name != "test_role_implementation.py":  # Skip if it has special requirements
                main_tests.append(str(file.relative_to(Path(__file__).parent.parent)))
        all_tests.extend(main_tests)
        if main_tests:
            print(f"📋 Found {len(main_tests)} main tests")
    
    if not all_tests:
        print("📭 No tests found to run")
        return 0
    
    print(f"\n🏃 Running {len(all_tests)} tests...")
    
    passed = 0
    failed = 0
    
    for test_path in all_tests:
        if run_test(test_path):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"❌ {failed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 