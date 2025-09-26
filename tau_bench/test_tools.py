"""
Generic environment-agnostic task validation for all tau-bench environments.

This module provides a unified validation approach that can work with any environment:
1. Syntactic checks via Python compiler for task actions
2. Semantic checks via automatic function invocation with environment data
"""

import argparse
import sys
from typing import Dict, List, Any, Optional
from tau_bench.task_validation import TaskValidator, print_validation_summary


def get_environment_data(env_name: str, task_split: str = "test") -> tuple[Any, List[Any], List[Any]]:
    """
    Load data, tools, and tasks for a specific environment using the factory pattern.
    
    Args:
        env_name: Name of the environment (dynamically discovered)
        task_split: Task split to load ('test', 'train', 'dev')
        
    Returns:
        Tuple of (data, tools, tasks)
    """
    from tau_bench.envs import get_env
    
    try:
        # Create a temporary environment instance to get its data, tools, and tasks
        # Use 'human' user strategy to avoid API key requirements during validation
        env = get_env(env_name, 'human', 'gpt-4o', task_split)
        
        # Extract the components from the environment
        data = env.data
        tools = list(env.tools_map.values())  # Convert tools_map values to list
        tasks = env.tasks
        
        return data, tools, tasks
        
    except Exception as e:
        # Provide helpful error message with available environments
        from tau_bench.envs import get_available_environments
        available_envs = ', '.join(get_available_environments())
        raise ValueError(f"Failed to load environment '{env_name}': {e}. Available environments: {available_envs}")


def run_environment_validation(
    env_name: str, 
    task_split: str = "test",
    max_tasks: Optional[int] = None,
    skip_semantics: bool = False,
    verbose: bool = True
) -> bool:
    """
    Run task validation for a specific environment.
    
    Args:
        env_name: Name of the environment to validate
        task_split: Task split to validate
        max_tasks: Maximum number of tasks to validate (None for all)
        skip_semantics: Skip semantic validation (syntax only)
        verbose: Print detailed results
        
    Returns:
        True if all validations pass, False otherwise
    """
    print(f"🔍 Loading {env_name} environment data and tools...")
    
    try:
        data, tools, tasks = get_environment_data(env_name, task_split)
        
        # Limit tasks if requested
        if max_tasks and max_tasks < len(tasks):
            tasks = tasks[:max_tasks]
            print(f"📋 Validating {len(tasks)} {env_name} tasks (limited from {len(get_environment_data(env_name, task_split)[2])} total)...")
        else:
            print(f"📋 Validating {len(tasks)} {env_name} tasks...")
        
        # Create task validator
        validator = TaskValidator(data, tools)
        
        # Validate tasks
        all_valid, summary = validator.validate_tasks(tasks, skip_semantics=skip_semantics)
        
        # Print results
        print_validation_summary(summary, verbose=verbose)
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error during {env_name} validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_environments_validation(
    task_split: str = "test",
    max_tasks: Optional[int] = None,
    skip_semantics: bool = False,
    verbose: bool = True,
    envs: Optional[List[str]] = None
) -> Dict[str, bool]:
    """
    Run validation for all or specified environments.
    
    Args:
        task_split: Task split to validate
        max_tasks: Maximum number of tasks per environment
        skip_semantics: Skip semantic validation
        verbose: Print detailed results
        envs: List of environment names to validate (None for all)
        
    Returns:
        Dictionary mapping environment names to validation results
    """
    from tau_bench.envs import get_available_environments
    env_names = envs or get_available_environments()
    results = {}
    
    for env_name in env_names:
        print(f"\n{'='*60}")
        print(f"VALIDATING {env_name.upper()} ENVIRONMENT")
        print(f"{'='*60}")
        
        success = run_environment_validation(
            env_name, 
            task_split=task_split,
            max_tasks=max_tasks,
            skip_semantics=skip_semantics,
            verbose=verbose
        )
        
        results[env_name] = success
        
        if success:
            print(f"✅ {env_name.capitalize()} environment validation PASSED")
        else:
            print(f"❌ {env_name.capitalize()} environment validation FAILED")
    
    # Print summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    for env_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{env_name.capitalize():12}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print(f"\n🎉 Overall result: ✅ ALL ENVIRONMENTS PASSED")
        print("   All environments are ready for model testing!")
    else:
        failed_envs = [env for env, passed in results.items() if not passed]
        print(f"\n⚠️  Overall result: ❌ SOME ENVIRONMENTS FAILED")
        print(f"   Failed environments: {', '.join(failed_envs)}")
        print("   Please fix the issues above before running model tests.")
    
    return results


def main():
    """Command line interface for generic environment validation."""
    from tau_bench.envs import get_available_environments
    
    # Get available environments dynamically
    available_envs = get_available_environments()
    env_choices = available_envs + ["all"]
    
    parser = argparse.ArgumentParser(
        description="Generic task validation for tau-bench environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python -m tau_bench.test_tools                    # Validate all environments
  python -m tau_bench.test_tools {available_envs[0] if available_envs else 'env_name'}         # Validate {available_envs[0] if available_envs else 'environment'} only
  python -m tau_bench.test_tools --env {available_envs[1] if len(available_envs) > 1 else (available_envs[0] if available_envs else 'env_name')}       # Validate {available_envs[1] if len(available_envs) > 1 else (available_envs[0] if available_envs else 'environment')} only
  python -m tau_bench.test_tools --max-tasks 10     # Limit to 10 tasks per env
  python -m tau_bench.test_tools --skip-semantics   # Syntax validation only
  python -m tau_bench.test_tools --task-split train # Use training tasks
        """
    )
    
    parser.add_argument(
        "environment",
        nargs="?",
        choices=env_choices,
        default="all",
        help="Environment to validate (default: all)"
    )
    
    parser.add_argument(
        "--env",
        choices=available_envs,
        help="Alternative way to specify environment"
    )
    
    parser.add_argument(
        "--task-split",
        default="test",
        choices=["test", "train", "dev"],
        help="Task split to validate (default: test)"
    )
    
    parser.add_argument(
        "--max-tasks",
        type=int,
        help="Maximum number of tasks to validate per environment"
    )
    
    parser.add_argument(
        "--skip-semantics",
        action="store_true",
        help="Skip semantic validation (syntax only)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Print detailed validation results (default: True)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    args = parser.parse_args()
    
    # Handle environment selection
    env_name = args.env or args.environment
    verbose = args.verbose and not args.quiet
    
    if env_name == "all":
        results = run_all_environments_validation(
            task_split=args.task_split,
            max_tasks=args.max_tasks,
            skip_semantics=args.skip_semantics,
            verbose=verbose
        )
        success = all(results.values())
    else:
        success = run_environment_validation(
            env_name,
            task_split=args.task_split,
            max_tasks=args.max_tasks,
            skip_semantics=args.skip_semantics,
            verbose=verbose
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()