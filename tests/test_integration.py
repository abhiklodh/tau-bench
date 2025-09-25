# Copyright Sierra

"""
Integration tests for tau_bench environments.

These tests validate that environments work correctly with their full
tool suites and that tools integrate properly with the environment data.
"""

import pytest
from tau_bench.envs import get_env
from tau_bench.envs.user import UserStrategy


class TestEnvironmentIntegration:
    """Test integration between environments, tools, and data."""
    
    @pytest.mark.parametrize("env_name", ["retail", "airline"])
    def test_environment_initialization(self, env_name):
        """Test that environments can be initialized correctly."""
        env = get_env(
            env_name=env_name,
            user_strategy=UserStrategy.HUMAN,
            user_model="gpt-4o",
            
            
            task_split="test",
            task_index=0
        )
        
        # Check that environment has required attributes
        assert hasattr(env, 'data')
        assert hasattr(env, 'tools_map')
        assert hasattr(env, 'tools_info')
        assert hasattr(env, 'tasks')
        assert hasattr(env, 'task')
        
        # Check data is loaded
        assert len(env.data) > 0
        assert len(env.tools_map) > 0
        assert len(env.tools_info) > 0
        assert len(env.tasks) > 0
        
        # Check current task is set
        assert env.task is not None
    
    @pytest.mark.parametrize("env_name", ["retail", "airline"])
    def test_all_tools_work_with_env_data(self, env_name):
        """Test that all tools work with the environment's loaded data."""
        env = get_env(
            env_name=env_name,
            user_strategy=UserStrategy.HUMAN,
            user_model="gpt-4o",
            
            
            task_split="test",
            task_index=0
        )
        
        # Test each tool with environment data
        for tool_name, tool_class in env.tools_map.items():
            # Get tool info to understand required parameters
            tool_info = tool_class.get_info()
            params = tool_info["function"]["parameters"]
            required_params = params.get("required", [])
            
            # Skip tools that require specific parameters we can't easily generate
            # These are tested individually in their specific test files
            if required_params and any(param not in ["data"] for param in required_params):
                continue
                
            # Test tools that don't require parameters or only need data
            if not required_params or (len(required_params) == 1 and "data" in required_params):
                try:
                    result = tool_class.invoke(env.data)
                    assert isinstance(result, str), f"Tool {tool_name} should return a string"
                except TypeError:
                    # Tool might not accept just data parameter - this is fine
                    pass
    
    @pytest.mark.parametrize("env_name,expected_tools", [
        ("retail", 16),
        ("airline", 14)  
    ])
    def test_expected_tool_counts(self, env_name, expected_tools):
        """Test that environments have expected number of tools."""
        env = get_env(
            env_name=env_name,
            user_strategy=UserStrategy.HUMAN,
            user_model="gpt-4o", 
            task_split="test",
            task_index=0
        )
        
        assert len(env.tools_map) == expected_tools
        assert len(env.tools_info) == expected_tools
    
    def test_retail_specific_integration(self):
        """Test retail-specific integrations."""
        env = get_env(
            env_name="retail",
            user_strategy=UserStrategy.HUMAN,
            user_model="gpt-4o",
            
            task_split="test",
            task_index=0
        )
        
        # Test that retail data has expected structure
        assert "users" in env.data
        assert "orders" in env.data  
        assert "products" in env.data
        
        # Test that retail-specific tools are present
        retail_tools = {
            "get_user_details", "get_order_details", "get_product_details",
            "find_user_id_by_name_zip", "find_user_id_by_email",
            "list_all_product_types", "cancel_pending_order"
        }
        
        env_tool_names = set(env.tools_map.keys())
        assert retail_tools.issubset(env_tool_names)
    
    def test_airline_specific_integration(self):
        """Test airline-specific integrations.""" 
        env = get_env(
            env_name="airline",
            user_strategy=UserStrategy.HUMAN,
            user_model="gpt-4o",
            
            task_split="test", 
            task_index=0
        )
        
        # Test that airline data has expected structure
        assert "users" in env.data
        assert "reservations" in env.data
        assert "flights" in env.data
        
        # Test that airline-specific tools are present
        airline_tools = {
            "get_user_details", "get_reservation_details", 
            "search_direct_flight", "search_onestop_flight",
            "list_all_airports", "book_reservation"
        }
        
        env_tool_names = set(env.tools_map.keys())
        assert airline_tools.issubset(env_tool_names)
    
    @pytest.mark.parametrize("env_name,task_split", [
        ("retail", "test"),
        ("retail", "dev"),
        ("retail", "train"),
        ("airline", "test")
    ])
    def test_task_splits(self, env_name, task_split):
        """Test that different task splits work correctly."""
        try:
            env = get_env(
                env_name=env_name,
                user_strategy=UserStrategy.HUMAN,
                user_model="gpt-4o",
            
                task_split=task_split,
                task_index=0
            )
            
            # Should have tasks
            assert len(env.tasks) > 0
            assert env.task is not None
            
        except ValueError as e:
            # Some task splits might not exist for some environments
            if "Unknown task split" in str(e):
                pytest.skip(f"Task split {task_split} not available for {env_name}")
            else:
                raise
    
    def test_data_consistency_across_tools(self):
        """Test that data remains consistent when used by multiple tools."""
        env = get_env(
            env_name="retail",
            user_strategy=UserStrategy.HUMAN,
            user_model="gpt-4o",
            
            task_split="test",
            task_index=0
        )
        
        # Get original data hash
        original_hash = env.get_data_hash()
        
        # Use several tools (that don't modify data)
        if "get_user_details" in env.tools_map:
            # Get first user
            user_id = next(iter(env.data["users"].keys()))
            env.tools_map["get_user_details"].invoke(env.data, user_id=user_id)
        
        if "list_all_product_types" in env.tools_map:
            env.tools_map["list_all_product_types"].invoke(env.data)
        
        # Data hash should remain the same
        new_hash = env.get_data_hash()
        assert original_hash == new_hash, "Data should not be modified by read-only tools"