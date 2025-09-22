# Copyright Sierra

import os
import importlib
from typing import Optional, Union, List
from tau_bench.envs.base import Env
from tau_bench.envs.user import UserStrategy


def _discover_environments() -> List[str]:
    """Discover available environments by scanning the envs directory."""
    envs_dir = os.path.dirname(__file__)
    env_names = []
    
    for item in os.listdir(envs_dir):
        item_path = os.path.join(envs_dir, item)
        if (os.path.isdir(item_path) and 
            not item.startswith('_') and 
            item not in ['__pycache__'] and
            os.path.exists(os.path.join(item_path, '__init__.py')) and
            os.path.exists(os.path.join(item_path, 'env.py'))):
            env_names.append(item)
    
    return sorted(env_names)


def get_available_environments() -> List[str]:
    """Get list of available environment names."""
    return _discover_environments()


def get_env(
    env_name: str,
    user_strategy: Union[str, UserStrategy],
    user_model: str,
    task_split: str,
    user_provider: Optional[str] = None,
    task_index: Optional[int] = None,
) -> Env:
    """Create an environment instance using the factory pattern."""
    available_envs = get_available_environments()
    
    if env_name not in available_envs:
        raise ValueError(f"Unknown environment: {env_name}. Available environments: {available_envs}")
    
    try:
        # Dynamically import the environment module
        env_module = importlib.import_module(f'tau_bench.envs.{env_name}')
        
        # Find the environment class by looking for classes that end with 'Env' and inherit from Env
        env_class = None
        for attr_name in dir(env_module):
            attr = getattr(env_module, attr_name)
            if (isinstance(attr, type) and 
                attr_name.endswith('Env') and 
                issubclass(attr, Env) and 
                attr != Env):
                env_class = attr
                break
        
        if env_class is None:
            raise ValueError(f"Could not find environment class in {env_name} module")
        
        return env_class(
            user_strategy=user_strategy,
            user_model=user_model,
            task_split=task_split,
            user_provider=user_provider,
            task_index=task_index,
        )
        
    except ImportError as e:
        raise ValueError(f"Failed to import environment '{env_name}': {e}")
    except Exception as e:
        raise ValueError(f"Failed to create environment '{env_name}': {e}")
