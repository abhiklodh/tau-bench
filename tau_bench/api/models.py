# Copyright Sierra

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import uuid


class EnvironmentType(str, Enum):
    """Supported environment types"""
    RETAIL = "retail"
    AIRLINE = "airline"
    HEALTHCARE = "healthcare"


class AgentStrategy(str, Enum):
    """Supported agent strategies"""
    TOOL_CALLING = "tool-calling"
    ACT = "act"
    REACT = "react"
    FEW_SHOT = "few-shot"


class TaskSplit(str, Enum):
    """Supported task splits"""
    TRAIN = "train"
    TEST = "test"
    DEV = "dev"


class UserStrategy(str, Enum):
    """Supported user strategies"""
    LLM = "llm"


class TaskValidationRequest(BaseModel):
    """Request model for task validation API"""
    
    # Required fields
    model_provider: str = Field(..., description="Model provider for the agent (e.g., 'openai', 'anthropic')")
    model: str = Field(..., description="Model name for the agent (e.g., 'gpt-4o', 'claude-3-5-sonnet')")
    env: EnvironmentType = Field(..., description="Environment type for task validation")
    
    # Optional fields with defaults
    user_model_provider: str = Field("openai", description="Model provider for user simulator")
    user_model: str = Field("gpt-4o", description="Model name for user simulator")
    num_trials: int = Field(1, ge=1, le=10, description="Number of trials to run (1-10)")
    agent_strategy: AgentStrategy = Field(AgentStrategy.TOOL_CALLING, description="Agent strategy to use")
    temperature: float = Field(0.0, ge=0.0, le=2.0, description="Sampling temperature for the agent model")
    task_split: TaskSplit = Field(TaskSplit.TEST, description="Task split to use")
    
    # Task selection
    start_index: int = Field(0, ge=0, description="Starting index for task range")
    end_index: int = Field(-1, description="Ending index for task range (-1 for all tasks)")
    task_ids: Optional[List[int]] = Field(None, description="Specific task IDs to run")
    
    # Execution settings
    max_concurrency: int = Field(1, ge=1, le=10, description="Maximum number of concurrent tasks")
    seed: int = Field(10, description="Random seed for reproducibility")
    shuffle: bool = Field(False, description="Whether to shuffle task order")
    user_strategy: UserStrategy = Field(UserStrategy.LLM, description="User simulation strategy")
    
    # Optional advanced settings
    few_shot_displays_path: Optional[str] = Field(None, description="Path to few-shot examples file")
    
    @field_validator('end_index')
    def validate_end_index(cls, v, info):
        if v != -1 and info.data and 'start_index' in info.data and v <= info.data['start_index']:
            raise ValueError("end_index must be greater than start_index or -1")
        return v


class ValidationMetrics(BaseModel):
    """Metrics from task validation"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float
    average_reward: float
    total_cost: Optional[float] = None
    average_task_duration: Optional[float] = None


class ValidationResult(BaseModel):
    """Individual task validation result"""
    task_id: int
    reward: float
    success: bool
    info: Dict[str, Any]
    trial: int
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


class TaskValidationResponse(BaseModel):
    """Response model for task validation API"""
    
    # Request metadata
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = Field(..., description="Validation status: 'completed', 'failed', 'partial'")
    
    # Results
    results: List[ValidationResult] = Field(default_factory=list)
    metrics: Optional[ValidationMetrics] = None
    
    # Execution details
    execution_time_seconds: float
    timestamp: str
    config_used: Dict[str, Any]
    
    # Error handling
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class APIError(BaseModel):
    """Error response model"""
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    version: str = "0.1.0"
    timestamp: str
    supported_environments: List[str] = ["retail", "airline", "healthcare"]
    supported_models: Dict[str, List[str]] = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620"],
        "google": ["gemini-1.5-pro", "gemini-1.5-flash"],
    }


class TaskListRequest(BaseModel):
    """Request model for listing available tasks"""
    env: EnvironmentType = Field(..., description="Environment to list tasks for")
    task_split: TaskSplit = Field(TaskSplit.TEST, description="Task split to list")


class TaskListResponse(BaseModel):
    """Response model for listing available tasks"""
    env: str
    task_split: str
    total_tasks: int
    tasks: List[Dict[str, Any]] = Field(default_factory=list)