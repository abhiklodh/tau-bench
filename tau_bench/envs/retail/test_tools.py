"""
Retail environment task validation using simplified approach.

This module provides lightweight task validation using:
1. Syntactic checks via Python compiler
2. Semantic checks via automatic function invocation
"""

from tau_bench.task_validation import TaskValidator, print_validation_summary
from tau_bench.envs.retail.data import load_data
from tau_bench.envs.retail.tools import ALL_TOOLS
from tau_bench.envs.retail.tasks_test import TASKS_TEST


def run_retail_tests():
    """Run simplified retail task validation."""
    print("🔍 Loading retail environment data and tools...")
    
    try:
        # Load data and tools
        data = load_data()
        tools = ALL_TOOLS
        
        # Create task validator
        validator = TaskValidator(data, tools)
        
        print(f"📋 Validating {len(TASKS_TEST)} retail tasks...")
        
        # Validate tasks
        all_valid, summary = validator.validate_tasks(TASKS_TEST)
        
        # Print results
        print_validation_summary(summary, verbose=True)
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error during retail validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_retail_tests()
    exit(0 if success else 1)