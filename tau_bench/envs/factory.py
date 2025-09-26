# Copyright Sierra

import os
import importlib
import inspect
from typing import Dict, List, Type, Optional, Union
from tau_bench.envs.base import Env
from tau_bench.envs.user import UserStrategy


class EnvironmentFactory:
    """Factory for dynamically discovering and creating environment instances."""
    
    def __init__(self):
        self._env_registry: Dict[str, Type[Env]] = {}
        self._discover_environments()
    
    def _discover_environments(self) -> None:
        """Discover and register all available environments from the envs directory."""
        envs_dir = os.path.dirname(__file__)
        
        # Find all subdirectories that could be environments
        for item in os.listdir(envs_dir):
            item_path = os.path.join(envs_dir, item)
            
            # Skip non-directories and special directories
            if not os.path.isdir(item_path) or item.startswith('_'):
                continue
                
            # Check if it has an env.py file
            env_py_path = os.path.join(item_path, 'env.py')
            if not os.path.exists(env_py_path):
                continue
                
            try:
                # Import the environment module
                module_name = f'tau_bench.envs.{item}.env'
                module = importlib.import_module(module_name)
                
                # Find classes that inherit from Env
                env_class = None
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (obj is not Env and 
                        issubclass(obj, Env) and 
                        obj.__module__ == module_name):
                        env_class = obj
                        break
                
                if env_class:
                    self._env_registry[item] = env_class
                    
            except ImportError as e:
                # Log warning but continue with other environments
                print(f"Warning: Could not import environment '{item}': {e}")
                continue
    
    def get_available_environments(self) -> List[str]:
        """Get list of all available environment names."""
        return list(self._env_registry.keys())
    
    def create_env(
        self,
        env_name: str,
        user_strategy: Union[str, UserStrategy],
        user_model: str,
        task_split: str,
        user_provider: Optional[str] = None,
        task_index: Optional[int] = None,
    ) -> Env:
        """
        Create an environment instance.
        
        Args:
            env_name: Name of the environment to create
            user_strategy: User simulation strategy
            user_model: Model to use for user simulation
            task_split: Task split to use (test, train, dev)
            user_provider: Optional provider for user model
            task_index: Optional specific task index
            
        Returns:
            Environment instance
            
        Raises:
            ValueError: If environment is not found or cannot be created
        """
        if env_name not in self._env_registry:
            available_envs = ', '.join(self.get_available_environments())
            raise ValueError(
                f"Unknown environment: {env_name}. "
                f"Available environments: {available_envs}"
            )
        
        env_class = self._env_registry[env_name]
        
        try:
            return env_class(
                user_strategy=user_strategy,
                user_model=user_model,
                task_split=task_split,
                user_provider=user_provider,
                task_index=task_index,
            )
        except Exception as e:
            raise ValueError(f"Failed to create environment '{env_name}': {e}")


# Global factory instance
_factory = EnvironmentFactory()


def get_available_environments() -> List[str]:
    """Get list of all available environment names."""
    return _factory.get_available_environments()


def get_env(
    env_name: str,
    user_strategy: Union[str, UserStrategy],
    user_model: str,
    task_split: str,
    user_provider: Optional[str] = None,
    task_index: Optional[int] = None,
) -> Env:
    """
    Create an environment instance using the factory.
    
    This replaces the hardcoded environment creation with dynamic discovery.
    """
    return _factory.create_env(
        env_name=env_name,
        user_strategy=user_strategy,
        user_model=user_model,
        task_split=task_split,
        user_provider=user_provider,
        task_index=task_index,
    )