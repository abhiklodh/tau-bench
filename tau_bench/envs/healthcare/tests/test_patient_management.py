# Copyright Sierra

"""
Unit tests for patient management tools in healthcare environment.
"""

import pytest
from typing import Dict, Any
from tau_bench.envs.healthcare.tools.patient_management import GetPatientInfo


class TestGetPatientInfo:
    """Test cases for GetPatientInfo tool."""
    
    def test_get_info_returns_correct_structure(self):
        """Test that get_info returns the correct function structure."""
        info = GetPatientInfo.get_info()
        
        assert info["type"] == "function"
        assert info["function"]["name"] == "get_patient_info"
        assert "description" in info["function"]
        assert info["function"]["parameters"]["type"] == "object"
        assert "patient_id" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["patient_id"]
    
    def test_invoke_with_valid_patient_id(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str
    ):
        """Test invoke with a valid patient ID."""
        result = GetPatientInfo.invoke(healthcare_data, sample_patient_id)
        
        assert "John Smith" in result
        assert "1985-03-15" in result
        assert "555-0123" in result
        assert "john.smith@email.com" in result
        assert "Patient:" in result
    
    def test_invoke_with_invalid_patient_id(
        self, healthcare_data: Dict[str, Any], invalid_patient_id: str
    ):
        """Test invoke with an invalid patient ID."""
        result = GetPatientInfo.invoke(healthcare_data, invalid_patient_id)
        
        assert "Patient INVALID_ID not found." in result
    
    def test_invoke_with_second_patient(self, healthcare_data: Dict[str, Any]):
        """Test invoke with the second patient in the data."""
        result = GetPatientInfo.invoke(healthcare_data, "PAT002")
        
        assert "Sarah Johnson" in result
        assert "1992-07-22" in result
        assert "555-0456" in result
        assert "sarah.j@email.com" in result
    
    def test_invoke_with_empty_data(self, sample_patient_id: str):
        """Test invoke with empty data."""
        empty_data = {"patients": {}}
        result = GetPatientInfo.invoke(empty_data, sample_patient_id)
        
        assert "Patient PAT001 not found." in result
    
    def test_invoke_with_malformed_data(self, sample_patient_id: str):
        """Test invoke with malformed data structure."""
        malformed_data = {}
        result = GetPatientInfo.invoke(malformed_data, sample_patient_id)
        
        assert "Patient PAT001 not found." in result