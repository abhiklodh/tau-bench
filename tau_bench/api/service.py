# Copyright Sierra

import os
import time
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from tau_bench.run import run as tau_run
from tau_bench.types import RunConfig, EnvRunResult
from tau_bench.envs import get_env
from tau_bench.api.models import (
    TaskValidationRequest,
    TaskValidationResponse,
    ValidationResult,
    ValidationMetrics,
    APIError,
    HealthResponse,
    TaskListRequest,
    TaskListResponse
)
from litellm import provider_list


logger = logging.getLogger(__name__)


class TauBenchAPIService:
    """
    Main service class for Tau-Bench API.
    
    This service provides task validation functionality for AI model development
    by running tasks across different environments (retail, airline, healthcare)
    with specified models and repetitions.
    """
    
    def __init__(self, log_dir: str = "api_results"):
        """
        Initialize the API service.
        
        Args:
            log_dir: Directory to store validation results
        """
        self.log_dir = log_dir
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info(f"TauBenchAPIService initialized with log_dir: {log_dir}")
    
    def validate_request(self, request: TaskValidationRequest) -> List[str]:
        """
        Validate the incoming request and return any validation errors.
        
        Args:
            request: The task validation request
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate model provider
        if request.model_provider not in provider_list:
            errors.append(f"Invalid model provider: {request.model_provider}. Supported: {provider_list}")
        
        if request.user_model_provider not in provider_list:
            errors.append(f"Invalid user model provider: {request.user_model_provider}. Supported: {provider_list}")
        
        # Validate environment
        if request.env not in ["retail", "airline", "healthcare"]:
            errors.append(f"Invalid environment: {request.env}. Supported: retail, airline, healthcare")
        
        # Validate task range
        if request.task_ids is None and request.start_index < 0:
            errors.append("start_index must be >= 0")
        
        if request.task_ids is None and request.end_index != -1 and request.end_index <= request.start_index:
            errors.append("end_index must be > start_index or -1")
        
        return errors
    
    async def validate_tasks(self, request: TaskValidationRequest) -> TaskValidationResponse:
        """
        Main method to validate tasks with specified configuration.
        
        Args:
            request: Task validation request
            
        Returns:
            Task validation response with results and metrics
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        # Validate request
        validation_errors = self.validate_request(request)
        if validation_errors:
            return TaskValidationResponse(
                status="failed",
                execution_time_seconds=time.time() - start_time,
                timestamp=timestamp,
                config_used=request.model_dump(),
                errors=validation_errors
            )
        
        try:
            # Convert API request to RunConfig
            config = self._convert_to_run_config(request)
            
            logger.info(f"Starting task validation with config: {config}")
            
            # Run validation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(self.executor, tau_run, config)
            
            # Convert results to API format
            validation_results = self._convert_results(results)
            
            # Calculate metrics
            metrics = self._calculate_metrics(results)
            
            execution_time = time.time() - start_time
            
            response = TaskValidationResponse(
                status="completed",
                results=validation_results,
                metrics=metrics,
                execution_time_seconds=execution_time,
                timestamp=timestamp,
                config_used=request.model_dump()
            )
            
            logger.info(f"Task validation completed successfully in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Task validation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return TaskValidationResponse(
                status="failed",
                execution_time_seconds=execution_time,
                timestamp=timestamp,
                config_used=request.model_dump(),
                errors=[error_msg]
            )
    
    def _convert_to_run_config(self, request: TaskValidationRequest) -> RunConfig:
        """Convert API request to RunConfig."""
        return RunConfig(
            model_provider=request.model_provider,
            user_model_provider=request.user_model_provider,
            model=request.model,
            user_model=request.user_model,
            num_trials=request.num_trials,
            env=request.env.value,
            agent_strategy=request.agent_strategy.value,
            temperature=request.temperature,
            task_split=request.task_split.value,
            start_index=request.start_index,
            end_index=request.end_index,
            task_ids=request.task_ids,
            log_dir=self.log_dir,
            max_concurrency=request.max_concurrency,
            seed=request.seed,
            shuffle=int(request.shuffle),
            user_strategy=request.user_strategy.value,
            few_shot_displays_path=request.few_shot_displays_path,
        )
    
    def _convert_results(self, results: List[EnvRunResult]) -> List[ValidationResult]:
        """Convert tau-bench results to API format."""
        api_results = []
        
        for result in results:
            # Check if task was successful (you may need to adjust this logic)
            success = result.reward > 0.0
            
            api_result = ValidationResult(
                task_id=result.task_id,
                reward=result.reward,
                success=success,
                info=result.info,
                trial=result.trial,
                error=None if success else "Task failed with zero reward"
            )
            api_results.append(api_result)
        
        return api_results
    
    def _calculate_metrics(self, results: List[EnvRunResult]) -> ValidationMetrics:
        """Calculate metrics from results."""
        if not results:
            return ValidationMetrics(
                total_tasks=0,
                successful_tasks=0,
                failed_tasks=0,
                success_rate=0.0,
                average_reward=0.0
            )
        
        total_tasks = len(results)
        successful_tasks = sum(1 for r in results if r.reward > 0.0)
        failed_tasks = total_tasks - successful_tasks
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0
        average_reward = sum(r.reward for r in results) / total_tasks if total_tasks > 0 else 0.0
        
        return ValidationMetrics(
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            success_rate=success_rate,
            average_reward=average_reward
        )
    
    async def get_health(self) -> HealthResponse:
        """Get service health status."""
        return HealthResponse(
            timestamp=datetime.now().isoformat()
        )
    
    async def list_tasks(self, request: TaskListRequest) -> TaskListResponse:
        """
        List available tasks for a given environment and task split.
        
        Args:
            request: Task list request
            
        Returns:
            Task list response with available tasks
        """
        try:
            # Get environment to access tasks
            env = get_env(
                env_name=request.env.value,
                user_strategy="llm",
                user_model="gpt-4o",
                user_provider="openai",
                task_split=request.task_split.value,
            )
            
            # Extract basic task information (avoid exposing full task details)
            tasks_info = []
            for i, task in enumerate(env.tasks):
                task_info = {
                    "task_id": i,
                    "user_id": getattr(task, 'user_id', None),
                    "instruction_preview": (
                        getattr(task, 'instruction', '')[:100] + "..." 
                        if len(getattr(task, 'instruction', '')) > 100 
                        else getattr(task, 'instruction', '')
                    ),
                    "num_actions": len(getattr(task, 'actions', []))
                }
                tasks_info.append(task_info)
            
            return TaskListResponse(
                env=request.env.value,
                task_split=request.task_split.value,
                total_tasks=len(env.tasks),
                tasks=tasks_info
            )
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {str(e)}", exc_info=True)
            raise
    
    def cleanup(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        logger.info("TauBenchAPIService cleanup completed")