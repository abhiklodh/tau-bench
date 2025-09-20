# Copyright Sierra

"""
Healthcare domain tools for medical records.
"""

from tau_bench.envs.tool import Tool
from typing import Dict, Any


class GetTestResults(Tool):
    """Tool to get patient test results."""
    
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_test_results",
                "description": "Get patient test results",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": "The patient ID"
                        },
                        "test_id": {
                            "type": "string",
                            "description": "The test ID (optional)",
                            "required": False
                        }
                    },
                    "required": ["patient_id"]
                }
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], patient_id: str, test_id: str = None) -> str:
        """Get test results for a patient."""
        test_results = data.get("test_results", {})
        
        if test_id:
            if test_id not in test_results:
                return f"Test {test_id} not found."
            
            test = test_results[test_id]
            if test["patient_id"] != patient_id:
                return f"Test {test_id} does not belong to patient {patient_id}."
            
            return f"Test {test_id}: {test['test_type']} on {test['date']}, Results: {test['results']}, Doctor: {test['doctor']}"
        else:
            # Return all tests for the patient
            patient_tests = [test for test in test_results.values() if test["patient_id"] == patient_id]
            
            if not patient_tests:
                return f"No test results found for patient {patient_id}."
            
            results = []
            for test_id, test in test_results.items():
                if test["patient_id"] == patient_id:
                    results.append(f"Test {test_id}: {test['test_type']} on {test['date']}, Results: {test['results']}")
            
            return "\n".join(results)