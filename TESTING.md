# Tool Testing Infrastructure

This document describes the comprehensive testing infrastructure added to validate tools in each environment (retail and airline) to ensure they behave correctly with the provided JSON data.

## Overview

The testing infrastructure provides:

1. **Unit tests** for each tool in both retail and airline environments
2. **Integration tests** that validate environment-wide functionality  
3. **Base test classes** that provide common testing patterns
4. **Test runners** for easy execution of all tests

## Structure

```
tests/
├── __init__.py                     # Test package initialization
├── test_integration.py             # Integration tests across environments
├── envs/
│   ├── __init__.py
│   ├── base_test.py               # Base test classes
│   ├── retail/
│   │   ├── __init__.py
│   │   └── test_tools.py          # Retail environment tool tests
│   └── airline/
│       ├── __init__.py
│       └── test_tools.py          # Airline environment tool tests
└── test_tools.py                   # Test runner script (in project root)
```

## Running Tests

### Using the Test Runner (Recommended)

The project includes a convenient test runner script:

```bash
# Run all tests for both environments
python test_tools.py

# Run tests for specific environment only
python test_tools.py retail
python test_tools.py airline
```

### Using pytest directly

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific environment tests
python -m pytest tests/envs/retail/test_tools.py -v
python -m pytest tests/envs/airline/test_tools.py -v

# Run integration tests
python -m pytest tests/test_integration.py -v
```

## Test Categories

### 1. Unit Tests for Individual Tools

Each tool class has comprehensive unit tests covering:

- **Tool info structure validation**: Ensures `get_info()` returns proper OpenAI function schema
- **Basic invocation**: Tests that `invoke()` method works with environment data
- **Parameter validation**: Tests behavior with invalid/missing parameters
- **Expected behavior**: Tests tool-specific functionality with real data scenarios
- **Error handling**: Tests graceful handling of edge cases

#### Example: GetUserDetails Tool Tests

```python
class TestGetUserDetails(BaseToolTest):
    def test_get_existing_user(self):
        # Test retrieving valid user data
    
    def test_get_nonexistent_user(self):
        # Test error handling for missing users
        
    def test_tool_info(self):
        # Test function schema structure
```

### 2. Environment-Level Tests  

Each environment (retail/airline) has comprehensive tests covering:

- **Data structure validation**: Ensures loaded data has expected format
- **Tool uniqueness**: Verifies all tools have unique names
- **Tool instantiation**: Tests all tools can be created and work with environment data
- **Environment-specific functionality**: Tests domain-specific requirements

#### Retail Environment (16 tools tested)
- User management tools (get_user_details, find_user_id_by_name_zip, find_user_id_by_email)  
- Order management tools (get_order_details, cancel_pending_order, modify_pending_order_*)
- Product tools (get_product_details, list_all_product_types)
- Utility tools (calculate, think, transfer_to_human_agents)

#### Airline Environment (14 tools tested)
- User management tools (get_user_details)
- Reservation tools (get_reservation_details, book_reservation, cancel_reservation)  
- Flight search tools (search_direct_flight, search_onestop_flight)
- Airport tools (list_all_airports)
- Utility tools (calculate, think, transfer_to_human_agents)

### 3. Integration Tests

Cross-cutting tests that validate:

- **Environment initialization**: Tests that environments can be created successfully
- **Tool integration**: Tests that tools work correctly within environment context
- **Data consistency**: Tests that data remains consistent across multiple tool calls
- **Task splits**: Tests that different task splits (train/test/dev) work correctly
- **Tool counts**: Validates expected number of tools per environment

## Test Data Usage

Tests use the same JSON data files that the actual environments use:

### Retail Environment Data
- `users.json`: Customer profiles with addresses, payment methods, orders
- `orders.json`: Order details with items, status, payment history  
- `products.json`: Product catalog with variants, pricing, availability

### Airline Environment Data  
- `users.json`: Customer profiles with addresses, reservations, preferences
- `reservations.json`: Flight bookings with passengers, payment, status
- `flights.json`: Available flights with dates, pricing, availability

## Base Test Classes

The testing infrastructure provides base classes for consistent testing:

### BaseToolTest
Abstract base class for testing individual tools:
- Provides common test methods for tool info structure validation
- Handles basic invocation testing  
- Validates parameter handling
- Requires subclasses to implement `data` and `tool_class` properties

### BaseEnvironmentTest  
Abstract base class for testing entire environments:
- Validates tool uniqueness across environment
- Tests tool instantiation with environment data
- Validates data structure consistency
- Requires subclasses to implement `data_load_func` and `all_tools` properties

## Key Testing Principles

1. **Data-Driven**: All tests use real JSON data from environment data folders
2. **Comprehensive Coverage**: Every tool method is tested with multiple scenarios  
3. **Error Handling**: Tests validate graceful handling of invalid inputs
4. **Schema Validation**: Tool info schemas are validated against OpenAI function format
5. **Integration**: Tests verify tools work correctly within their environment context
6. **Non-Destructive**: Tests don't modify the original data files

## Benefits

This testing infrastructure provides:

- **Quality Assurance**: Ensures all tools behave correctly with their data
- **Regression Prevention**: Catches breaking changes to tool implementations
- **Documentation**: Tests serve as executable documentation of expected behavior
- **Development Speed**: Fast feedback loop for tool changes
- **Deployment Confidence**: Comprehensive validation before model interactions

## Dependencies

The testing infrastructure requires:
- `pytest>=7.0.0` (added to setup.py)
- All existing tau-bench dependencies for environment loading

No additional external dependencies were introduced to keep the testing infrastructure lightweight and focused.