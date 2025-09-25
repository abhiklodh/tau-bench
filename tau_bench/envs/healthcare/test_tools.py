"""
Healthcare environment tool validation tests.

This module provides comprehensive tests for all healthcare domain tools
to ensure they behave correctly with the provided test data.
"""

import unittest
from tau_bench.envs.healthcare.data import load_data
from tau_bench.envs.healthcare.tools import (
    GetPatientInfo,
    ScheduleAppointment, 
    GetAppointmentDetails,
    CancelAppointment,
    GetTestResults,
    TransferToMedicalStaff
)


class TestHealthcareTools(unittest.TestCase):
    """Test suite for healthcare domain tools."""
    
    def setUp(self):
        """Set up test data for each test."""
        self.data = load_data()
        # Create a fresh copy of appointments for each test to avoid side effects
        self.original_appointments = self.data["appointments"].copy()
    
    def tearDown(self):
        """Clean up after each test."""
        # Restore original appointments data
        self.data["appointments"] = self.original_appointments.copy()
    
    def test_get_patient_info_valid_patient(self):
        """Test GetPatientInfo with valid patient ID."""
        result = GetPatientInfo.invoke(self.data, "PAT001")
        self.assertIn("John Smith", result)
        self.assertIn("1985-03-15", result)
        self.assertIn("555-0123", result)
        self.assertIn("john.smith@email.com", result)
    
    def test_get_patient_info_invalid_patient(self):
        """Test GetPatientInfo with invalid patient ID."""
        result = GetPatientInfo.invoke(self.data, "PAT999")
        self.assertEqual(result, "Patient PAT999 not found.")
    
    def test_get_patient_info_tool_schema(self):
        """Test GetPatientInfo tool schema is properly formatted."""
        info = GetPatientInfo.get_info()
        self.assertEqual(info["type"], "function")
        self.assertEqual(info["function"]["name"], "get_patient_info")
        self.assertIn("patient_id", info["function"]["parameters"]["properties"])
        self.assertIn("patient_id", info["function"]["parameters"]["required"])
    
    def test_schedule_appointment_valid_params(self):
        """Test ScheduleAppointment with valid parameters."""
        result = ScheduleAppointment.invoke(
            self.data, 
            "PAT001", 
            "Dr. Brown", 
            "2025-10-15", 
            "10:00 AM", 
            "Consultation"
        )
        self.assertIn("Appointment APT003 scheduled", result)
        self.assertIn("PAT001", result)
        self.assertIn("Dr. Brown", result)
        
        # Verify appointment was added to data
        self.assertIn("APT003", self.data["appointments"])
        appt = self.data["appointments"]["APT003"]
        self.assertEqual(appt["patient_id"], "PAT001")
        self.assertEqual(appt["doctor"], "Dr. Brown")
        self.assertEqual(appt["status"], "scheduled")
    
    def test_schedule_appointment_tool_schema(self):
        """Test ScheduleAppointment tool schema is properly formatted."""
        info = ScheduleAppointment.get_info()
        self.assertEqual(info["type"], "function")
        self.assertEqual(info["function"]["name"], "schedule_appointment")
        required_fields = ["patient_id", "doctor", "date", "time", "type"]
        for field in required_fields:
            self.assertIn(field, info["function"]["parameters"]["properties"])
            self.assertIn(field, info["function"]["parameters"]["required"])
    
    def test_get_appointment_details_by_patient_id(self):
        """Test GetAppointmentDetails with patient ID only."""
        result = GetAppointmentDetails.invoke(self.data, "PAT001")
        self.assertIn("Appointment APT001", result)
        self.assertIn("Dr. Williams", result)
        self.assertIn("2025-09-22", result)
        self.assertIn("General Checkup", result)
    
    def test_get_appointment_details_by_appointment_id(self):
        """Test GetAppointmentDetails with specific appointment ID."""
        result = GetAppointmentDetails.invoke(self.data, "PAT001", "APT001")
        self.assertIn("Appointment APT001", result)
        self.assertIn("PAT001", result)
        self.assertIn("Dr. Williams", result)
        self.assertIn("scheduled", result)
    
    def test_get_appointment_details_invalid_appointment(self):
        """Test GetAppointmentDetails with invalid appointment ID."""
        result = GetAppointmentDetails.invoke(self.data, "PAT001", "APT999")
        self.assertEqual(result, "Appointment APT999 not found.")
    
    def test_get_appointment_details_wrong_patient(self):
        """Test GetAppointmentDetails with wrong patient ID for appointment."""
        result = GetAppointmentDetails.invoke(self.data, "PAT002", "APT001")
        self.assertIn("does not belong to patient PAT002", result)
    
    def test_get_appointment_details_no_appointments(self):
        """Test GetAppointmentDetails for patient with no appointments."""
        result = GetAppointmentDetails.invoke(self.data, "PAT999")
        self.assertEqual(result, "No appointments found for patient PAT999.")
    
    def test_cancel_appointment_valid(self):
        """Test CancelAppointment with valid appointment ID."""
        result = CancelAppointment.invoke(self.data, "APT001")
        self.assertIn("Appointment APT001 has been cancelled", result)
        
        # Verify appointment status was updated
        self.assertEqual(self.data["appointments"]["APT001"]["status"], "cancelled")
    
    def test_cancel_appointment_invalid(self):
        """Test CancelAppointment with invalid appointment ID."""
        result = CancelAppointment.invoke(self.data, "APT999")
        self.assertEqual(result, "Appointment APT999 not found.")
    
    def test_get_test_results_by_patient_id(self):
        """Test GetTestResults with patient ID only."""
        result = GetTestResults.invoke(self.data, "PAT001")
        self.assertIn("Test TEST001", result)
        self.assertIn("Blood Work", result)
        self.assertIn("2024-01-30", result)
        self.assertIn("Normal", result)
    
    def test_get_test_results_by_test_id(self):
        """Test GetTestResults with specific test ID."""
        result = GetTestResults.invoke(self.data, "PAT001", "TEST001")
        self.assertIn("Test TEST001", result)
        self.assertIn("Blood Work", result)
        self.assertIn("Dr. Williams", result)
        self.assertIn("Normal", result)
    
    def test_get_test_results_invalid_test(self):
        """Test GetTestResults with invalid test ID."""
        result = GetTestResults.invoke(self.data, "PAT001", "TEST999")
        self.assertEqual(result, "Test TEST999 not found.")
    
    def test_get_test_results_wrong_patient(self):
        """Test GetTestResults with wrong patient ID for test."""
        result = GetTestResults.invoke(self.data, "PAT002", "TEST001")
        self.assertIn("does not belong to patient PAT002", result)
    
    def test_get_test_results_no_results(self):
        """Test GetTestResults for patient with no test results."""
        result = GetTestResults.invoke(self.data, "PAT002")
        self.assertEqual(result, "No test results found for patient PAT002.")
    
    def test_transfer_to_medical_staff_basic(self):
        """Test TransferToMedicalStaff with basic parameters."""
        result = TransferToMedicalStaff.invoke(self.data, "Patient needs specialist consultation")
        self.assertIn("Transferring to medical staff", result)
        self.assertIn("Patient needs specialist consultation", result)
        self.assertIn("Urgency: medium", result)
    
    def test_transfer_to_medical_staff_with_urgency(self):
        """Test TransferToMedicalStaff with custom urgency level."""
        result = TransferToMedicalStaff.invoke(
            self.data, 
            "Emergency medical situation", 
            "emergency"
        )
        self.assertIn("Transferring to medical staff", result)
        self.assertIn("Emergency medical situation", result)
        self.assertIn("Urgency: emergency", result)
    
    def test_transfer_to_medical_staff_tool_schema(self):
        """Test TransferToMedicalStaff tool schema includes urgency enum."""
        info = TransferToMedicalStaff.get_info()
        urgency_prop = info["function"]["parameters"]["properties"]["urgency"]
        expected_enum = ["low", "medium", "high", "emergency"]
        self.assertEqual(urgency_prop["enum"], expected_enum)
    
    def test_data_loading_integrity(self):
        """Test that data loading provides expected structure."""
        self.assertIn("patients", self.data)
        self.assertIn("appointments", self.data) 
        self.assertIn("test_results", self.data)
        
        # Verify patients data
        self.assertIn("PAT001", self.data["patients"])
        self.assertIn("PAT002", self.data["patients"])
        
        # Verify appointments data
        self.assertIn("APT001", self.data["appointments"])
        self.assertIn("APT002", self.data["appointments"])
        
        # Verify test results data
        self.assertIn("TEST001", self.data["test_results"])
    
    def test_all_tools_have_proper_schemas(self):
        """Test that all tools have properly formatted schemas."""
        tools = [
            GetPatientInfo,
            ScheduleAppointment,
            GetAppointmentDetails, 
            CancelAppointment,
            GetTestResults,
            TransferToMedicalStaff
        ]
        
        for tool in tools:
            with self.subTest(tool=tool.__name__):
                info = tool.get_info()
                self.assertEqual(info["type"], "function")
                self.assertIn("function", info)
                self.assertIn("name", info["function"])
                self.assertIn("description", info["function"])
                self.assertIn("parameters", info["function"])
                self.assertIn("type", info["function"]["parameters"])
                self.assertIn("properties", info["function"]["parameters"])


