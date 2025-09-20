# Copyright Sierra

"""
Domain initialization module.
Automatically discovers and registers built-in domains.
"""

from pathlib import Path
from tau_bench.domain_config import domain_registry


def initialize_builtin_domains():
    """Initialize built-in domains in the registry."""
    # Get the path to the envs directory
    envs_dir = Path(__file__).parent
    
    # Discover and register built-in domains
    domain_registry.discover_domains(envs_dir)


# Auto-initialize when this module is imported
initialize_builtin_domains()