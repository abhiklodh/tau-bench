# AWS Bedrock/Nova Support in Tau-Bench

Tau-bench supports AWS Bedrock models through **two approaches**:

1. **LiteLLM Integration** (existing): Uses LiteLLM's Bedrock provider with `bedrock/` prefix
2. **Dedicated boto3 Integration** (new): Direct boto3 integration with custom endpoint support

## Approach 1: LiteLLM Integration

Uses LiteLLM's built-in Bedrock support with automatic credential handling.

### Supported Models (LiteLLM)
- **Amazon Nova Models**:
  - `bedrock/amazon.nova-pro-v1:0`
  - `bedrock/amazon.nova-lite-v1:0`
  - `bedrock/amazon.nova-micro-v1:0`

- **Anthropic Claude on Bedrock**:
  - `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0`
  - `bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0`
  - `bedrock/anthropic.claude-3-opus-20240229-v1:0`
  - `bedrock/anthropic.claude-3-haiku-20240307-v1:0`

- **Meta Llama on Bedrock**:
  - `bedrock/meta.llama3-2-90b-instruct-v1:0`
  - `bedrock/meta.llama3-2-11b-instruct-v1:0`

### Usage (LiteLLM)
```bash
python run.py --agent-strategy tool-calling --env retail --model bedrock/amazon.nova-pro-v1:0 --model-provider bedrock --user-model bedrock/amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 5
```

## Approach 2: Dedicated boto3 Integration

Uses boto3 directly for maximum control and custom endpoint support.

### Supported Models (Dedicated)
All Bedrock models without the `bedrock/` prefix:
- **Amazon Nova Models**:
  - `amazon.nova-pro-v1:0`
  - `amazon.nova-lite-v1:0`
  - `amazon.nova-micro-v1:0`

- **Anthropic Claude on Bedrock**:
  - `anthropic.claude-3-5-sonnet-20241022-v2:0`
  - `anthropic.claude-3-5-sonnet-20240620-v1:0`
  - `anthropic.claude-3-opus-20240229-v1:0`
  - `anthropic.claude-3-haiku-20240307-v1:0`

- **Meta Llama on Bedrock**:
  - `meta.llama3-2-90b-instruct-v1:0`
  - `meta.llama3-2-11b-instruct-v1:0`

### Usage (Dedicated)
```bash
# Using dedicated boto3 integration
python run.py --agent-strategy tool-calling --env retail --model amazon.nova-pro-v1:0 --model-provider bedrock --user-model amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 5
```

### Custom Endpoints (Dedicated Only)
The dedicated integration supports custom Bedrock endpoints:

```bash
# Using custom Bedrock endpoint
export AWS_BEDROCK_ENDPOINT_URL=https://custom-bedrock.example.com
python run.py --agent-strategy tool-calling --env retail --model amazon.nova-pro-v1:0 --model-provider bedrock --user-model amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm
```

## Which Approach to Use?

- **Use LiteLLM Integration** if:
  - You want simple, out-of-the-box Bedrock support
  - You don't need custom endpoints
  - You prefer LiteLLM's unified interface

- **Use Dedicated Integration** if:
  - You need custom Bedrock endpoints
  - You want direct boto3 control for advanced configuration
  - You prefer working directly with AWS SDKs

## Setup

Both approaches use the same AWS credentials setup:

1. **Install AWS CLI and configure credentials**:
   ```bash
   pip install awscli boto3
   aws configure
   ```

2. **Set up AWS credentials** (one of the following):
   - AWS credentials file (`~/.aws/credentials`)
   - Environment variables:
     ```bash
     export AWS_ACCESS_KEY_ID=your_access_key
     export AWS_SECRET_ACCESS_KEY=your_secret_key
     export AWS_REGION=us-east-1  # or your preferred region
     ```
   - IAM roles (if running on EC2)

3. **Ensure Bedrock model access**: Enable model access in the AWS Bedrock console for the models you want to use.

4. **For dedicated integration with custom endpoints** (optional):
   ```bash
   export AWS_BEDROCK_ENDPOINT_URL=https://your-custom-endpoint.com
   ```

## More Usage Examples

### LiteLLM Approach Examples
### LiteLLM Approach Examples

#### Amazon Nova Pro
```bash
python run.py --agent-strategy tool-calling --env retail --model bedrock/amazon.nova-pro-v1:0 --model-provider bedrock --user-model bedrock/amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 5
```

#### Claude 3.5 Sonnet on Bedrock
```bash
python run.py --agent-strategy tool-calling --env airline --model bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0 --model-provider bedrock --user-model bedrock/anthropic.claude-3-haiku-20240307-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 3
```

### Dedicated boto3 Approach Examples

#### Amazon Nova Pro (Dedicated)
```bash
python run.py --agent-strategy tool-calling --env retail --model amazon.nova-pro-v1:0 --model-provider bedrock --user-model amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 5
```

#### Claude 3.5 Sonnet (Dedicated)
```bash
python run.py --agent-strategy tool-calling --env airline --model anthropic.claude-3-5-sonnet-20241022-v2:0 --model-provider bedrock --user-model anthropic.claude-3-haiku-20240307-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 3
```

#### With Custom Endpoint (Dedicated Only)
```bash
export AWS_BEDROCK_ENDPOINT_URL=https://bedrock-fips.us-gov-west-1.amazonaws.com
python run.py --agent-strategy tool-calling --env retail --model amazon.nova-pro-v1:0 --model-provider bedrock --user-model amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm
```

### Using Custom Domain with AWS Models (Both Approaches)

**LiteLLM:**
```bash
python run.py --env healthcare --domain-config-path examples/healthcare_domain/domain.yaml --model bedrock/amazon.nova-pro-v1:0 --model-provider bedrock --user-model bedrock/amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 2
```

**Dedicated:**
```bash
python run.py --env healthcare --domain-config-path examples/healthcare_domain/domain.yaml --model amazon.nova-pro-v1:0 --model-provider bedrock --user-model amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 2
```

## Cost Considerations

- Amazon Nova models offer competitive pricing
- Monitor your AWS Bedrock usage through the AWS console
- Consider using smaller models (Nova Lite/Micro) for user simulation to reduce costs
- Use `--max-concurrency` to control parallel requests and manage costs

## Troubleshooting

1. **Authentication errors**: Ensure AWS credentials are properly configured
2. **Model access errors**: Enable model access in Bedrock console
3. **Region errors**: Ensure your AWS region supports the Bedrock models you're using
4. **Rate limits**: Reduce `--max-concurrency` if hitting rate limits

## Regional Availability

AWS Bedrock models are available in specific regions. Check the [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) for current availability.