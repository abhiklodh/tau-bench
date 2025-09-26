"""
Environment validation test runner using simplified task validation.

This module provides a simplified task validation approach that:
1. Uses syntactic checks via Python compiler for task actions
2. Uses semantic checks via automatic function invocation with database
"""

import sys
import traceback
from typing import Dict, List, Tuple


def run_environment_tests(env_names: List[str]) -> Dict[str, bool]:
    """
    Run simplified task validation for specified environments.
    
    Args:
        env_names: List of environment names to test ('healthcare', 'retail', 'airline')
        
    Returns:
        Dictionary mapping environment names to test success status
    """
    results = {}
    
    for env_name in env_names:
        print(f"\n{'='*60}")
        print(f"VALIDATING {env_name.upper()} ENVIRONMENT")
        print(f"{'='*60}")
        
        try:
            if env_name == "healthcare":
                from tau_bench.envs.healthcare.test_tools import run_healthcare_tests
                success = run_healthcare_tests()
            elif env_name == "retail":
                from tau_bench.envs.retail.test_tools import run_retail_tests
                success = run_retail_tests()
            elif env_name == "airline":
                from tau_bench.envs.airline.test_tools import run_airline_tests
                success = run_airline_tests()
            else:
                print(f"❌ Unknown environment: {env_name}")
                success = False
            
            results[env_name] = success
            
            if success:
                print(f"✅ {env_name.capitalize()} environment validation PASSED")
            else:
                print(f"❌ {env_name.capitalize()} environment validation FAILED")
                print(f"   Please fix the {env_name} environment issues before running model tests.")
                
        except ImportError as e:
            print(f"❌ Error importing {env_name} test module: {str(e)}")
            print(f"   Make sure test_tools.py exists in tau_bench/envs/{env_name}/")
            results[env_name] = False
        except Exception as e:
            print(f"❌ Unexpected error validating {env_name} environment: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            results[env_name] = False
    
    return results


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
    
    results = run_environment_tests([env_name])
    return results.get(env_name, False)


def validate_all_environments() -> Tuple[bool, Dict[str, bool]]:
    """
    Validate all available environments.
    
    Returns:
        Tuple of (all_passed, individual_results)
    """
    env_names = ["healthcare", "retail", "airline"]
    results = run_environment_tests(env_names)
    
    all_passed = all(results.values())
    
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    for env_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{env_name.capitalize():12}: {status}")
    
    if all_passed:
        print(f"\n🎉 Overall result: ✅ ALL ENVIRONMENTS PASSED")
        print("   All environments are ready for model testing!")
    else:
        failed_envs = [env for env, passed in results.items() if not passed]
        print(f"\n⚠️  Overall result: ❌ SOME ENVIRONMENTS FAILED")
        print(f"   Failed environments: {', '.join(failed_envs)}")
        print("   Please fix the issues above before running model tests.")
    
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