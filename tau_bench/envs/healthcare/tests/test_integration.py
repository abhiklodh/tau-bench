# Copyright Sierra

"""
Integration tests for healthcare environment tools.
These tests verify that tools work together correctly and with the actual data.
"""

import pytest
from typing import Dict, Any
from tau_bench.envs.healthcare.tools import ALL_TOOLS
from tau_bench.envs.healthcare.tools.patient_management import GetPatientInfo
from tau_bench.envs.healthcare.tools.appointment_management import (
    GetAppointmentDetails, ScheduleAppointment, CancelAppointment
)
from tau_bench.envs.healthcare.tools.medical_records import GetTestResults
from tau_bench.envs.healthcare.tools.escalation import TransferToMedicalStaff


class TestHealthcareToolsIntegration:
    """Integration tests for healthcare tools."""
    
    def test_all_tools_imported_correctly(self):
        """Test that all tools are properly imported in ALL_TOOLS."""
        expected_tools = [
            GetPatientInfo,
            ScheduleAppointment, 
            GetAppointmentDetails,
            CancelAppointment,
            GetTestResults,
            TransferToMedicalStaff,
        ]
        
        assert len(ALL_TOOLS) == len(expected_tools)
        for tool in expected_tools:
            assert tool in ALL_TOOLS
    
    def test_all_tools_have_get_info_method(self):
        """Test that all tools implement the get_info method."""
        for tool in ALL_TOOLS:
            info = tool.get_info()
            assert isinstance(info, dict)
            assert "type" in info
            assert info["type"] == "function"
            assert "function" in info
            assert "name" in info["function"]
            assert "description" in info["function"]
            assert "parameters" in info["function"]
    
    def test_all_tools_have_invoke_method(self, healthcare_data: Dict[str, Any]):
        """Test that all tools implement the invoke method."""
        for tool in ALL_TOOLS:
            assert hasattr(tool, 'invoke')
            assert callable(getattr(tool, 'invoke'))
    
    def test_patient_workflow_complete_journey(self, healthcare_data: Dict[str, Any]):
        """Test a complete patient workflow using multiple tools."""
        patient_id = "PAT001"
        
        # 1. Get patient information
        patient_info = GetPatientInfo.invoke(healthcare_data, patient_id)
        assert "John Smith" in patient_info
        
        # 2. Check existing appointments
        appointments = GetAppointmentDetails.invoke(healthcare_data, patient_id)
        assert "APT001" in appointments
        
        # 3. Check test results
        test_results = GetTestResults.invoke(healthcare_data, patient_id)
        assert "Blood Work" in test_results
        assert "Normal" in test_results
        
        # 4. Schedule a new appointment
        new_appointment = ScheduleAppointment.invoke(
            healthcare_data, patient_id, "Dr. Smith", "2024-08-15", "3:00 PM", "Follow-up"
        )
        assert "scheduled for patient PAT001" in new_appointment
        assert "APT003" in new_appointment
        
        # 5. Verify new appointment shows up in patient's appointments
        updated_appointments = GetAppointmentDetails.invoke(healthcare_data, patient_id)
        assert "APT003" in updated_appointments
        assert "Dr. Smith" in updated_appointments
    
    def test_appointment_cancellation_workflow(self, healthcare_data: Dict[str, Any]):
        """Test appointment scheduling and cancellation workflow."""
        patient_id = "PAT002"
        
        # 1. Schedule a new appointment
        new_appointment = ScheduleAppointment.invoke(
            healthcare_data, patient_id, "Dr. Jones", "2024-09-01", "11:00 AM", "Consultation"
        )
        new_apt_id = "APT003"  # Should be the third appointment
        assert new_apt_id in new_appointment
        
        # 2. Verify appointment exists
        appointment_details = GetAppointmentDetails.invoke(
            healthcare_data, patient_id, new_apt_id
        )
        assert "Dr. Jones" in appointment_details
        assert "scheduled" in appointment_details
        
        # 3. Cancel the appointment
        cancellation = CancelAppointment.invoke(healthcare_data, new_apt_id)
        assert "has been cancelled" in cancellation
        
        # 4. Verify appointment is cancelled
        updated_details = GetAppointmentDetails.invoke(
            healthcare_data, patient_id, new_apt_id
        )
        assert "cancelled" in updated_details
    
    def test_escalation_scenarios(self, healthcare_data: Dict[str, Any]):
        """Test different escalation scenarios."""
        # Test routine escalation
        routine_transfer = TransferToMedicalStaff.invoke(
            healthcare_data, "Patient has questions about medication dosage"
        )
        assert "Urgency: medium" in routine_transfer
        
        # Test emergency escalation
        emergency_transfer = TransferToMedicalStaff.invoke(
            healthcare_data, "Patient experiencing severe allergic reaction", "emergency"
        )
        assert "Urgency: emergency" in emergency_transfer
        
        # Test high priority escalation
        high_priority_transfer = TransferToMedicalStaff.invoke(
            healthcare_data, "Patient reports worsening symptoms", "high"
        )
        assert "Urgency: high" in high_priority_transfer
    
    def test_patient_data_consistency(self, healthcare_data: Dict[str, Any]):
        """Test that patient data remains consistent across different tool calls."""
        patient_id = "PAT001"
        
        # Get patient info multiple times
        info1 = GetPatientInfo.invoke(healthcare_data, patient_id)
        info2 = GetPatientInfo.invoke(healthcare_data, patient_id)
        
        assert info1 == info2
        
        # Get appointments multiple times
        appointments1 = GetAppointmentDetails.invoke(healthcare_data, patient_id)
        appointments2 = GetAppointmentDetails.invoke(healthcare_data, patient_id)
        
        assert appointments1 == appointments2
    
    def test_nonexistent_patient_across_tools(self, healthcare_data: Dict[str, Any]):
        """Test how all tools handle non-existent patients."""
        invalid_patient = "NONEXISTENT"
        
        # Patient info should return not found
        patient_info = GetPatientInfo.invoke(healthcare_data, invalid_patient)
        assert "not found" in patient_info
        
        # Appointments should return no appointments found
        appointments = GetAppointmentDetails.invoke(healthcare_data, invalid_patient)
        assert "No appointments found" in appointments
        
        # Test results should return no results found
        test_results = GetTestResults.invoke(healthcare_data, invalid_patient)
        assert "No test results found" in test_results
        
        # Scheduling should still work (doesn't validate patient exists)
        schedule_result = ScheduleAppointment.invoke(
            healthcare_data, invalid_patient, "Dr. Test", "2024-12-01", "9:00 AM", "Checkup"
        )
        assert "scheduled for patient NONEXISTENT" in schedule_result
    
    def test_data_modification_persistence(self, healthcare_data: Dict[str, Any]):
        """Test that modifications to data persist across tool calls."""
        patient_id = "PAT001"
        
        # Schedule appointment
        ScheduleAppointment.invoke(
            healthcare_data, patient_id, "Dr. Persistence", "2024-10-01", "2:00 PM", "Test"
        )
        
        # Verify it appears in subsequent calls
        appointments = GetAppointmentDetails.invoke(healthcare_data, patient_id)
        assert "Dr. Persistence" in appointments
        
        # Cancel an existing appointment
        CancelAppointment.invoke(healthcare_data, "APT001")
        
        # Verify cancellation persists
        updated_appointments = GetAppointmentDetails.invoke(healthcare_data, patient_id, "APT001")
        assert "cancelled" in updated_appointments