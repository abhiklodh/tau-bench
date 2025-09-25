# Copyright Sierra

"""
Unit tests for medical records tools in healthcare environment.
"""

import pytest
from typing import Dict, Any
from tau_bench.envs.healthcare.tools.medical_records import GetTestResults


class TestGetTestResults:
    """Test cases for GetTestResults tool."""
    
    def test_get_info_returns_correct_structure(self):
        """Test that get_info returns the correct function structure."""
        info = GetTestResults.get_info()
        
        assert info["type"] == "function"
        assert info["function"]["name"] == "get_test_results"
        assert "description" in info["function"]
        assert info["function"]["parameters"]["type"] == "object"
        assert "patient_id" in info["function"]["parameters"]["properties"]
        assert "test_id" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["patient_id"]
    
    def test_invoke_with_valid_patient_id_only(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str
    ):
        """Test invoke with only patient ID (get all test results)."""
        result = GetTestResults.invoke(healthcare_data, sample_patient_id)
        
        assert "TEST001" in result
        assert "Blood Work" in result
        assert "2024-01-30" in result
        assert "Normal" in result
    
    def test_invoke_with_valid_test_id(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str, sample_test_id: str
    ):
        """Test invoke with valid patient and test ID."""
        result = GetTestResults.invoke(healthcare_data, sample_patient_id, sample_test_id)
        
        assert "TEST001" in result
        assert "Blood Work" in result
        assert "2024-01-30" in result
        assert "Normal" in result
        assert "Dr. Williams" in result
    
    def test_invoke_with_invalid_patient_id(
        self, healthcare_data: Dict[str, Any], invalid_patient_id: str
    ):
        """Test invoke with invalid patient ID."""
        result = GetTestResults.invoke(healthcare_data, invalid_patient_id)
        
        assert "No test results found for patient INVALID_ID" in result
    
    def test_invoke_with_invalid_test_id(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str, invalid_test_id: str
    ):
        """Test invoke with invalid test ID."""
        result = GetTestResults.invoke(healthcare_data, sample_patient_id, invalid_test_id)
        
        assert "Test INVALID_TEST not found" in result
    
    def test_invoke_with_mismatched_patient_test(self, healthcare_data: Dict[str, Any]):
        """Test invoke with test that doesn't belong to the patient."""
        # TEST001 belongs to PAT001, testing with PAT002
        result = GetTestResults.invoke(healthcare_data, "PAT002", "TEST001")
        
        assert "Test TEST001 does not belong to patient PAT002" in result
    
    def test_invoke_with_patient_no_tests(self, healthcare_data: Dict[str, Any]):
        """Test invoke with patient who has no test results."""
        result = GetTestResults.invoke(healthcare_data, "PAT002")
        
        assert "No test results found for patient PAT002" in result
    
    def test_invoke_with_empty_test_data(self, sample_patient_id: str):
        """Test invoke with empty test results data."""
        empty_data = {"test_results": {}}
        result = GetTestResults.invoke(empty_data, sample_patient_id)
        
        assert "No test results found for patient PAT001" in result
    
    def test_invoke_with_malformed_data(self, sample_patient_id: str):
        """Test invoke with malformed data structure."""
        malformed_data = {}
        result = GetTestResults.invoke(malformed_data, sample_patient_id)
        
        assert "No test results found for patient PAT001" in result