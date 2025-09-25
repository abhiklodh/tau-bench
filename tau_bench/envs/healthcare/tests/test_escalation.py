# Copyright Sierra

"""
Unit tests for escalation tools in healthcare environment.
"""

import pytest
from typing import Dict, Any
from tau_bench.envs.healthcare.tools.escalation import TransferToMedicalStaff


class TestTransferToMedicalStaff:
    """Test cases for TransferToMedicalStaff tool."""
    
    def test_get_info_returns_correct_structure(self):
        """Test that get_info returns the correct function structure."""
        info = TransferToMedicalStaff.get_info()
        
        assert info["type"] == "function"
        assert info["function"]["name"] == "transfer_to_medical_staff"
        assert "description" in info["function"]
        assert info["function"]["parameters"]["type"] == "object"
        assert "reason" in info["function"]["parameters"]["properties"]
        assert "urgency" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["reason"]
        
        # Check urgency enum values
        urgency_enum = info["function"]["parameters"]["properties"]["urgency"]["enum"]
        expected_urgency_levels = ["low", "medium", "high", "emergency"]
        assert urgency_enum == expected_urgency_levels
    
    def test_invoke_with_reason_only(self, healthcare_data: Dict[str, Any]):
        """Test invoke with only reason (default urgency)."""
        reason = "Patient needs specialist consultation"
        result = TransferToMedicalStaff.invoke(healthcare_data, reason)
        
        assert "Transferring to medical staff" in result
        assert reason in result
        assert "Urgency: medium" in result  # Default urgency
        assert "qualified medical professional will assist" in result
    
    def test_invoke_with_reason_and_urgency(self, healthcare_data: Dict[str, Any]):
        """Test invoke with reason and custom urgency."""
        reason = "Patient experiencing chest pain"
        urgency = "emergency"
        result = TransferToMedicalStaff.invoke(healthcare_data, reason, urgency)
        
        assert "Transferring to medical staff" in result
        assert reason in result
        assert "Urgency: emergency" in result
        assert "qualified medical professional will assist" in result
    
    def test_invoke_with_low_urgency(self, healthcare_data: Dict[str, Any]):
        """Test invoke with low urgency."""
        reason = "General question about medication"
        urgency = "low"
        result = TransferToMedicalStaff.invoke(healthcare_data, reason, urgency)
        
        assert "Transferring to medical staff" in result
        assert reason in result
        assert "Urgency: low" in result
    
    def test_invoke_with_high_urgency(self, healthcare_data: Dict[str, Any]):
        """Test invoke with high urgency."""
        reason = "Patient reporting severe side effects"
        urgency = "high"
        result = TransferToMedicalStaff.invoke(healthcare_data, reason, urgency)
        
        assert "Transferring to medical staff" in result
        assert reason in result
        assert "Urgency: high" in result
    
    def test_invoke_with_medium_urgency(self, healthcare_data: Dict[str, Any]):
        """Test invoke with medium urgency."""
        reason = "Need clarification on test results"
        urgency = "medium"
        result = TransferToMedicalStaff.invoke(healthcare_data, reason, urgency)
        
        assert "Transferring to medical staff" in result
        assert reason in result
        assert "Urgency: medium" in result
    
    def test_invoke_with_empty_reason(self, healthcare_data: Dict[str, Any]):
        """Test invoke with empty reason."""
        reason = ""
        result = TransferToMedicalStaff.invoke(healthcare_data, reason)
        
        assert "Transferring to medical staff" in result
        assert "Reason: " in result  # Empty reason still appears
        assert "Urgency: medium" in result
    
    def test_invoke_with_long_reason(self, healthcare_data: Dict[str, Any]):
        """Test invoke with a long reason."""
        reason = ("Patient has complex medical history with multiple conditions "
                 "and requires comprehensive review by multiple specialists "
                 "to determine the best treatment approach")
        result = TransferToMedicalStaff.invoke(healthcare_data, reason)
        
        assert "Transferring to medical staff" in result
        assert reason in result
        assert "Urgency: medium" in result
    
    def test_invoke_does_not_modify_data(self, healthcare_data: Dict[str, Any]):
        """Test that invoke does not modify the healthcare data."""
        original_data = healthcare_data.copy()
        reason = "Test transfer"
        TransferToMedicalStaff.invoke(healthcare_data, reason)
        
        # Data should remain unchanged
        assert healthcare_data == original_data