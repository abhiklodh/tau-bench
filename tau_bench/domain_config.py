# Copyright Sierra

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Callable
from pathlib import Path
import yaml
import json
from enum import Enum


class TaskSplit(str, Enum):
    TRAIN = "train"
    TEST = "test"
    DEV = "dev"


class ToolConfig(BaseModel):
    """Configuration for a domain tool."""
    name: str
    module_path: str
    class_name: str
    description: Optional[str] = None


class DomainConfig(BaseModel):
    """Configuration schema for a domain."""
    name: str
    display_name: str
    description: str
    version: str = "1.0.0"
    
    # Core components
    data_loader: str = Field(description="Module path to data loading function")
    wiki_file: str = Field(description="Path to wiki markdown file")
    rules_file: str = Field(description="Path to rules Python file")
    
    # Tools configuration
    tools: List[ToolConfig] = Field(description="List of available tools")
    
    # Task configuration
    task_splits: Dict[TaskSplit, str] = Field(
        description="Mapping of task splits to their file paths"
    )
    
    # Termination tools (optional)
    terminate_tools: List[str] = Field(
        default=[], 
        description="List of tool names that terminate the episode"
    )
    
    # Domain-specific settings
    settings: Dict[str, Any] = Field(
        default={}, 
        description="Domain-specific configuration settings"
    )


class DomainRegistry:
    """Registry for managing domain configurations."""
    
    def __init__(self):
        self._domains: Dict[str, DomainConfig] = {}
        self._domain_paths: Dict[str, Path] = {}
    
    def register_domain(self, config: DomainConfig, config_path: Optional[Path] = None):
        """Register a domain configuration."""
        self._domains[config.name] = config
        if config_path:
            self._domain_paths[config.name] = config_path
    
    def get_domain(self, name: str) -> Optional[DomainConfig]:
        """Get a domain configuration by name."""
        return self._domains.get(name)
    
    def list_domains(self) -> List[str]:
        """List all registered domain names."""
        return list(self._domains.keys())
    
    def load_domain_from_file(self, config_path: Union[str, Path]) -> DomainConfig:
        """Load domain configuration from YAML or JSON file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Domain config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        
        config = DomainConfig(**data)
        config._config_path = config_path  # Store the config path
        self.register_domain(config, config_path)
        return config
    
    def discover_domains(self, domains_dir: Union[str, Path]) -> List[DomainConfig]:
        """Discover and load all domain configurations from a directory."""
        domains_dir = Path(domains_dir)
        discovered_configs = []
        
        if not domains_dir.exists():
            return discovered_configs
        
        # Look for domain config files
        for config_file in domains_dir.rglob("domain.yaml"):
            try:
                config = self.load_domain_from_file(config_file)
                discovered_configs.append(config)
            except Exception as e:
                print(f"Warning: Failed to load domain config {config_file}: {e}")
        
        for config_file in domains_dir.rglob("domain.yml"):
            try:
                config = self.load_domain_from_file(config_file)
                discovered_configs.append(config)
            except Exception as e:
                print(f"Warning: Failed to load domain config {config_file}: {e}")
                
        for config_file in domains_dir.rglob("domain.json"):
            try:
                config = self.load_domain_from_file(config_file)
                discovered_configs.append(config)
            except Exception as e:
                print(f"Warning: Failed to load domain config {config_file}: {e}")
        
        return discovered_configs


# Global domain registry instance
domain_registry = DomainRegistry()