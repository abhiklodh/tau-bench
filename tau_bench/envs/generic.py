# Copyright Sierra

import importlib
import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict, List, Type, Optional, Union
from tau_bench.envs.base import Env
from tau_bench.envs.tool import Tool
from tau_bench.envs.user import UserStrategy
from tau_bench.domain_config import DomainConfig, domain_registry
from tau_bench.types import Task


class GenericDomainEnv(Env):
    """Generic domain environment that can be configured through DomainConfig."""
    
    def __init__(
        self,
        domain_config: Union[str, DomainConfig],
        user_strategy: Union[str, UserStrategy] = UserStrategy.LLM,
        user_model: str = "gpt-4o",
        user_provider: Optional[str] = None,
        task_split: str = "test",
        task_index: Optional[int] = None,
        config_base_path: Optional[Path] = None,
    ):
        # Load domain configuration
        if isinstance(domain_config, str):
            config = domain_registry.get_domain(domain_config)
            if config is None:
                raise ValueError(f"Domain '{domain_config}' not found in registry")
        else:
            config = domain_config
        
        self.domain_config = config
        self.config_base_path = config_base_path or Path.cwd()
        
        # Store domain config path if available
        self._domain_config_path = getattr(config, '_config_path', None)
        
        # Load domain components
        data_load_func = self._load_data_function()
        tools = self._load_tools()
        tasks = self._load_tasks(task_split)
        wiki = self._load_wiki()
        rules = self._load_rules()
        
        # Initialize base environment
        super().__init__(
            data_load_func=data_load_func,
            tools=tools,
            tasks=tasks,
            wiki=wiki,
            rules=rules,
            user_strategy=user_strategy,
            user_model=user_model,
            user_provider=user_provider,
            task_index=task_index,
        )
        
        # Set terminate tools
        self.terminate_tools = config.terminate_tools
    
    def _load_data_function(self) -> Callable[[], Dict[str, Any]]:
        """Load the data loading function from the configured module."""
        module_path = self.domain_config.data_loader
        
        # Try to import as a module path first
        try:
            module_name, func_name = module_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            return getattr(module, func_name)
        except (ValueError, ImportError, AttributeError):
            pass
        
        # Try to load as a file path
        try:
            file_path = self.config_base_path / module_path
            if file_path.exists():
                spec = importlib.util.spec_from_file_location("data_module", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Look for common function names
                for func_name in ['load_data', 'load', 'get_data']:
                    if hasattr(module, func_name):
                        return getattr(module, func_name)
        except Exception:
            pass
        
        raise ImportError(f"Could not load data function from: {module_path}")
    
    def _load_tools(self) -> List[Type[Tool]]:
        """Load tools from the configuration."""
        tools = []
        
        for tool_config in self.domain_config.tools:
            try:
                # Try to import as module path
                module = importlib.import_module(tool_config.module_path)
                tool_class = getattr(module, tool_config.class_name)
                tools.append(tool_class)
            except (ImportError, AttributeError):
                # Try to load as file path
                try:
                    file_path = self.config_base_path / tool_config.module_path
                    if file_path.exists():
                        spec = importlib.util.spec_from_file_location("tool_module", file_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        tool_class = getattr(module, tool_config.class_name)
                        tools.append(tool_class)
                    else:
                        print(f"Warning: Could not load tool {tool_config.name} from {tool_config.module_path}")
                except Exception as e:
                    print(f"Warning: Failed to load tool {tool_config.name}: {e}")
        
        return tools
    
    def _load_tasks(self, task_split: str) -> List[Task]:
        """Load tasks for the specified split."""
        if task_split not in self.domain_config.task_splits:
            raise ValueError(f"Task split '{task_split}' not available. Available splits: {list(self.domain_config.task_splits.keys())}")
        
        task_file = self.domain_config.task_splits[task_split]
        
        # Try to import as module path
        try:
            module = importlib.import_module(task_file)
            # Look for common task variable names
            for var_name in ['TASKS', 'TASKS_TEST', 'TASKS_TRAIN', 'TASKS_DEV', 'tasks']:
                if hasattr(module, var_name):
                    return getattr(module, var_name)
        except ImportError:
            pass
        
        # Try to load as file path
        try:
            file_path = self.config_base_path / task_file
            if file_path.exists():
                spec = importlib.util.spec_from_file_location("tasks_module", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Look for common task variable names
                for var_name in ['TASKS', 'TASKS_TEST', 'TASKS_TRAIN', 'TASKS_DEV', 'tasks']:
                    if hasattr(module, var_name):
                        return getattr(module, var_name)
        except Exception:
            pass
        
        raise ImportError(f"Could not load tasks from: {task_file}")
    
    def _load_wiki(self) -> str:
        """Load wiki content from the configured file."""
        wiki_file = self.domain_config.wiki_file
        
        # Try as absolute path first
        wiki_path = Path(wiki_file)
        if not wiki_path.is_absolute():
            wiki_path = self.config_base_path / wiki_file
        
        if wiki_path.exists():
            return wiki_path.read_text(encoding='utf-8')
        
        # Try as relative path from domain config location
        if hasattr(self, '_domain_config_path') and self._domain_config_path:
            config_dir = Path(self._domain_config_path).parent
            wiki_path = config_dir / wiki_file.split('/')[-1]  # Just filename
            if wiki_path.exists():
                return wiki_path.read_text(encoding='utf-8')
            
            # Try full relative path from config dir
            wiki_path = config_dir / wiki_file
            if wiki_path.exists():
                return wiki_path.read_text(encoding='utf-8')
        
        # Try to import as module
        try:
            module_path = wiki_file.replace('.py', '').replace('/', '.')
            module = importlib.import_module(module_path)
            # Look for common wiki variable names
            for var_name in ['WIKI', 'wiki', 'WIKI_CONTENT']:
                if hasattr(module, var_name):
                    return getattr(module, var_name)
        except ImportError:
            pass
        
        raise FileNotFoundError(f"Could not load wiki from: {wiki_file}")
    
    def _load_rules(self) -> List[str]:
        """Load rules from the configured file."""
        rules_file = self.domain_config.rules_file
        
        # Try to import as module path
        try:
            module_path = rules_file.replace('.py', '').replace('/', '.')
            module = importlib.import_module(module_path)
            # Look for common rules variable names
            for var_name in ['RULES', 'rules', 'RULE_LIST']:
                if hasattr(module, var_name):
                    return getattr(module, var_name)
        except ImportError:
            pass
        
        # Try to load as file path
        try:
            file_path = self.config_base_path / rules_file
            if file_path.exists():
                spec = importlib.util.spec_from_file_location("rules_module", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Look for common rules variable names
                for var_name in ['RULES', 'rules', 'RULE_LIST']:
                    if hasattr(module, var_name):
                        return getattr(module, var_name)
        except Exception:
            pass
        
        raise ImportError(f"Could not load rules from: {rules_file}")