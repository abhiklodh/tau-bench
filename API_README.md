# Tau-Bench API Service

A comprehensive REST API service for validating AI model tasks across retail, airline, and healthcare environments using the Tau-Bench framework.

## 🌟 Overview

The Tau-Bench API Service provides a robust, scalable way to validate AI model performance across different business domains. It supports:

- **Multiple Environments**: Retail, airline, and healthcare scenarios
- **Various AI Models**: OpenAI, Anthropic, Google, and more
- **Flexible Configuration**: Customizable task validation parameters
- **Concurrent Processing**: High-performance task execution
- **Comprehensive Metrics**: Detailed success rates and performance analytics

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/abhiklodh/tau-bench
cd tau-bench

# Install with API dependencies
pip install -e .

# Or with optional API dependencies
pip install -e ".[api]"
```

### Starting the Server

```bash
# Start with default settings
tau-bench-server

# Custom configuration
tau-bench-server --host 0.0.0.0 --port 8080 --log-level debug
```

### Environment Variables

Set up your AI model API keys:

```bash
# Required for OpenAI models
export OPENAI_API_KEY="your-openai-api-key"

# Required for Anthropic models
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Required for Google models
export GOOGLE_API_KEY="your-google-api-key"

# Optional: Custom log directory
export TAU_BENCH_LOG_DIR="/custom/log/path"
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-09-25T16:27:33.874817",
  "supported_environments": ["retail", "airline", "healthcare"],
  "supported_models": {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620"],
    "google": ["gemini-1.5-pro", "gemini-1.5-flash"]
  }
}
```

#### 2. Validate Tasks
```bash
POST /api/v1/validate-tasks
```

**Request Body:**
```json
{
  "model_provider": "openai",
  "model": "gpt-4o",
  "env": "retail",
  "num_trials": 3,
  "agent_strategy": "tool-calling",
  "temperature": 0.0,
  "task_split": "test",
  "start_index": 0,
  "end_index": 10,
  "max_concurrency": 2
}
```

**Response:**
```json
{
  "request_id": "uuid-here",
  "status": "completed",
  "results": [
    {
      "task_id": 0,
      "reward": 1.0,
      "success": true,
      "info": {...},
      "trial": 0
    }
  ],
  "metrics": {
    "total_tasks": 10,
    "successful_tasks": 8,
    "failed_tasks": 2,
    "success_rate": 0.8,
    "average_reward": 0.75
  },
  "execution_time_seconds": 45.2,
  "timestamp": "2025-09-25T16:27:33.874817",
  "config_used": {...}
}
```

#### 3. List Tasks
```bash
POST /api/v1/list-tasks
```

**Request Body:**
```json
{
  "env": "retail",
  "task_split": "test"
}
```

**Response:**
```json
{
  "env": "retail",
  "task_split": "test",
  "total_tasks": 50,
  "tasks": [
    {
      "task_id": 0,
      "user_id": "user123",
      "instruction_preview": "You want to return a product...",
      "num_actions": 5
    }
  ]
}
```

## 🔧 Client SDK

Use the provided Python client for easy integration:

```python
from tau_bench.api.client import TauBenchAPIClient

# Initialize client
client = TauBenchAPIClient(base_url="http://localhost:8000")

# Check health
health = client.health_check()
print(f"Service status: {health.status}")

# Validate tasks
response = client.validate_tasks(
    model_provider="openai",
    model="gpt-4o",
    env="retail",
    num_trials=2,
    start_index=0,
    end_index=5
)

print(f"Success rate: {response.metrics.success_rate:.2%}")
```

### Convenience Functions

```python
from tau_bench.api.client import quick_validate, validate_with_comparison

# Quick validation
result = quick_validate(
    model_provider="openai",
    model="gpt-4o",
    env="airline",
    num_trials=1
)

