# Creating Custom Domains in Tau-Bench

This guide explains how to create custom domains for tau-bench, making it possible to benchmark agents in virtually any domain.

## Overview

Tau-bench now supports domain-agnostic operation through configuration files. You can create new domains by defining:
- Domain configuration (YAML/JSON)
- Tools for the domain
- Data loading functions
- Wiki/knowledge base
- Domain rules
- Task definitions

## Domain Configuration Schema

Create a `domain.yaml` file with the following structure:

```yaml
name: your_domain_name
display_name: "Human Readable Domain Name"
description: "Description of what this domain covers"
version: "1.0.0"

# Core components
data_loader: "path.to.data.load_function"
wiki_file: "path/to/wiki.md"
rules_file: "path.to.rules.module"

# Tools configuration
tools:
  - name: "tool_name"
    module_path: "path.to.tool.module"
    class_name: "ToolClassName"
    description: "What this tool does"

# Task configuration
task_splits:
  test: "path.to.test.tasks"
  train: "path.to.train.tasks"  # optional
  dev: "path.to.dev.tasks"      # optional

# Termination tools (optional)
terminate_tools:
  - "tool_that_ends_conversation"

# Domain-specific settings (optional)
settings:
  max_conversation_turns: 30
  custom_setting: "value"
```

## Step-by-Step Domain Creation

### 1. Create Domain Directory Structure

```
your_domain/
├── domain.yaml           # Main configuration
├── wiki.md              # Knowledge base
├── rules.py              # Domain rules
├── data/
│   └── __init__.py       # Data loading function
├── tools/
│   ├── tool1.py          # Individual tool files
│   ├── tool2.py
│   └── ...
└── tasks.py              # Task definitions
```

### 2. Define Tools

Each tool must inherit from `tau_bench.envs.tool.Tool`:

```python
from tau_bench.envs.tool import Tool
from typing import Dict, Any

class YourTool(Tool):
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "your_tool_name",
                "description": "What your tool does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Parameter description"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], param1: str) -> str:
        """Tool implementation."""
        # Your tool logic here
        return "Tool response"
```

### 3. Create Data Loader

In your data module, define a `load_data()` function:

```python
def load_data():
    """Load domain-specific data."""
    return {
        "entities": {...},
        "relationships": {...},
        # Your domain data structure
    }
```

### 4. Define Tasks

Tasks follow the existing tau-bench format:

```python
from tau_bench.types import Task, Action

TASKS = [
    Task(
        user_id="user_001",
        instruction="Task instruction for the user simulator",
        actions=[
            Action(
                name="tool_name",
                kwargs={"param": "value"}
            )
        ],
        outputs=["expected", "outputs"]
    )
]
```

### 5. Create Wiki/Knowledge Base

Write a markdown file with domain knowledge:

```markdown
# Domain Knowledge

## Overview
Description of the domain

## Available Services
- Service 1
- Service 2

## Policies
- Policy 1
- Policy 2
```

### 6. Define Rules

Create a rules module:

```python
RULES = [
    "Rule 1: Always verify user identity",
    "Rule 2: Escalate urgent issues",
    "Rule 3: Follow privacy guidelines"
]
```

## Example: Healthcare Domain

See the complete healthcare domain example in `examples/healthcare_domain/` which demonstrates:
- Patient information management
- Appointment scheduling
- Test result access
- Medical staff escalation

## Using Your Custom Domain

### Method 1: Direct Configuration File
```bash
python run.py --env your_domain --domain-config-path path/to/your_domain/domain.yaml --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --user-strategy llm
```

### Method 2: Register and Use by Name
```python
from tau_bench.domain_config import domain_registry

# Register your domain
domain_registry.load_domain_from_file("path/to/your_domain/domain.yaml")

# Now use by name
python run.py --env your_domain --model gpt-4o --model-provider openai
```

## Best Practices

1. **Modular Tool Design**: Keep tools focused on single responsibilities
2. **Clear Tool Descriptions**: Write detailed descriptions for LLM understanding
3. **Realistic Data**: Use representative data structures for your domain
4. **Comprehensive Tasks**: Cover various scenarios in your task definitions
5. **Privacy Considerations**: Be mindful of sensitive data in your domain
6. **Error Handling**: Implement robust error handling in tools
7. **Documentation**: Maintain clear wiki content for domain knowledge

## Testing Your Domain

Run the test suite to verify your domain works correctly:

```bash
python -c "
from tau_bench.domain_config import domain_registry
from tau_bench.envs.generic import GenericDomainEnv

# Load and test your domain
config = domain_registry.load_domain_from_file('path/to/domain.yaml')
print('Domain loaded:', config.name)

# Test component loading
env = GenericDomainEnv.__new__(GenericDomainEnv)
env.domain_config = config
env.config_base_path = Path('path/to/domain')

# Test each component
try:
    tools = env._load_tools()
    print('Tools loaded:', len(tools))
    
    tasks = env._load_tasks('test')
    print('Tasks loaded:', len(tasks))
    
    print('Domain validation successful!')
except Exception as e:
    print('Error:', e)
"
```

## Advanced Features

### Custom Task Splits
Define different task sets for training, testing, and development:

```yaml
task_splits:
  train: "path.to.training.tasks"
  test: "path.to.test.tasks"
  dev: "path.to.dev.tasks"
  custom_split: "path.to.custom.tasks"
```

### Domain-Specific Settings
Add custom configuration options:

```yaml
settings:
  max_conversation_turns: 25
  enable_feature_x: true
  custom_timeout: 60
  domain_specific_option: "value"
```

### Multiple Tool Modules
Organize tools across multiple modules:

```yaml
tools:
  - name: "tool1"
    module_path: "domain.tools.category1"
    class_name: "Tool1"
  - name: "tool2"
    module_path: "domain.tools.category2"
    class_name: "Tool2"
```

## Troubleshooting

Common issues and solutions:

1. **Import errors**: Ensure all modules are in Python path
2. **Tool loading failures**: Check tool class names and module paths
3. **Task validation errors**: Verify task structure matches schema
4. **Data loading issues**: Ensure data function returns expected format

## Contributing Domains

Consider contributing your domain to the tau-bench repository:

1. Create a clean, well-documented domain
2. Include comprehensive test cases
3. Provide usage examples
4. Submit a pull request

Your domain could help expand tau-bench's applicability to new areas!