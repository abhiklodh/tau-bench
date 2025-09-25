# Environment Validation Framework

This document describes the environment validation framework added to τ-bench to ensure tools and data are working correctly before running model tests.

## Overview

The validation framework automatically runs comprehensive tests for each environment (healthcare, retail, airline) before model testing begins. This ensures that:

- All tools work correctly with the provided test data
- Tool schemas are properly formatted
- Data integrity is maintained
- Edge cases and error conditions are handled properly

## Usage

### Automatic Validation

Environment validation runs automatically when you use the main run script:

```bash
python run.py --env healthcare --model gpt-4o --model-provider openai ...
```

The system will:
1. ✅ Run validation tests for the specified environment
2. ✅ Only proceed to model testing if validation passes  
3. ❌ Abort with clear error messages if validation fails

### Manual Validation

You can also run validation manually:

```bash
# Validate a specific environment
python -m tau_bench.validate_environments healthcare
python -m tau_bench.validate_environments retail 
python -m tau_bench.validate_environments airline

# Validate all environments
python -m tau_bench.validate_environments all
```

## Test Coverage

### Healthcare Environment (Comprehensive)
- **Tools Tested**: 6 tools with 26+ test cases
  - `GetPatientInfo`: Valid/invalid patient IDs, schema validation
  - `ScheduleAppointment`: Valid parameters, data persistence
  - `GetAppointmentDetails`: Patient/appointment ID queries, error cases
  - `CancelAppointment`: Valid/invalid appointment cancellation
  - `GetTestResults`: Patient/test ID queries, missing data handling
  - `TransferToMedicalStaff`: Basic and urgency-level transfers
- **Data Integrity**: Patient, appointment, and test result data validation
- **Schema Validation**: All tool function schemas properly formatted

### Retail Environment (Dummy Tests)
- **Status**: Framework ready, placeholder tests implemented
- **TODO**: Implement comprehensive tool and data validation tests

### Airline Environment (Dummy Tests)  
- **Status**: Framework ready, placeholder tests implemented
- **TODO**: Implement comprehensive tool and data validation tests

## Test Results Example

```
============================================================
VALIDATING HEALTHCARE ENVIRONMENT
============================================================
test_get_patient_info_valid_patient ... ok
test_get_patient_info_invalid_patient ... ok
test_schedule_appointment_valid_params ... ok
test_cancel_appointment_valid ... ok
[... 22 more tests ...]

----------------------------------------------------------------------
Ran 26 tests in 0.005s

OK
✅ Healthcare environment validation PASSED
✅ Healthcare environment validation passed! Proceeding with model testing...
```

## Benefits

1. **Early Error Detection**: Catch environment issues before expensive model runs
2. **Data Integrity**: Ensure test data is complete and properly formatted
3. **Tool Reliability**: Verify all tools work correctly with edge cases
4. **Development Safety**: Prevent broken environments from affecting model evaluation
5. **Clear Diagnostics**: Detailed error reporting when validation fails

## Implementation Details

- **Test Framework**: Python's built-in `unittest` framework
- **Test Location**: `tau_bench/envs/{env_name}/test_tools.py`
- **Integration**: Automatic validation in `tau_bench/run.py`
- **CLI Tool**: `tau_bench/validate_environments.py`

## Future Enhancements

- Complete comprehensive tests for retail and airline environments
- Add performance benchmarking for tool execution times
- Implement data consistency checks across environments
- Add configurable validation levels (basic, comprehensive)