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
        env_names: List of environment names to test (dynamically discovered)
        
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
    from tau_bench.envs import get_available_environments
    
    available_envs = get_available_environments()
    if env_name not in available_envs:
        print(f"❌ Unknown environment: {env_name}")
        print(f"   Valid environments: {', '.join(available_envs)}")
        return False
    
    return run_environment_validation(env_name)


def validate_all_environments() -> Tuple[bool, Dict[str, bool]]:
    """
    Validate all available environments.
    
    Returns:
        Tuple of (all_passed, individual_results)
    """
    from tau_bench.envs import get_available_environments
    
    env_names = get_available_environments()
    results = run_all_environments_validation(envs=env_names)
    all_passed = all(results.values())
    return all_passed, results


def main():
    """Command line interface for environment validation."""
    from tau_bench.envs import get_available_environments
    
    available_envs = get_available_environments()
    
    if len(sys.argv) > 1:
        env_name = sys.argv[1].lower()
        if env_name in available_envs:
            success = validate_environment(env_name)
            sys.exit(0 if success else 1)
        elif env_name == "all":
            all_passed, _ = validate_all_environments()
            sys.exit(0 if all_passed else 1)
        else:
            print(f"❌ Unknown environment: {env_name}")
            env_list = '|'.join(available_envs)
            print(f"   Usage: python validate_environments.py [{env_list}|all]")
            print("   Examples:")
            if available_envs:
                print(f"     python validate_environments.py {available_envs[0]}")
            print("     python validate_environments.py all")
            sys.exit(1)
    else:
        # Default: validate all environments
        all_passed, _ = validate_all_environments()
        sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()