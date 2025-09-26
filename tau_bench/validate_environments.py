"""
Environment validation test runner using simplified task validation.

This module provides a simplified task validation approach that:
1. Uses syntactic checks via Python compiler for task actions
2. Uses semantic checks via automatic function invocation with database
"""

import sys
from typing import Dict, List, Tuple
from tau_bench.test_tools import run_environment_validation, run_all_environments_validation


def run_environment_tests(env_names: List[str]) -> Dict[str, bool]:
    """
    Run simplified task validation for specified environments.
    
    Args:
        env_names: List of environment names to test ('healthcare', 'retail', 'airline')
        
    Returns:
        Dictionary mapping environment names to test success status
    """
    return run_all_environments_validation(envs=env_names)


def validate_environment(env_name: str) -> bool:
    """
    Validate a single environment.
    
    Args:
        env_name: Name of the environment to validate
        
    Returns:
        True if validation passes, False otherwise
    """
    if env_name not in ["healthcare", "retail", "airline"]:
        print(f"❌ Unknown environment: {env_name}")
        print("   Valid environments: healthcare, retail, airline")
        return False
    
    return run_environment_validation(env_name)


def validate_all_environments() -> Tuple[bool, Dict[str, bool]]:
    """
    Validate all available environments.
    
    Returns:
        Tuple of (all_passed, individual_results)
    """
    env_names = ["healthcare", "retail", "airline"]
    results = run_all_environments_validation(envs=env_names)
    all_passed = all(results.values())
    return all_passed, results


def main():
    """Command line interface for environment validation."""
    if len(sys.argv) > 1:
        env_name = sys.argv[1].lower()
        if env_name in ["healthcare", "retail", "airline"]:
            success = validate_environment(env_name)
            sys.exit(0 if success else 1)
        elif env_name == "all":
            all_passed, _ = validate_all_environments()
            sys.exit(0 if all_passed else 1)
        else:
            print(f"❌ Unknown environment: {env_name}")
            print("   Usage: python validate_environments.py [healthcare|retail|airline|all]")
            print("   Examples:")
            print("     python validate_environments.py healthcare")
            print("     python validate_environments.py all")
            sys.exit(1)
    else:
        # Default: validate all environments
        all_passed, _ = validate_all_environments()
        sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()