# Compare multiple models
models = [
    {"provider": "openai", "model": "gpt-4o"},
    {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
]

results = validate_with_comparison(
    models=models,
    env="healthcare",
    num_trials=2
)
```

## 🛠️ Configuration Options

### Task Validation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_provider` | string | **required** | Model provider (openai, anthropic, google) |
| `model` | string | **required** | Specific model name |
| `env` | string | **required** | Environment (retail, airline, healthcare) |
| `num_trials` | integer | 1 | Number of trials (1-10) |
| `agent_strategy` | string | "tool-calling" | Agent strategy |
| `temperature` | float | 0.0 | Sampling temperature (0.0-2.0) |
| `task_split` | string | "test" | Task split (train, test, dev) |
| `start_index` | integer | 0 | Starting task index |
| `end_index` | integer | -1 | Ending task index (-1 for all) |
| `task_ids` | array | null | Specific task IDs to run |
| `max_concurrency` | integer | 1 | Max concurrent tasks (1-10) |
| `seed` | integer | 10 | Random seed |
| `shuffle` | boolean | false | Shuffle task order |

### Server Configuration

| CLI Option | Environment Variable | Default | Description |
|------------|---------------------|---------|-------------|
| `--host` | `HOST` | "0.0.0.0" | Server host |
| `--port` | `PORT` | 8000 | Server port |
| `--log-dir` | `TAU_BENCH_LOG_DIR` | "api_results" | Log directory |
| `--log-level` | `LOG_LEVEL` | "info" | Logging level |
| `--workers` | `WORKERS` | 1 | Worker processes |

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t tau-bench-api .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  -v $(pwd)/logs:/app/logs \
  tau-bench-api
```

### Docker Compose

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## 📊 Examples

Check out the comprehensive examples in `examples/api_examples.py`:

```bash
# Make sure the server is running first
tau-bench-server &

# Run examples
python examples/api_examples.py
```

The examples demonstrate:
- Basic task validation
- Model comparison
- Task listing
- Advanced configuration options
- Error handling

## 🔍 Monitoring and Logging

### Health Monitoring

The service provides a health check endpoint for monitoring:

```bash
# Check service health
curl http://localhost:8000/health

# Monitor continuously
watch -n 30 'curl -s http://localhost:8000/health | jq .status'
```

### Log Files

Logs are stored in the configured log directory:

```
api_results/
├── validation_results.json    # Task results
├── service.log               # Service logs
└── api_audit.log            # API request audit
```

### Performance Metrics

The API tracks key metrics:
- Task success rates
- Average rewards
- Execution times
- Request/response latency
- Error rates

## 🚨 Error Handling

### Common Error Responses

1. **Authentication Error**
```json
{
  "error_type": "authentication_error",
  "message": "API key not provided",
  "timestamp": "2025-09-25T16:27:33.874817"
}
```

2. **Validation Error**
```json
{
  "error_type": "validation_error", 
  "message": "Invalid model provider",
  "details": {"provider": "invalid_provider"},
  "timestamp": "2025-09-25T16:27:33.874817"
}
```

3. **Rate Limit Error**
```json
{
  "error_type": "rate_limit_error",
  "message": "Too many requests",
  "retry_after": 60,
  "timestamp": "2025-09-25T16:27:33.874817"
}
```

## 📈 Performance

### Recommended Settings

- **Development**: 1-2 workers, low concurrency
- **Production**: 4-8 workers, higher concurrency based on load
- **High Load**: Use nginx load balancer + multiple instances

### Optimization Tips

1. **Concurrent Tasks**: Increase `max_concurrency` for I/O bound workloads
2. **Batch Processing**: Use task ranges instead of individual task IDs
3. **Caching**: Results are automatically cached in the log directory
4. **Rate Limiting**: Configure based on your model provider limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Start development server
tau-bench-server --reload --log-level debug
```

## 📄 License

Copyright Sierra - See LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/abhiklodh/tau-bench/issues)
- **Documentation**: Available at `/docs` endpoint when server is running
- **Examples**: See `examples/` directory for usage patterns