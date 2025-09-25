# Healthcare Environment Tests

This directory contains comprehensive unit and integration tests for the healthcare environment tools in tau-bench.

## Overview

The test suite validates all healthcare tools and their interactions with the healthcare data, ensuring that:
- Each tool behaves correctly with valid and invalid inputs
- Tools properly handle edge cases and error conditions
- Data modifications persist correctly across tool calls
- Tool integration works as expected in realistic workflows

## Test Structure

### Unit Tests
- `test_patient_management.py` - Tests for the GetPatientInfo tool
- `test_appointment_management.py` - Tests for appointment-related tools (GetAppointmentDetails, ScheduleAppointment, CancelAppointment)
- `test_medical_records.py` - Tests for the GetTestResults tool
- `test_escalation.py` - Tests for the TransferToMedicalStaff tool

### Integration Tests
- `test_integration.py` - End-to-end workflow tests and cross-tool validation

## Tools Tested

### Patient Management
- **GetPatientInfo**: Retrieves patient information by patient ID
  - Tests valid/invalid patient IDs
  - Tests data structure integrity
  - Tests error handling for missing data

### Appointment Management
- **GetAppointmentDetails**: Retrieves appointment information
  - Tests with patient ID only (all appointments)
  - Tests with specific appointment ID
  - Tests patient-appointment ownership validation
- **ScheduleAppointment**: Creates new appointments
  - Tests appointment creation
  - Tests unique ID generation
  - Tests data persistence
- **CancelAppointment**: Cancels existing appointments
  - Tests valid cancellation
  - Tests invalid appointment handling
  - Tests status updates

### Medical Records
- **GetTestResults**: Retrieves patient test results
  - Tests with patient ID only (all results)
  - Tests with specific test ID
  - Tests patient-test ownership validation
  - Tests handling of patients with no results

### Escalation
- **TransferToMedicalStaff**: Escalates issues to medical staff
  - Tests default urgency handling
  - Tests all urgency levels (low, medium, high, emergency)
  - Tests reason formatting
  - Tests data immutability

## Running the Tests

### Run all healthcare tests:
```bash
python -m pytest tau_bench/envs/healthcare/tests/ -v
```

### Run specific test files:
```bash
python -m pytest tau_bench/envs/healthcare/tests/test_patient_management.py -v
python -m pytest tau_bench/envs/healthcare/tests/test_appointment_management.py -v
python -m pytest tau_bench/envs/healthcare/tests/test_medical_records.py -v
python -m pytest tau_bench/envs/healthcare/tests/test_escalation.py -v
python -m pytest tau_bench/envs/healthcare/tests/test_integration.py -v
```

### Run with coverage:
```bash
python -m pytest tau_bench/envs/healthcare/tests/ --cov=tau_bench.envs.healthcare.tools
```

## Test Data

The tests use the actual healthcare data from the `data/` directory:
- `patients.json` - Patient information (PAT001, PAT002)
- `appointments.json` - Existing appointments (APT001, APT002)
- `test_results.json` - Medical test results (TEST001)

## Fixtures

Common test fixtures are defined in `conftest.py`:
- `healthcare_data`: Loads the complete healthcare dataset
- `sample_patient_id`: Valid patient ID (PAT001)
- `invalid_patient_id`: Invalid patient ID for error testing
- `sample_appointment_id`: Valid appointment ID (APT001)
- `invalid_appointment_id`: Invalid appointment ID for error testing
- `sample_test_id`: Valid test ID (TEST001)
- `invalid_test_id`: Invalid test ID for error testing

## Integration Test Scenarios

The integration tests cover realistic workflows:

1. **Complete Patient Journey**: Get patient info → Check appointments → View test results → Schedule new appointment
2. **Appointment Management**: Schedule appointment → Verify creation → Cancel appointment → Verify cancellation
3. **Escalation Scenarios**: Test different urgency levels and transfer reasons
4. **Data Consistency**: Ensure data remains consistent across multiple tool calls
5. **Error Handling**: Test how all tools handle non-existent patients
6. **Data Persistence**: Verify that data modifications persist across tool calls

## Benefits

This comprehensive test suite provides:
- **Validation**: Ensures all tools work correctly with the provided data
- **Regression Prevention**: Catches breaking changes to tool behavior
- **Documentation**: Tests serve as examples of correct tool usage
- **Confidence**: Validates that tasks executed by models will have access to correctly behaving tools
- **Quality Assurance**: Ensures the logic is sound before deployment

## Coverage

The test suite achieves comprehensive coverage of:
- All 6 healthcare tools
- Valid and invalid input scenarios
- Edge cases and error conditions
- Tool integration patterns
- Data modification workflows
- Error handling and recovery