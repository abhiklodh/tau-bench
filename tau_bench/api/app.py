# Copyright Sierra

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from tau_bench.api.service import TauBenchAPIService
from tau_bench.api.models import (
    TaskValidationRequest,
    TaskValidationResponse,
    TaskListRequest,
    TaskListResponse,
    HealthResponse,
    APIError
)


# Global service instance
service: TauBenchAPIService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global service
    
    # Startup
    log_dir = os.getenv("TAU_BENCH_LOG_DIR", "api_results")
    service = TauBenchAPIService(log_dir=log_dir)
    
    logging.info("TauBench API Service started")
    yield
    
    # Shutdown
    if service:
        service.cleanup()
    logging.info("TauBench API Service stopped")


# Create FastAPI application
app = FastAPI(
    title="Tau-Bench API",
    description="""
    **Tau-Bench Task Validation API**
    
    This API service provides endpoints for validating AI model tasks across different environments:
    - **Retail**: Customer service and e-commerce scenarios
    - **Airline**: Flight booking and customer service scenarios  
    - **Healthcare**: Medical appointment and patient service scenarios
    
    The service allows you to:
    - Validate tasks with specified models and number of repetitions
    - Get detailed metrics and results from task executions
    - List available tasks for each environment
    - Monitor service health and status
    
    ## Supported Models
    
    ### OpenAI
    - gpt-4o, gpt-4o-mini, gpt-4-turbo
    
    ### Anthropic  
    - claude-3-5-sonnet-20241022, claude-3-5-sonnet-20240620
    
    ### Google
    - gemini-1.5-pro, gemini-1.5-flash
    
    ## Example Usage
    
    ```python
    import requests
    
    # Validate tasks in retail environment
    response = requests.post('/api/v1/validate-tasks', json={
        'model_provider': 'openai',
        'model': 'gpt-4o',
        'env': 'retail',
        'num_trials': 3,
        'max_concurrency': 2
    })
    
    results = response.json()
    print(f"Success rate: {results['metrics']['success_rate']}")
    ```
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logging.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    error_response = APIError(
        error_type="internal_error",
        message="An internal error occurred",
        timestamp=datetime.now().isoformat()
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Tau-Bench Task Validation API",
        "version": "1.0.0",
        "description": "API service for validating AI model tasks in retail, airline, and healthcare environments",
        "endpoints": {
            "health": "/health",
            "validate_tasks": "/api/v1/validate-tasks",
            "list_tasks": "/api/v1/list-tasks",
            "docs": "/docs",
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global service
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return await service.get_health()


@app.post("/api/v1/validate-tasks", response_model=TaskValidationResponse)
async def validate_tasks(
    request: TaskValidationRequest,
    background_tasks: BackgroundTasks
) -> TaskValidationResponse:
    """
    Validate tasks with specified model and configuration.
    
    This endpoint runs task validation using the tau-bench framework with the
    specified model, environment, and configuration parameters.
    
    **Parameters:**
    - **model_provider**: Model provider (openai, anthropic, google, etc.)
    - **model**: Specific model name (gpt-4o, claude-3-5-sonnet, etc.)
    - **env**: Environment type (retail, airline, healthcare)
    - **num_trials**: Number of trials to run (1-10)
    - **agent_strategy**: Agent strategy (tool-calling, act, react, few-shot)
    - **temperature**: Sampling temperature (0.0-2.0)
    - **task_split**: Task split (train, test, dev)
    - **max_concurrency**: Maximum concurrent tasks (1-10)
    
    **Returns:**
    - Detailed validation results with metrics
    - Individual task results with rewards and success status
    - Execution metadata and timing information
    """
    global service
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await service.validate_tasks(request)
        
        # Log the validation request for audit purposes
        background_tasks.add_task(
            _log_validation_request,
            request.model_dump(),
            result.model_dump()
        )
        
        return result
    
    except Exception as e:
        logging.error(f"Task validation failed: {str(e)}", exc_info=True)
        error_response = APIError(
            error_type="validation_error",
            message=str(e),
            timestamp=datetime.now().isoformat()
        )
        raise HTTPException(status_code=400, detail=error_response.model_dump())


@app.post("/api/v1/list-tasks", response_model=TaskListResponse)
async def list_tasks(request: TaskListRequest) -> TaskListResponse:
    """
    List available tasks for a given environment and task split.
    
    This endpoint returns information about available tasks in the specified
    environment and task split, including basic metadata like task IDs,
    user IDs, and instruction previews.
    
    **Parameters:**
    - **env**: Environment type (retail, airline, healthcare)
    - **task_split**: Task split (train, test, dev)
    
    **Returns:**
    - List of available tasks with metadata
    - Total task count for the environment/split
    """
    global service
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        return await service.list_tasks(request)
    
    except Exception as e:
        logging.error(f"Failed to list tasks: {str(e)}", exc_info=True)
        error_response = APIError(
            error_type="list_error", 
            message=str(e),
            timestamp=datetime.now().isoformat()
        )
        raise HTTPException(status_code=400, detail=error_response.model_dump())


async def _log_validation_request(request_data: dict, response_data: dict):
    """Background task to log validation requests."""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request_data,
            "response": {
                "status": response_data.get("status"),
                "metrics": response_data.get("metrics"),
                "execution_time": response_data.get("execution_time_seconds"),
            }
        }
        
        # Log to file or external service as needed
        logging.info(f"Validation request logged: {log_entry}")
        
    except Exception as e:
        logging.error(f"Failed to log validation request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    # Run the application
    uvicorn.run(
        "tau_bench.api.app:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )