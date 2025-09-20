# Copyright Sierra

"""
Tests for the domain-agnostic tau-bench system.
"""

import unittest
import tempfile
import yaml
from pathlib import Path
from tau_bench.domain_config import DomainConfig, DomainRegistry, domain_registry
from tau_bench.envs.generic import GenericDomainEnv


class TestDomainConfig(unittest.TestCase):
    """Test domain configuration functionality."""
    
    def test_domain_config_creation(self):
        """Test creating a domain configuration."""
        config = DomainConfig(
            name="test_domain",
            display_name="Test Domain",
            description="A test domain",
            data_loader="test.data.load_data",
            wiki_file="test/wiki.md",
            rules_file="test.rules",
            tools=[],
            task_splits={"test": "test.tasks"},
        )
        
        self.assertEqual(config.name, "test_domain")
        self.assertEqual(config.display_name, "Test Domain")
        self.assertEqual(config.version, "1.0.0")  # default
    
    def test_domain_registry(self):
        """Test domain registry functionality."""
        registry = DomainRegistry()
        
        config = DomainConfig(
            name="test_registry",
            display_name="Test Registry Domain",
            description="A test domain for registry",
            data_loader="test.data.load_data",
            wiki_file="test/wiki.md",
            rules_file="test.rules",
            tools=[],
            task_splits={"test": "test.tasks"},
        )
        
        # Test registration
        registry.register_domain(config)
        self.assertIn("test_registry", registry.list_domains())
        
        # Test retrieval
        retrieved = registry.get_domain("test_registry")
        self.assertEqual(retrieved.name, "test_registry")
        
        # Test non-existent domain
        self.assertIsNone(registry.get_domain("non_existent"))
    
    def test_domain_config_file_loading(self):
        """Test loading domain configuration from file."""
        config_data = {
            "name": "test_file_domain",
            "display_name": "Test File Domain",
            "description": "A test domain loaded from file",
            "data_loader": "test.data.load_data",
            "wiki_file": "test/wiki.md",
            "rules_file": "test.rules",
            "tools": [],
            "task_splits": {"test": "test.tasks"},
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            registry = DomainRegistry()
            config = registry.load_domain_from_file(config_path)
            
            self.assertEqual(config.name, "test_file_domain")
            self.assertEqual(config.display_name, "Test File Domain")
            self.assertIn("test_file_domain", registry.list_domains())
        finally:
            Path(config_path).unlink()


class TestBuiltinDomains(unittest.TestCase):
    """Test built-in domain configurations."""
    
    def test_builtin_domains_discovered(self):
        """Test that built-in domains are discovered."""
        domains = domain_registry.list_domains()
        self.assertIn("retail", domains)
        self.assertIn("airline", domains)
    
    def test_retail_domain_config(self):
        """Test retail domain configuration."""
        config = domain_registry.get_domain("retail")
        self.assertIsNotNone(config)
        self.assertEqual(config.name, "retail")
        self.assertEqual(config.display_name, "Retail Customer Service")
        self.assertIn("transfer_to_human_agents", config.terminate_tools)
        self.assertTrue(len(config.tools) > 0)
        self.assertIn("test", config.task_splits)
    
    def test_airline_domain_config(self):
        """Test airline domain configuration."""
        config = domain_registry.get_domain("airline")
        self.assertIsNotNone(config)
        self.assertEqual(config.name, "airline")
        self.assertEqual(config.display_name, "Airline Customer Service")
        self.assertIn("transfer_to_human_agents", config.terminate_tools)
        self.assertTrue(len(config.tools) > 0)
        self.assertIn("test", config.task_splits)


class TestGenericEnvironment(unittest.TestCase):
    """Test generic domain environment."""
    
    def test_component_loading(self):
        """Test loading domain components without user initialization."""
        config = domain_registry.get_domain("retail")
        self.assertIsNotNone(config)
        
        # Create environment instance without full initialization
        env = GenericDomainEnv.__new__(GenericDomainEnv)
        env.domain_config = config
        env.config_base_path = Path.cwd()
        
        # Test data function loading
        data_func = env._load_data_function()
        self.assertIsNotNone(data_func)
        self.assertTrue(callable(data_func))
        
        # Test tools loading
        tools = env._load_tools()
        self.assertTrue(len(tools) > 0)
        self.assertTrue(all(hasattr(tool, 'get_info') for tool in tools))
        
        # Test tasks loading
        tasks = env._load_tasks('test')
        self.assertTrue(len(tasks) > 0)
        
        # Test wiki loading
        wiki = env._load_wiki()
        self.assertIsInstance(wiki, str)
        self.assertTrue(len(wiki) > 0)
        
        # Test rules loading
        rules = env._load_rules()
        self.assertIsInstance(rules, list)
        self.assertTrue(len(rules) > 0)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with legacy domains."""
    
    def test_legacy_domain_names(self):
        """Test that legacy domain names still work."""
        from tau_bench.envs import get_env
        
        # These should not raise errors even without API keys
        # (we're just testing that the factory function can create the environments)
        try:
            # Test without domain_config_path (legacy mode)
            env = get_env(
                "retail",
                user_strategy="llm",
                user_model="gpt-4o",
                task_split="test",
                user_provider="openai",
            )
            # This will fail due to missing API key, but that's expected
        except Exception as e:
            # Should fail on authentication, not on unknown environment
            self.assertNotIn("Unknown environment", str(e))
        
        try:
            env = get_env(
                "airline",
                user_strategy="llm", 
                user_model="gpt-4o",
                task_split="test",
                user_provider="openai",
            )
        except Exception as e:
            # Should fail on authentication, not on unknown environment
            self.assertNotIn("Unknown environment", str(e))


if __name__ == "__main__":
    unittest.main()