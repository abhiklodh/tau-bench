# Copyright Sierra

"""
Healthcare domain tools for patient management.
"""

from tau_bench.envs.tool import Tool
from typing import Dict, Any


class GetPatientInfo(Tool):
    """Tool to get patient information."""
    
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_patient_info",
                "description": "Get patient information by patient ID",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": "The patient ID"
                        }
                    },
                    "required": ["patient_id"]
                }
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], patient_id: str) -> str:
        """Get patient information."""
        patients = data.get("patients", {})
        
        if patient_id not in patients:
            return f"Patient {patient_id} not found."
        
        patient = patients[patient_id]
        return f"Patient: {patient['name']}, DOB: {patient['dob']}, Phone: {patient['phone']}, Email: {patient['email']}"