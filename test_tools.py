# Copyright Sierra

"""
Test runner script for tau_bench tool validation.

This script runs comprehensive tests for all tools in each environment
to ensure they behave correctly with the provided JSON data.
"""

import sys
import pytest
from pathlib import Path


def run_all_tests():
    """Run all tool tests for both environments."""
    test_dir = Path(__file__).parent / "tests"
    
    print("Running comprehensive tool tests for tau_bench...")
    print("=" * 60)
    
    # Run retail environment tests
    print("\n🛒 Testing Retail Environment Tools...")
    retail_result = pytest.main([
        str(test_dir / "envs" / "retail" / "test_tools.py"),
        "-v",
        "--tb=short"
    ])
    
    # Run airline environment tests  
    print("\n✈️  Testing Airline Environment Tools...")
    airline_result = pytest.main([
        str(test_dir / "envs" / "airline" / "test_tools.py"),
        "-v", 
        "--tb=short"
    ])
    
    # Summary
    print("\n" + "=" * 60)
    if retail_result == 0 and airline_result == 0:
        print("✅ All tool tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


def run_env_tests(env_name: str):
    """Run tests for a specific environment."""
    if env_name not in ["retail", "airline"]:
        print(f"❌ Unknown environment: {env_name}")
        print("Available environments: retail, airline")
        return 1
    
    test_dir = Path(__file__).parent / "tests" / "envs" / env_name
    print(f"Running {env_name} environment tests...")
    
    result = pytest.main([
        str(test_dir / "test_tools.py"),
        "-v",
        "--tb=short"
    ])
    
    return result


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Run all tests
        exit(run_all_tests())
    elif len(sys.argv) == 2:
        env_name = sys.argv[1]
        exit(run_env_tests(env_name))
    else:
        print("Usage:")
        print("  python test_tools.py          # Run all tests")
        print("  python test_tools.py retail   # Run retail tests only") 
        print("  python test_tools.py airline  # Run airline tests only")
        exit(1)