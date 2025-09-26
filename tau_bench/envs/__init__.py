# Copyright Sierra

from typing import Optional, Union
from tau_bench.envs.base import Env
from tau_bench.envs.user import UserStrategy
from tau_bench.envs.factory import get_env as factory_get_env, get_available_environments


def get_env(
    env_name: str,
    user_strategy: Union[str, UserStrategy],
    user_model: str,
    task_split: str,
    user_provider: Optional[str] = None,
    task_index: Optional[int] = None,
) -> Env:
    """
    Create an environment instance using dynamic discovery.
    
    This function now uses a factory pattern to discover and instantiate
    environments dynamically from the tau_bench/envs directory.
    """
    return factory_get_env(
        env_name=env_name,
        user_strategy=user_strategy,
        user_model=user_model,
        task_split=task_split,
        user_provider=user_provider,
        task_index=task_index,
    )
