# Copyright Sierra

"""
Pytest configuration and fixtures for healthcare environment tests.
"""

import pytest
from typing import Dict, Any
from tau_bench.envs.healthcare.data import load_data


@pytest.fixture
def healthcare_data() -> Dict[str, Any]:
    """Load healthcare test data."""
    return load_data()


@pytest.fixture
def sample_patient_id() -> str:
    """Sample valid patient ID."""
    return "PAT001"


@pytest.fixture
def invalid_patient_id() -> str:
    """Sample invalid patient ID."""
    return "INVALID_ID"


@pytest.fixture
def sample_appointment_id() -> str:
    """Sample valid appointment ID."""
    return "APT001"


@pytest.fixture
def invalid_appointment_id() -> str:
    """Sample invalid appointment ID."""
    return "INVALID_APT"


@pytest.fixture
def sample_test_id() -> str:
    """Sample valid test ID."""
    return "TEST001"


@pytest.fixture
def invalid_test_id() -> str:
    """Sample invalid test ID."""
    return "INVALID_TEST"