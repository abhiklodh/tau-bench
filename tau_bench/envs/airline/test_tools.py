"""
Airline environment task validation using simplified approach.

This module provides lightweight task validation using:
1. Syntactic checks via Python compiler
2. Semantic checks via automatic function invocation
"""

from tau_bench.task_validation import TaskValidator, print_validation_summary
from tau_bench.envs.airline.data import load_data
from tau_bench.envs.airline.tools import ALL_TOOLS
from tau_bench.envs.airline.tasks_test import TASKS


def run_airline_tests():
    """Run simplified airline task validation."""
    print("🔍 Loading airline environment data and tools...")
    
    try:
        # Load data and tools
        data = load_data()
        tools = ALL_TOOLS
        
        # Create task validator
        validator = TaskValidator(data, tools)
        
        print(f"📋 Validating {len(TASKS)} airline tasks...")
        
        # Validate tasks
        all_valid, summary = validator.validate_tasks(TASKS)
        
        # Print results
        print_validation_summary(summary, verbose=True)
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error during airline validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_airline_tests()
    exit(0 if success else 1)