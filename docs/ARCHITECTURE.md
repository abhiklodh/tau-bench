# Tau-Bench Domain-Agnostic Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Tau-Bench System                           │
├─────────────────────────────────────────────────────────────────────┤
│                             CLI Layer                               │
│  run.py --env <domain> --domain-config-path <config.yaml>          │
│         --model <model> --model-provider <provider>                │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────────┐
│                     Environment Factory                            │
│  get_env() - Dynamic environment creation based on:                │
│  • Domain name (legacy: retail, airline)                          │
│  • Domain config path (new: any YAML/JSON config)                 │
│  • Registry lookup (registered domains)                           │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
┌────────▼──────┐  ┌──────▼────────────────────────────────────────────┐
│ Legacy Envs   │  │            Generic Domain Environment            │
│ • RetailEnv   │  │ • ConfigurableDomainEnv                          │
│ • AirlineEnv  │  │ • Loads components dynamically                   │
└───────────────┘  │ • Plugin-based architecture                      │
                   └──────┬────────────────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────────────┐
│                    Domain Registry                                   │
│ • Dynamic domain discovery                                           │
│ • YAML/JSON configuration loading                                    │
│ • Domain registration and retrieval                                  │
└─────────────────────────┬─────────────────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────────────┐
│                   Domain Configuration                               │
│ domain.yaml/json:                                                    │
│ • name, display_name, description                                    │
│ • data_loader, wiki_file, rules_file                                │
│ • tools[], task_splits{}, terminate_tools[]                         │
│ • settings{} (domain-specific)                                      │
└─────────────────────────┬─────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
┌─────────▼─────┐ ┌──────▼──────┐ ┌──────▼──────────────────────────────┐
│     Tools     │ │    Data     │ │        Tasks & Content              │
│ • Plugin-based│ │ • Dynamic   │ │ • task_splits (train/test/dev)      │
│ • Configurable│ │   loading   │ │ • wiki content (markdown/python)   │
│ • Tool registry│ │ • Domain-   │ │ • rules (policies/guidelines)      │
└───────────────┘ │   specific  │ └─────────────────────────────────────┘
                  └─────────────┘
```

## Component Details

### 1. Domain Configuration Schema
```yaml
name: domain_name
display_name: "Human Readable Name"
description: "Domain description"
version: "1.0.0"

data_loader: "module.path.to.load_data_function"
wiki_file: "path/to/wiki.md"
rules_file: "module.path.to.rules"

tools:
  - name: "tool_name"
    module_path: "module.path.to.tool"
    class_name: "ToolClass"
    description: "Tool description"

task_splits:
  test: "module.path.to.test_tasks"
  train: "module.path.to.train_tasks"

terminate_tools:
  - "tool_that_ends_conversation"

settings:
  custom_setting: "value"
```

### 2. Tool Plugin System
```python
class CustomTool(Tool):
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "Tool description",
                "parameters": {...}
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], **kwargs) -> str:
        # Tool implementation
        return "Tool response"
```

### 3. Generic Environment Flow
```
GenericDomainEnv.__init__()
├── Load domain config
├── Set config base path
├── Load data function
├── Load tools (dynamic import)
├── Load tasks (per split)
├── Load wiki content
├── Load rules
└── Initialize base environment
```

### 4. Model Provider Support
- **OpenAI**: GPT-4, GPT-3.5-turbo, etc.
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus/Haiku
- **Google**: Gemini Pro, Gemini Flash
- **Mistral**: Mistral Large, Mistral Medium
- **AWS Bedrock**: Amazon Nova Pro/Lite/Micro, Claude on Bedrock, Llama on Bedrock

## Key Features

### Domain Agnostic
- **No code changes needed** for new domains
- **Configuration-driven** architecture
- **Plugin-based** tool system
- **Dynamic discovery** of domains

### Backward Compatible
- **Existing domains** (retail, airline) work unchanged
- **Legacy API** preserved
- **Existing benchmarks** continue to work
- **Gradual migration** path

### Extensible
- **Easy domain creation** with YAML/JSON
- **Tool plugin system** for custom functionality
- **Flexible task definitions** 
- **Custom model providers** via LiteLLM

### Cloud Native
- **AWS Bedrock integration** for Nova models
- **Multi-provider support** (OpenAI, Anthropic, Google, etc.)
- **Concurrent execution** with configurable limits
- **Cost management** features

## Usage Examples

### Built-in Domain
```bash
python run.py --env retail --model gpt-4o --model-provider openai
```

### Custom Domain
```bash
python run.py --env healthcare \
  --domain-config-path examples/healthcare_domain/domain.yaml \
  --model bedrock/amazon.nova-pro-v1:0 --model-provider bedrock
```

### List Available Domains
```bash
python run.py --list-domains
```

## Migration Path

1. **Immediate**: All existing functionality works unchanged
2. **Short-term**: Create domain configs for built-in domains
3. **Medium-term**: Add new domains via configuration
4. **Long-term**: Deprecate hardcoded domain logic

This architecture makes tau-bench a truly universal benchmarking framework for any domain!