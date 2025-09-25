#!/usr/bin/env python3
# Copyright Sierra

"""
Example script demonstrating how to use the Tau-Bench API service.

This script shows various ways to interact with the API, including:
1. Basic task validation
2. Comparing multiple models
3. Listing available tasks
4. Using different environments and configurations
"""

import asyncio
import json
from tau_bench.api.client import TauBenchAPIClient, quick_validate, validate_with_comparison


async def example_basic_validation():
    """Example 1: Basic task validation"""
    print("🔍 Example 1: Basic Task Validation")
    print("=" * 50)
    
    try:
        # Initialize client
        client = TauBenchAPIClient(base_url="http://localhost:8000")
        
        # Check service health first
        health = client.health_check()
        print(f"✅ Service Status: {health.status}")
        print(f"📅 Version: {health.version}")
        
        # Validate tasks with GPT-4o in retail environment
        response = client.validate_tasks(
            model_provider="openai",
            model="gpt-4o",
            env="retail",
            num_trials=2,
            max_concurrency=2,
            start_index=0,
            end_index=5  # Run first 5 tasks only
        )
        
        print(f"\n📊 Validation Results:")
        print(f"   Status: {response.status}")
        print(f"   Total Tasks: {response.metrics.total_tasks}")
        print(f"   Success Rate: {response.metrics.success_rate:.2%}")
        print(f"   Average Reward: {response.metrics.average_reward:.3f}")
        print(f"   Execution Time: {response.execution_time_seconds:.2f}s")
        
        # Show individual results
        print(f"\n📋 Individual Task Results:")
        for i, result in enumerate(response.results[:3]):  # Show first 3
            status = "✅" if result.success else "❌"
            print(f"   Task {result.task_id}: {status} Reward: {result.reward:.3f}")
            if i >= 2:
                break
        
        if len(response.results) > 3:
            print(f"   ... and {len(response.results) - 3} more tasks")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_model_comparison():
    """Example 2: Compare multiple models"""
    print("\n🆚 Example 2: Model Comparison")
    print("=" * 50)
    
    try:
        models_to_compare = [
            {"provider": "openai", "model": "gpt-4o"},
            {"provider": "openai", "model": "gpt-4o-mini"},
        ]
        
        results = validate_with_comparison(
            models=models_to_compare,
            env="airline",
            num_trials=1,
            start_index=0,
            end_index=3  # Run first 3 tasks only for comparison
        )
        
        print(f"📊 Comparison Results:")
        for i, result in enumerate(results):
            model_info = models_to_compare[i]
            print(f"\n🤖 {model_info['model']} ({model_info['provider']}):")
            print(f"   Success Rate: {result.metrics.success_rate:.2%}")
            print(f"   Average Reward: {result.metrics.average_reward:.3f}")
            print(f"   Execution Time: {result.execution_time_seconds:.2f}s")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_list_tasks():
    """Example 3: List available tasks"""
    print("\n📋 Example 3: List Available Tasks")
    print("=" * 50)
    
    try:
        client = TauBenchAPIClient(base_url="http://localhost:8000")
        
        # List tasks for different environments
        environments = ["retail", "airline", "healthcare"]
        
        for env in environments:
            tasks = client.list_tasks(env=env, task_split="test")
            print(f"\n🏢 {env.title()} Environment:")
            print(f"   Total Tasks: {tasks.total_tasks}")
            
            # Show first few tasks
            for i, task in enumerate(tasks.tasks[:2]):  # Show first 2 tasks
                print(f"   Task {task['task_id']}: {task['instruction_preview']}")
                if i >= 1:
                    break
                    
            if tasks.total_tasks > 2:
                print(f"   ... and {tasks.total_tasks - 2} more tasks")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_quick_validation():
    """Example 4: Quick validation using convenience function"""
    print("\n⚡ Example 4: Quick Validation")
    print("=" * 50)
    
    try:
        # Quick validation with minimal parameters
        result = quick_validate(
            model_provider="openai",
            model="gpt-4o-mini",
            env="healthcare",
            num_trials=1,
            end_index=2  # Run only first 2 tasks
        )
        
        print(f"📊 Quick Validation Results:")
        print(f"   Environment: {result.config_used['env']}")
        print(f"   Model: {result.config_used['model']}")
        print(f"   Success Rate: {result.metrics.success_rate:.2%}")
        print(f"   Average Reward: {result.metrics.average_reward:.3f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_advanced_configuration():
    """Example 5: Advanced configuration options"""
    print("\n⚙️ Example 5: Advanced Configuration")
    print("=" * 50)
    
    try:
        client = TauBenchAPIClient(base_url="http://localhost:8000")
        
        # Advanced validation with custom settings
        response = client.validate_tasks(
            model_provider="openai",
            model="gpt-4o",
            env="retail",
            num_trials=2,
            agent_strategy="react",  # Use ReAct strategy instead of tool-calling
            temperature=0.1,  # Add some randomness
            shuffle=True,  # Shuffle task order
            max_concurrency=3,  # Higher concurrency
            seed=42,  # Different seed for reproducibility
            start_index=0,
            end_index=3
        )
        
        print(f"📊 Advanced Configuration Results:")
        print(f"   Agent Strategy: {response.config_used['agent_strategy']}")
        print(f"   Temperature: {response.config_used['temperature']}")
        print(f"   Shuffle: {response.config_used['shuffle']}")
        print(f"   Success Rate: {response.metrics.success_rate:.2%}")
        print(f"   Execution Time: {response.execution_time_seconds:.2f}s")
        
        # Check if there were any errors or warnings
        if response.errors:
            print(f"⚠️ Errors: {response.errors}")
        if response.warnings:
            print(f"🔔 Warnings: {response.warnings}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all examples"""
    print("🚀 Tau-Bench API Examples")
    print("=" * 50)
    print("Make sure the API server is running: tau-bench-server")
    print("Or manually: python -m tau_bench.api.app")
    print()
    
    examples = [
        example_basic_validation,
        example_model_comparison,
        example_list_tasks,
        example_quick_validation,
        example_advanced_configuration,
    ]
    
    for example_func in examples:
        try:
            await example_func()
            print("\n" + "="*50)
        except KeyboardInterrupt:
            print("\n❌ Examples interrupted by user")
            break
        except Exception as e:
            print(f"❌ Example failed: {e}")
            continue
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())