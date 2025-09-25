# Copyright Sierra

"""
Unit tests for appointment management tools in healthcare environment.
"""

import pytest
from typing import Dict, Any
from tau_bench.envs.healthcare.tools.appointment_management import (
    GetAppointmentDetails, ScheduleAppointment, CancelAppointment
)


class TestGetAppointmentDetails:
    """Test cases for GetAppointmentDetails tool."""
    
    def test_get_info_returns_correct_structure(self):
        """Test that get_info returns the correct function structure."""
        info = GetAppointmentDetails.get_info()
        
        assert info["type"] == "function"
        assert info["function"]["name"] == "get_appointment_details"
        assert "description" in info["function"]
        assert info["function"]["parameters"]["type"] == "object"
        assert "patient_id" in info["function"]["parameters"]["properties"]
        assert info["function"]["parameters"]["required"] == ["patient_id"]
    
    def test_invoke_with_valid_patient_id_only(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str
    ):
        """Test invoke with only patient ID (get all appointments)."""
        result = GetAppointmentDetails.invoke(healthcare_data, sample_patient_id)
        
        assert "APT001" in result
        assert "Dr. Williams" in result
        assert "2025-09-22" in result
        assert "2:00 PM" in result
        assert "General Checkup" in result
        assert "scheduled" in result
    
    def test_invoke_with_valid_appointment_id(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str, sample_appointment_id: str
    ):
        """Test invoke with valid patient and appointment ID."""
        result = GetAppointmentDetails.invoke(
            healthcare_data, sample_patient_id, sample_appointment_id
        )
        
        assert "APT001" in result
        assert "PAT001" in result
        assert "Dr. Williams" in result
        assert "2025-09-22" in result
        assert "General Checkup" in result
    
    def test_invoke_with_invalid_patient_id(
        self, healthcare_data: Dict[str, Any], invalid_patient_id: str
    ):
        """Test invoke with invalid patient ID."""
        result = GetAppointmentDetails.invoke(healthcare_data, invalid_patient_id)
        
        assert "No appointments found for patient INVALID_ID" in result
    
    def test_invoke_with_invalid_appointment_id(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str, invalid_appointment_id: str
    ):
        """Test invoke with invalid appointment ID."""
        result = GetAppointmentDetails.invoke(
            healthcare_data, sample_patient_id, invalid_appointment_id
        )
        
        assert "Appointment INVALID_APT not found" in result
    
    def test_invoke_with_mismatched_patient_appointment(
        self, healthcare_data: Dict[str, Any]
    ):
        """Test invoke with appointment that doesn't belong to the patient."""
        # APT001 belongs to PAT001, testing with PAT002
        result = GetAppointmentDetails.invoke(healthcare_data, "PAT002", "APT001")
        
        assert "Appointment APT001 does not belong to patient PAT002" in result
    
    def test_invoke_second_patient_appointments(self, healthcare_data: Dict[str, Any]):
        """Test getting appointments for second patient."""
        result = GetAppointmentDetails.invoke(healthcare_data, "PAT002")
        
        assert "APT002" in result
        assert "Dr. Brown" in result
        assert "Follow-up" in result


class TestScheduleAppointment:
    """Test cases for ScheduleAppointment tool."""
    
    def test_get_info_returns_correct_structure(self):
        """Test that get_info returns the correct function structure."""
        info = ScheduleAppointment.get_info()
        
        assert info["type"] == "function"
        assert info["function"]["name"] == "schedule_appointment"
        assert "description" in info["function"]
        required_params = info["function"]["parameters"]["required"]
        assert all(param in required_params for param in 
                  ["patient_id", "doctor", "date", "time", "type"])
    
    def test_invoke_schedule_new_appointment(
        self, healthcare_data: Dict[str, Any], sample_patient_id: str
    ):
        """Test scheduling a new appointment."""
        result = ScheduleAppointment.invoke(
            healthcare_data, 
            sample_patient_id, 
            "Dr. Smith", 
            "2024-06-15", 
            "10:00 AM", 
            "Consultation"
        )
        
        assert "APT003" in result  # Should be the third appointment
        assert "scheduled for patient PAT001" in result
        assert "Dr. Smith" in result
        assert "2024-06-15" in result
        assert "10:00 AM" in result
        assert "Consultation" in result
        
        # Verify appointment was added to data
        assert "APT003" in healthcare_data["appointments"]
        new_apt = healthcare_data["appointments"]["APT003"]
        assert new_apt["patient_id"] == sample_patient_id
        assert new_apt["doctor"] == "Dr. Smith"
        assert new_apt["status"] == "scheduled"
    
    def test_invoke_schedule_multiple_appointments(self, healthcare_data: Dict[str, Any]):
        """Test scheduling multiple appointments generates unique IDs."""
        result1 = ScheduleAppointment.invoke(
            healthcare_data, "PAT001", "Dr. A", "2024-07-01", "9:00 AM", "Checkup"
        )
        result2 = ScheduleAppointment.invoke(
            healthcare_data, "PAT002", "Dr. B", "2024-07-02", "11:00 AM", "Surgery"
        )
        
        assert "APT003" in result1
        assert "APT004" in result2
        assert "APT003" in healthcare_data["appointments"]
        assert "APT004" in healthcare_data["appointments"]


class TestCancelAppointment:
    """Test cases for CancelAppointment tool."""
    
    def test_get_info_returns_correct_structure(self):
        """Test that get_info returns the correct function structure."""
        info = CancelAppointment.get_info()
        
        assert info["type"] == "function"
        assert info["function"]["name"] == "cancel_appointment"
        assert "description" in info["function"]
        assert info["function"]["parameters"]["required"] == ["appointment_id"]
    
    def test_invoke_cancel_valid_appointment(
        self, healthcare_data: Dict[str, Any], sample_appointment_id: str
    ):
        """Test canceling a valid appointment."""
        # Verify appointment exists and is scheduled
        assert healthcare_data["appointments"][sample_appointment_id]["status"] == "scheduled"
        
        result = CancelAppointment.invoke(healthcare_data, sample_appointment_id)
        
        assert "APT001 has been cancelled" in result
        # Verify appointment status was changed
        assert healthcare_data["appointments"][sample_appointment_id]["status"] == "cancelled"
    
    def test_invoke_cancel_invalid_appointment(
        self, healthcare_data: Dict[str, Any], invalid_appointment_id: str
    ):
        """Test canceling an invalid appointment."""
        result = CancelAppointment.invoke(healthcare_data, invalid_appointment_id)
        
        assert "Appointment INVALID_APT not found" in result
    
    def test_invoke_cancel_second_appointment(self, healthcare_data: Dict[str, Any]):
        """Test canceling the second appointment."""
        result = CancelAppointment.invoke(healthcare_data, "APT002")
        
        assert "APT002 has been cancelled" in result
        assert healthcare_data["appointments"]["APT002"]["status"] == "cancelled"