#!/usr/bin/env python3
"""
Example demonstrating the generic task validation system.

This example shows how the new centralized validation system works
and eliminates the need for test_tools.py in each environment.
"""

from tau_bench.validation import TaskValidator
from tau_bench.types import Task, Action


def example_usage():
    """Example showing how to use the generic validation system."""
    
    # Step 1: Define your environment's data loader
    def my_data_loader():
        """Load or reset environment data."""
        return {
            "users": {"user123": {"name": "John"}},
            "orders": {},
            "state": "initial"
        }
    
    # Step 2: Define mock tools (in real env, these would be your actual tools)
    class ExampleTool:
        @staticmethod
        def invoke(data, **kwargs):
            # Simulate tool modifying environment data
            data["state"] = "modified"
            return "Tool executed successfully"
    
    # Step 3: Create tools mapping (same as in your env)
    tools_map = {
        "example_tool": ExampleTool,
        "another_tool": ExampleTool,
    }
    
    # Step 4: Initialize the validator
    validator = TaskValidator(
        data_load_func=my_data_loader,
        tools_map=tools_map,
        terminate_tools=["transfer_to_human_agents"]  # Tools that end episodes
    )
    
    # Step 5: Define a task to validate
    task = Task(
        user_id="user123",
        instruction="Complete this example task",
        actions=[
            Action(name="example_tool", kwargs={"param": "value"}),
            Action(name="respond", kwargs={"content": "Task completed with result: SUCCESS"})
        ],
        outputs=["SUCCESS"]  # Expected outputs to find in agent responses
    )
    
    # Step 6: Simulate agent actions
    agent_actions = [
        Action(name="example_tool", kwargs={"param": "value"}),
        Action(name="respond", kwargs={"content": "Task completed with result: SUCCESS"})
    ]
    
    # Step 7: Get current environment data state
    current_data = my_data_loader()
    current_data["state"] = "modified"  # Simulate the correct final state
    
    # Step 8: Validate the task
    result = validator.validate_task(
        task=task,
        agent_actions=agent_actions,
        current_data=current_data
    )
    
    # Step 9: Check results
    print(f"Validation Result:")
    print(f"  Reward: {result.reward}")
    print(f"  Info Type: {type(result.info).__name__}")
    
    if hasattr(result.info, 'outputs'):
        print(f"  Outputs Found: {result.info.outputs}")
    if hasattr(result.info, 'r_actions'):
        print(f"  Actions Correct: {result.info.r_actions}")
    
    return result.reward == 1.0


def main():
    """Run the example."""
    print("Generic Task Validation System Example")
    print("=" * 40)
    
    success = example_usage()
    
    print("\nKey Benefits:")
    print("✅ No test_tools.py needed in each environment")
    print("✅ Centralized validation logic in tau_bench.validation")
    print("✅ Works with any environment without modification")
    print("✅ Handles both syntactic (database) and semantic (output) validation")
    
    if success:
        print("\n🎉 Example completed successfully!")
    else:
        print("\n❌ Example failed - check your implementation")


if __name__ == "__main__":
    main()