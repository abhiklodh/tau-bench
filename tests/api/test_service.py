# Copyright Sierra

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from tau_bench.api.service import TauBenchAPIService
from tau_bench.api.models import TaskValidationRequest, EnvironmentType, AgentStrategy, TaskSplit, UserStrategy
from tau_bench.types import EnvRunResult


@pytest.fixture
def service():
    """Create a test service instance."""
    return TauBenchAPIService(log_dir="/tmp/test_results")


@pytest.fixture
def valid_request():
    """Create a valid validation request."""
    return TaskValidationRequest(
        model_provider="openai",
        model="gpt-4o",
        env=EnvironmentType.RETAIL,
        num_trials=1,
        start_index=0,
        end_index=1
    )


@pytest.fixture
def mock_results():
    """Create mock results for testing."""
    return [
        EnvRunResult(
            task_id=0,
            reward=1.0,
            info={"test": "data"},
            traj=[{"action": "test", "observation": "test"}],
            trial=0
        ),
        EnvRunResult(
            task_id=1,
            reward=0.5,
            info={"test": "data2"},
            traj=[{"action": "test2", "observation": "test2"}],
            trial=0
        )
    ]


class TestTauBenchAPIService:
    """Test the main API service."""
    
    def test_validate_request_valid(self, service, valid_request):
        """Test validation of a valid request."""
        errors = service.validate_request(valid_request)
        assert errors == []
    
    def test_validate_request_invalid_provider(self, service, valid_request):
        """Test validation with invalid model provider."""
        valid_request.model_provider = "invalid_provider"
        errors = service.validate_request(valid_request)
        assert len(errors) > 0
        assert "Invalid model provider" in errors[0]
    
    def test_validate_request_invalid_env(self, service, valid_request):
        """Test validation with invalid environment."""
        valid_request.env = "invalid_env"
        errors = service.validate_request(valid_request)
        assert len(errors) > 0
        assert "Invalid environment" in errors[0]
    
    def test_convert_to_run_config(self, service, valid_request):
        """Test conversion of API request to RunConfig."""
        config = service._convert_to_run_config(valid_request)
        
        assert config.model_provider == valid_request.model_provider
        assert config.model == valid_request.model
        assert config.env == valid_request.env.value
        assert config.num_trials == valid_request.num_trials
    
    def test_convert_results(self, service, mock_results):
        """Test conversion of results to API format."""
        api_results = service._convert_results(mock_results)
        
        assert len(api_results) == 2
        assert api_results[0].task_id == 0
        assert api_results[0].reward == 1.0
        assert api_results[0].success == True
        
        assert api_results[1].task_id == 1
        assert api_results[1].reward == 0.5
        assert api_results[1].success == True
    
    def test_calculate_metrics(self, service, mock_results):
        """Test metrics calculation."""
        metrics = service._calculate_metrics(mock_results)
        
        assert metrics.total_tasks == 2
        assert metrics.successful_tasks == 2
        assert metrics.failed_tasks == 0
        assert metrics.success_rate == 1.0
        assert metrics.average_reward == 0.75
    
    @pytest.mark.asyncio
    async def test_get_health(self, service):
        """Test health check endpoint."""
        health = await service.get_health()
        
        assert health.status == "healthy"
        assert health.version == "0.1.0"
        assert "retail" in health.supported_environments
        assert "airline" in health.supported_environments
        assert "healthcare" in health.supported_environments
    
    @pytest.mark.asyncio
    @patch('tau_bench.api.service.tau_run')
    async def test_validate_tasks_success(self, mock_run, service, valid_request, mock_results):
        """Test successful task validation."""
        mock_run.return_value = mock_results
        
        response = await service.validate_tasks(valid_request)
        
        assert response.status == "completed"
        assert len(response.results) == 2
        assert response.metrics.total_tasks == 2
        assert response.metrics.success_rate == 1.0
        assert len(response.errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_tasks_validation_error(self, service, valid_request):
        """Test validation with invalid request."""
        valid_request.model_provider = "invalid_provider"
        
        response = await service.validate_tasks(valid_request)
        
        assert response.status == "failed"
        assert len(response.errors) > 0
        assert "Invalid model provider" in response.errors[0]
    
    @pytest.mark.asyncio
    @patch('tau_bench.api.service.tau_run')
    async def test_validate_tasks_execution_error(self, mock_run, service, valid_request):
        """Test handling of execution errors."""
        mock_run.side_effect = Exception("Test error")
        
        response = await service.validate_tasks(valid_request)
        
        assert response.status == "failed"
        assert len(response.errors) > 0
        assert "Test error" in response.errors[0]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])