class TestHealthcareDataIntegrity(unittest.TestCase):
    """Test suite for healthcare data integrity."""
    
    def setUp(self):
        """Set up test data."""
        self.data = load_data()
    
    def test_patient_data_completeness(self):
        """Test that patient records have all required fields."""
        for patient_id, patient in self.data["patients"].items():
            with self.subTest(patient_id=patient_id):
                required_fields = ["name", "dob", "phone", "email"]
                for field in required_fields:
                    self.assertIn(field, patient, 
                                f"Patient {patient_id} missing {field}")
    
    def test_appointment_data_completeness(self):
        """Test that appointment records have all required fields.""" 
        for appt_id, appt in self.data["appointments"].items():
            with self.subTest(appt_id=appt_id):
                required_fields = ["patient_id", "doctor", "date", "time", "type", "status"]
                for field in required_fields:
                    self.assertIn(field, appt,
                                f"Appointment {appt_id} missing {field}")
    
    def test_test_results_data_completeness(self):
        """Test that test result records have all required fields."""
        for test_id, test in self.data["test_results"].items():
            with self.subTest(test_id=test_id):
                required_fields = ["patient_id", "test_type", "date", "results", "doctor"]
                for field in required_fields:
                    self.assertIn(field, test,
                                f"Test result {test_id} missing {field}")
    
    def test_data_relationships(self):
        """Test that data relationships are consistent."""
        # All appointments should reference valid patients
        for appt_id, appt in self.data["appointments"].items():
            patient_id = appt["patient_id"]
            self.assertIn(patient_id, self.data["patients"],
                        f"Appointment {appt_id} references invalid patient {patient_id}")
        
        # All test results should reference valid patients  
        for test_id, test in self.data["test_results"].items():
            patient_id = test["patient_id"]
            self.assertIn(patient_id, self.data["patients"],
                        f"Test {test_id} references invalid patient {patient_id}")


def run_healthcare_tests():
    """Run all healthcare environment tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHealthcareTools))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthcareDataIntegrity))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_healthcare_tests()