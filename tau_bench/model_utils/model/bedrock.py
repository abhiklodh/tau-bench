import json
import os
from typing import Any, Dict

from tau_bench.model_utils.api.datapoint import Datapoint
from tau_bench.model_utils.model.chat import ChatModel, Message
from tau_bench.model_utils.model.completion import approx_cost_for_datapoint, approx_prompt_str
from tau_bench.model_utils.model.general_model import wrap_temperature
from tau_bench.model_utils.model.utils import approx_num_tokens

DEFAULT_BEDROCK_MODEL = "amazon.nova-pro-v1:0"
DEFAULT_MAX_TOKENS = 4096
ENV_VAR_REGION = "AWS_REGION"
DEFAULT_REGION = "us-east-1"

# Pricing per input token (USD per token)
PRICE_PER_INPUT_TOKEN_MAP = {
    # Amazon Nova models
    "amazon.nova-pro-v1:0": 0.8 / 1000000,
    "amazon.nova-lite-v1:0": 0.06 / 1000000,
    "amazon.nova-micro-v1:0": 0.035 / 1000000,
    
    # Anthropic Claude models on Bedrock
    "anthropic.claude-3-5-sonnet-20241022-v2:0": 3.0 / 1000000,
    "anthropic.claude-3-5-sonnet-20240620-v1:0": 3.0 / 1000000,
    "anthropic.claude-3-opus-20240229-v1:0": 15.0 / 1000000,
    "anthropic.claude-3-haiku-20240307-v1:0": 0.25 / 1000000,
    
    # Meta Llama models on Bedrock
    "meta.llama3-2-90b-instruct-v1:0": 2.0 / 1000000,
    "meta.llama3-2-11b-instruct-v1:0": 0.35 / 1000000,
}
INPUT_PRICE_PER_TOKEN_FALLBACK = 1.0 / 1000000

# Capability scores (0.0 to 1.0)
CAPABILITY_SCORE_MAP = {
    # Amazon Nova models
    "amazon.nova-pro-v1:0": 0.9,
    "amazon.nova-lite-v1:0": 0.7,
    "amazon.nova-micro-v1:0": 0.5,
    
    # Anthropic Claude models on Bedrock
    "anthropic.claude-3-5-sonnet-20241022-v2:0": 1.0,
    "anthropic.claude-3-5-sonnet-20240620-v1:0": 0.95,
    "anthropic.claude-3-opus-20240229-v1:0": 0.95,
    "anthropic.claude-3-haiku-20240307-v1:0": 0.7,
    
    # Meta Llama models on Bedrock
    "meta.llama3-2-90b-instruct-v1:0": 0.85,
    "meta.llama3-2-11b-instruct-v1:0": 0.6,
}
CAPABILITY_SCORE_FALLBACK = 0.5

# Latency (ms per output token) - estimated values
LATENCY_MS_PER_OUTPUT_TOKEN_MAP = {
    # Amazon Nova models (generally faster)
    "amazon.nova-pro-v1:0": 15.0,
    "amazon.nova-lite-v1:0": 10.0,
    "amazon.nova-micro-v1:0": 8.0,
    
    # Anthropic Claude models (moderate speed)
    "anthropic.claude-3-5-sonnet-20241022-v2:0": 20.0,
    "anthropic.claude-3-5-sonnet-20240620-v1:0": 20.0,
    "anthropic.claude-3-opus-20240229-v1:0": 25.0,
    "anthropic.claude-3-haiku-20240307-v1:0": 15.0,
    
    # Meta Llama models
    "meta.llama3-2-90b-instruct-v1:0": 30.0,
    "meta.llama3-2-11b-instruct-v1:0": 18.0,
}
LATENCY_MS_PER_OUTPUT_TOKEN_FALLBACK = 20.0

# Max context lengths
MAX_CONTEXT_LENGTH_MAP = {
    # Amazon Nova models
    "amazon.nova-pro-v1:0": 300000,
    "amazon.nova-lite-v1:0": 300000,
    "amazon.nova-micro-v1:0": 128000,
    
    # Anthropic Claude models on Bedrock
    "anthropic.claude-3-5-sonnet-20241022-v2:0": 200000,
    "anthropic.claude-3-5-sonnet-20240620-v1:0": 200000,
    "anthropic.claude-3-opus-20240229-v1:0": 200000,
    "anthropic.claude-3-haiku-20240307-v1:0": 200000,
    
    # Meta Llama models on Bedrock
    "meta.llama3-2-90b-instruct-v1:0": 128000,
    "meta.llama3-2-11b-instruct-v1:0": 128000,
}
MAX_CONTEXT_LENGTH_FALLBACK = 128000


