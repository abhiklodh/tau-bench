# AWS Bedrock/Nova Support in Tau-Bench

Tau-bench now supports AWS Bedrock models including the new Nova series through LiteLLM integration.

## Supported AWS Bedrock Models

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

## Setup

1. **Install AWS CLI and configure credentials**:
   ```bash
   pip install awscli
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

## Usage Examples

### Using Amazon Nova Pro
```bash
python run.py --agent-strategy tool-calling --env retail --model bedrock/amazon.nova-pro-v1:0 --model-provider bedrock --user-model bedrock/amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 5
```

### Using Claude 3.5 Sonnet on Bedrock
```bash
python run.py --agent-strategy tool-calling --env airline --model bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0 --model-provider bedrock --user-model bedrock/anthropic.claude-3-haiku-20240307-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 3
```

### Using Custom Domain with AWS Models
```bash
python run.py --env healthcare --domain-config-path examples/healthcare_domain/domain.yaml --model bedrock/amazon.nova-pro-v1:0 --model-provider bedrock --user-model bedrock/amazon.nova-lite-v1:0 --user-model-provider bedrock --user-strategy llm --max-concurrency 2
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