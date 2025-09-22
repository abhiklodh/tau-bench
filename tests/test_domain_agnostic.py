# Copyright Sierra

"""
Tests for the domain-agnostic tau-bench system.
"""

import unittest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from tau_bench.domain_config import DomainConfig, DomainRegistry, domain_registry
from tau_bench.envs.generic import GenericDomainEnv
from tau_bench.model_utils.model.bedrock import BedrockModel
from tau_bench.model_utils.model.general_model import model_factory
from tau_bench.model_utils.model.model import Platform
from tau_bench.model_utils.model.chat import Message, Role
from tau_bench.model_utils.api.datapoint import GenerateDatapoint


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


class TestBedrockModel(unittest.TestCase):
    """Test Bedrock model functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock boto3 to avoid requiring actual AWS credentials
        self.boto3_patcher = patch('boto3.client')
        self.mock_boto3_client = self.boto3_patcher.start()
        
        # Create mock client
        self.mock_client = Mock()
        self.mock_boto3_client.return_value = self.mock_client
        
    def tearDown(self):
        """Clean up test environment."""
        self.boto3_patcher.stop()
    
    def test_bedrock_model_initialization(self):
        """Test BedrockModel initialization."""
        model = BedrockModel(
            model="amazon.nova-pro-v1:0",
            region="us-east-1",
            temperature=0.5
        )
        
        self.assertEqual(model.model, "amazon.nova-pro-v1:0")
        self.assertEqual(model.region, "us-east-1")
        self.assertEqual(model.temperature, 0.5)
        
        # Verify boto3 client was called with correct parameters
        self.mock_boto3_client.assert_called_once_with(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
    
    def test_bedrock_model_with_custom_endpoint(self):
        """Test BedrockModel with custom endpoint URL."""
        model = BedrockModel(
            model="amazon.nova-lite-v1:0",
            endpoint_url="https://custom-bedrock-endpoint.com",
            region="us-west-2"
        )
        
        self.assertEqual(model.endpoint_url, "https://custom-bedrock-endpoint.com")
        self.assertEqual(model.region, "us-west-2")
        
        # Verify boto3 client was called with custom endpoint
        self.mock_boto3_client.assert_called_once_with(
            service_name='bedrock-runtime',
            region_name='us-west-2',
            endpoint_url='https://custom-bedrock-endpoint.com'
        )
    
    def test_model_factory_bedrock_platform(self):
        """Test model_factory with BEDROCK platform."""
        model = model_factory(
            model_id="amazon.nova-micro-v1:0",
            platform=Platform.BEDROCK,
            temperature=0.1
        )
        
        self.assertIsInstance(model, BedrockModel)
        self.assertEqual(model.model, "amazon.nova-micro-v1:0")
        self.assertEqual(model.temperature, 0.1)
    
    def test_get_capability_scoring(self):
        """Test capability scoring for different models."""
        # Test Amazon Nova Pro (high capability)
        model_pro = BedrockModel(model="amazon.nova-pro-v1:0")
        self.assertEqual(model_pro.get_capability(), 0.9)
        
        # Test Amazon Nova Micro (lower capability)
        model_micro = BedrockModel(model="amazon.nova-micro-v1:0")
        self.assertEqual(model_micro.get_capability(), 0.5)
        
        # Test Claude 3.5 Sonnet (highest capability)
        model_claude = BedrockModel(model="anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.assertEqual(model_claude.get_capability(), 1.0)
        
        # Test fallback for unknown model
        model_unknown = BedrockModel(model="unknown.model")
        self.assertEqual(model_unknown.get_capability(), 0.5)
    
    def test_message_conversion(self):
        """Test message conversion to Bedrock format."""
        model = BedrockModel(model="amazon.nova-pro-v1:0")
        
        messages = [
            Message(role=Role.SYSTEM, content="You are a helpful assistant."),
            Message(role=Role.USER, content="Hello, how are you?"),
            Message(role=Role.ASSISTANT, content="I'm doing well, thank you!")
        ]
        
        bedrock_format = model._convert_messages_to_bedrock_format(messages)
        
        # Verify structure
        self.assertIn("messages", bedrock_format)
        self.assertIn("system", bedrock_format)
        self.assertIn("max_tokens", bedrock_format)
        self.assertIn("temperature", bedrock_format)
        
        # Verify system message is separate
        self.assertEqual(len(bedrock_format["system"]), 1)
        self.assertEqual(bedrock_format["system"][0]["text"], "You are a helpful assistant.")
        
        # Verify conversation messages
        self.assertEqual(len(bedrock_format["messages"]), 2)
        self.assertEqual(bedrock_format["messages"][0]["role"], "user")
        self.assertEqual(bedrock_format["messages"][1]["role"], "assistant")


if __name__ == "__main__":
    unittest.main()