class BedrockModel(ChatModel):
    def __init__(
        self,
        model: str | None = None,
        region: str | None = None,
        endpoint_url: str | None = None,
        temperature: float = 0.0,
        **kwargs,
    ) -> None:
        """
        Initialize Bedrock model with boto3.
        
        Args:
            model: Bedrock model ID (e.g., 'amazon.nova-pro-v1:0')
            region: AWS region (defaults to AWS_REGION env var or us-east-1)
            endpoint_url: Custom endpoint URL for Bedrock service
            temperature: Sampling temperature
            **kwargs: Additional parameters for boto3 client
        """
        import boto3
        
        if model is None:
            self.model = DEFAULT_BEDROCK_MODEL
        else:
            self.model = model
            
        if region is None:
            region = os.getenv(ENV_VAR_REGION, DEFAULT_REGION)
        
        # Initialize boto3 Bedrock client
        client_kwargs = {
            'service_name': 'bedrock-runtime',
            'region_name': region,
            **kwargs
        }
        
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url
            
        self.client = boto3.client(**client_kwargs)
        self.region = region
        self.endpoint_url = endpoint_url
        self.temperature = temperature

    def get_approx_cost(self, dp: Datapoint) -> float:
        cost_per_token = PRICE_PER_INPUT_TOKEN_MAP.get(self.model, INPUT_PRICE_PER_TOKEN_FALLBACK)
        return approx_cost_for_datapoint(dp=dp, price_per_input_token=cost_per_token)

    def get_latency(self, dp: Datapoint) -> float:
        latency_per_output_token = LATENCY_MS_PER_OUTPUT_TOKEN_MAP.get(
            self.model, LATENCY_MS_PER_OUTPUT_TOKEN_FALLBACK
        )
        return approx_cost_for_datapoint(dp=dp, price_per_input_token=latency_per_output_token)

    def get_capability(self) -> float:
        return CAPABILITY_SCORE_MAP.get(self.model, CAPABILITY_SCORE_FALLBACK)

    def supports_dp(self, dp: Datapoint) -> bool:
        prompt = approx_prompt_str(dp)
        return approx_num_tokens(prompt) <= MAX_CONTEXT_LENGTH_MAP.get(
            self.model, MAX_CONTEXT_LENGTH_FALLBACK
        )

    def _convert_messages_to_bedrock_format(self, messages: list[Message]) -> Dict[str, Any]:
        """Convert messages to Bedrock API format."""
        converted_messages = []
        system_messages = []
        
        for msg in messages:
            if msg.obj is not None:
                content = json.dumps(msg.obj)
            else:
                content = msg.content
                
            if msg.role.value == "system":
                system_messages.append({"text": content})
            else:
                converted_messages.append({
                    "role": msg.role.value,
                    "content": [{"text": content}]
                })
        
        # Bedrock requires alternating user/assistant messages
        # and system messages are passed separately
        request_body = {
            "messages": converted_messages,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": wrap_temperature(self.temperature)
        }
        
        if system_messages:
            request_body["system"] = system_messages
            
        return request_body

    def _invoke_model(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke Bedrock model and return response."""
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body

    def generate_message(
        self,
        messages: list[Message],
        force_json: bool,
        temperature: float | None = None,
    ) -> Message:
        if temperature is None:
            temperature = self.temperature
            
        # Convert messages to Bedrock format
        body = self._convert_messages_to_bedrock_format(messages)
        body["temperature"] = wrap_temperature(temperature)
        
        # Add JSON mode if requested
        if force_json:
            # Different models may have different JSON format specifications
            if self.model.startswith("amazon.nova"):
                body["inferenceConfig"] = {"guardrailConfig": {"guardrailIdentifier": "none"}}
                body["additionalModelRequestFields"] = {"response_format": {"type": "json_object"}}
            elif self.model.startswith("anthropic.claude"):
                # Claude models handle JSON through system prompts typically
                if "system" not in body:
                    body["system"] = []
                body["system"].append({"text": "Respond only with valid JSON."})
        
        # Invoke the model
        response = self._invoke_model(body)
        
        # Extract content from response
        if "content" in response:
            # Amazon Nova format
            content = response["content"][0]["text"]
        elif "completion" in response:
            # Legacy format for some models
            content = response["completion"]
        else:
            # Try to find text content in various response formats
            content = str(response)
            
        return self.handle_generate_message_response(
            prompt=body["messages"], content=content, force_json=force_json
        )