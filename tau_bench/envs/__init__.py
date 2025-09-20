# Copyright Sierra

from pathlib import Path
from typing import Optional, Union
from tau_bench.envs.base import Env
from tau_bench.envs.user import UserStrategy
from tau_bench.domain_config import domain_registry, DomainConfig

# Initialize built-in domains
from tau_bench.envs import domain_init


def get_env(
    env_name: str,
    user_strategy: Union[str, UserStrategy],
    user_model: str,
    task_split: str,
    user_provider: Optional[str] = None,
    task_index: Optional[int] = None,
    domain_config_path: Optional[Union[str, Path]] = None,
) -> Env:
    """
    Get an environment instance. Supports both legacy hardcoded domains and new configurable domains.
    
    Args:
        env_name: Name of the environment (domain)
        user_strategy: User simulation strategy
        user_model: Model for user simulation
        task_split: Task split (train/test/dev)
        user_provider: Provider for user model
        task_index: Specific task index
        domain_config_path: Path to domain configuration file (for new configurable domains)
    
    Returns:
        Environment instance
    """
    # Try new configurable domain system first
    if domain_config_path:
        from tau_bench.envs.generic import GenericDomainEnv
        
        # Load domain config
        config = domain_registry.load_domain_from_file(domain_config_path)
        
        env = GenericDomainEnv(
            domain_config=config,
            user_strategy=user_strategy,
            user_model=user_model,
            user_provider=user_provider,
            task_split=task_split,
            task_index=task_index,
            config_base_path=Path(domain_config_path).parent,
        )
        env._domain_config_path = domain_config_path
        return env
    
    # Check if domain is already registered in the new system
    domain_config = domain_registry.get_domain(env_name)
    if domain_config:
        from tau_bench.envs.generic import GenericDomainEnv
        
        # Use stored config path if available
        config_path = getattr(domain_config, '_config_path', None)
        base_path = Path(config_path).parent if config_path else Path.cwd()
        
        env = GenericDomainEnv(
            domain_config=domain_config,
            user_strategy=user_strategy,
            user_model=user_model,
            user_provider=user_provider,
            task_split=task_split,
            task_index=task_index,
            config_base_path=base_path,
        )
        if config_path:
            env._domain_config_path = config_path
        return env
    
    # Fall back to legacy hardcoded domains for backward compatibility
    if env_name == "retail":
        from tau_bench.envs.retail import MockRetailDomainEnv

        return MockRetailDomainEnv(
            user_strategy=user_strategy,
            user_model=user_model,
            task_split=task_split,
            user_provider=user_provider,
            task_index=task_index,
        )
    elif env_name == "airline":
        from tau_bench.envs.airline import MockAirlineDomainEnv

        return MockAirlineDomainEnv(
            user_strategy=user_strategy,
            user_model=user_model,
            task_split=task_split,
            user_provider=user_provider,
            task_index=task_index,
        )
    else:
        raise ValueError(f"Unknown environment: {env_name}. Available legacy domains: retail, airline. Use domain_config_path for custom domains.")
