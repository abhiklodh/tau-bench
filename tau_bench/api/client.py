# Copyright Sierra

import requests
import json
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tau_bench.api.models import (
    TaskValidationRequest,
    TaskValidationResponse,
    TaskListRequest,
    TaskListResponse,
    HealthResponse
)


class TauBenchAPIClient:
    """
    Client SDK for interacting with the Tau-Bench API service.
    
    This client provides convenient methods for validating tasks, listing
    available tasks, and checking service health.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 300,
        max_retries: int = 3
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API service
            timeout: Request timeout in seconds
            max_retries: Maximum number of request retries
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "TauBenchAPIClient/1.0.0"
        })
    
    def validate_tasks(
        self,
        model_provider: str,
        model: str,
        env: str,
        num_trials: int = 1,
        agent_strategy: str = "tool-calling",
        temperature: float = 0.0,
        task_split: str = "test",
        start_index: int = 0,
        end_index: int = -1,
        task_ids: Optional[List[int]] = None,
        max_concurrency: int = 1,
        seed: int = 10,
        shuffle: bool = False,
        user_model_provider: str = "openai",
        user_model: str = "gpt-4o",
        user_strategy: str = "llm",
        few_shot_displays_path: Optional[str] = None,
    ) -> TaskValidationResponse:
        """
        Validate tasks with specified configuration.
        
        Args:
            model_provider: Model provider for the agent (e.g., 'openai', 'anthropic')
            model: Model name for the agent (e.g., 'gpt-4o', 'claude-3-5-sonnet')
            env: Environment type ('retail', 'airline', 'healthcare')
            num_trials: Number of trials to run (1-10)
            agent_strategy: Agent strategy ('tool-calling', 'act', 'react', 'few-shot')
            temperature: Sampling temperature (0.0-2.0)
            task_split: Task split ('train', 'test', 'dev')
            start_index: Starting index for task range
            end_index: Ending index for task range (-1 for all tasks)
            task_ids: Specific task IDs to run (overrides start/end index)
            max_concurrency: Maximum concurrent tasks (1-10)
            seed: Random seed for reproducibility
            shuffle: Whether to shuffle task order
            user_model_provider: Model provider for user simulator
            user_model: Model name for user simulator
            user_strategy: User simulation strategy
            few_shot_displays_path: Path to few-shot examples file
            
        Returns:
            Task validation response with results and metrics
        """
        request_data = TaskValidationRequest(
            model_provider=model_provider,
            model=model,
            env=env,
            num_trials=num_trials,
            agent_strategy=agent_strategy,
            temperature=temperature,
            task_split=task_split,
            start_index=start_index,
            end_index=end_index,
            task_ids=task_ids,
            max_concurrency=max_concurrency,
            seed=seed,
            shuffle=shuffle,
            user_model_provider=user_model_provider,
            user_model=user_model,
            user_strategy=user_strategy,
            few_shot_displays_path=few_shot_displays_path,
        )
        
        response = self.session.post(
            f"{self.base_url}/api/v1/validate-tasks",
            json=request_data.model_dump(),
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return TaskValidationResponse(**response.json())
    
    def list_tasks(
        self,
        env: str,
        task_split: str = "test"
    ) -> TaskListResponse:
        """
        List available tasks for a given environment and task split.
        
        Args:
            env: Environment type ('retail', 'airline', 'healthcare')
            task_split: Task split ('train', 'test', 'dev')
            
        Returns:
            Task list response with available tasks
        """
        request_data = TaskListRequest(
            env=env,
            task_split=task_split
        )
        
        response = self.session.post(
            f"{self.base_url}/api/v1/list-tasks",
            json=request_data.model_dump(),
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return TaskListResponse(**response.json())
    
    def health_check(self) -> HealthResponse:
        """
        Check service health and status.
        
        Returns:
            Health response with service status and supported features
        """
        response = self.session.get(
            f"{self.base_url}/health",
            timeout=10  # Use shorter timeout for health checks
        )
        response.raise_for_status()
        
        return HealthResponse(**response.json())
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get general service information.
        
        Returns:
            Service information dictionary
        """
        response = self.session.get(
            f"{self.base_url}/",
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()


# Convenience functions for common use cases

def quick_validate(
    model_provider: str,
    model: str,
    env: str,
    base_url: str = "http://localhost:8000",
    **kwargs
) -> TaskValidationResponse:
    """
    Quick validation with minimal configuration.
    
    Args:
        model_provider: Model provider for the agent
        model: Model name for the agent
        env: Environment type
        base_url: API service base URL
        **kwargs: Additional validation parameters
        
    Returns:
        Task validation response
    """
    client = TauBenchAPIClient(base_url=base_url)
    return client.validate_tasks(
        model_provider=model_provider,
        model=model,
        env=env,
        **kwargs
    )


def validate_with_comparison(
    models: List[Dict[str, str]],
    env: str,
    base_url: str = "http://localhost:8000",
    **kwargs
) -> List[TaskValidationResponse]:
    """
    Validate multiple models for comparison.
    
    Args:
        models: List of model configurations [{"provider": "openai", "model": "gpt-4o"}, ...]
        env: Environment type
        base_url: API service base URL
        **kwargs: Additional validation parameters
        
    Returns:
        List of validation responses for each model
    """
    client = TauBenchAPIClient(base_url=base_url)
    results = []
    
    for model_config in models:
        result = client.validate_tasks(
            model_provider=model_config["provider"],
            model=model_config["model"],
            env=env,
            **kwargs
        )
        results.append(result)
    
    return results