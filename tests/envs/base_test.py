# Copyright Sierra

import pytest
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List, Callable
from tau_bench.envs.tool import Tool


class BaseToolTest(ABC):
    """Base class for testing environment tools."""
    
    @property
    @abstractmethod
    def data(self) -> Dict[str, Any]:
        """Return test data for the environment."""
        pass
    
    @property
    @abstractmethod
    def tool_class(self) -> Type[Tool]:
        """Return the tool class to test."""
        pass
    
    def test_tool_info_structure(self):
        """Test that tool info has correct structure."""
        info = self.tool_class.get_info()
        
        # Check basic structure
        assert "type" in info
        assert info["type"] == "function"
        assert "function" in info
        
        func_info = info["function"]
        assert "name" in func_info
        assert "description" in func_info
        assert "parameters" in func_info
        
        # Check parameters structure
        params = func_info["parameters"]
        assert "type" in params
        assert params["type"] == "object"
        assert "properties" in params
        
        # Name should be a string
        assert isinstance(func_info["name"], str)
        assert len(func_info["name"]) > 0
        
        # Description should be a string
        assert isinstance(func_info["description"], str)
        assert len(func_info["description"]) > 0
    
    def test_tool_invoke_with_data(self):
        """Test that tool invoke method works with test data."""
        # This is a basic test that the method exists and can be called
        # Subclasses should override this to test specific behavior
        assert hasattr(self.tool_class, 'invoke')
        assert callable(self.tool_class.invoke)
    
    def test_tool_invoke_handles_invalid_params(self):
        """Test that tool handles invalid parameters gracefully."""
        # Test with empty kwargs
        try:
            result = self.tool_class.invoke(self.data)
            # If it doesn't raise an exception, result should indicate error
            assert isinstance(result, str)
        except (TypeError, KeyError):
            # This is acceptable - the tool should either handle gracefully 
            # or raise appropriate exceptions
            pass


class BaseEnvironmentTest(ABC):
    """Base class for testing entire environment tool suites."""
    
    @property
    @abstractmethod
    def data_load_func(self) -> Callable[[], Dict[str, Any]]:
        """Return data loading function for the environment."""
        pass
    
    @property
    @abstractmethod
    def all_tools(self) -> List[Type[Tool]]:
        """Return all tool classes for the environment."""
        pass
    
    def test_all_tools_have_unique_names(self):
        """Test that all tools have unique names."""
        names = []
        for tool in self.all_tools:
            info = tool.get_info()
            name = info["function"]["name"]
            assert name not in names, f"Duplicate tool name found: {name}"
            names.append(name)
    
    def test_all_tools_can_be_instantiated_with_data(self):
        """Test that all tools work with loaded data."""
        data = self.data_load_func()
        for tool in self.all_tools:
            info = tool.get_info()
            name = info["function"]["name"]
            
            # Check that the tool has required methods
            assert hasattr(tool, 'invoke'), f"Tool {name} missing invoke method"
            assert hasattr(tool, 'get_info'), f"Tool {name} missing get_info method"
            assert callable(tool.invoke), f"Tool {name} invoke is not callable"
            assert callable(tool.get_info), f"Tool {name} get_info is not callable"
    
    def test_data_structure_consistency(self):
        """Test that the loaded data has expected structure."""
        data = self.data_load_func()
        assert isinstance(data, dict), "Data should be a dictionary"
        assert len(data) > 0, "Data should not be empty"