"""
Healthcare domain escalation tools.
"""

from tau_bench.envs.tool import Tool
from typing import Dict, Any


class TransferToMedicalStaff(Tool):
    """Tool to transfer conversation to medical staff."""
    
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "transfer_to_medical_staff",
                "description": "Transfer the conversation to qualified medical staff",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Reason for transfer to medical staff"
                        },
                        "urgency": {
                            "type": "string",
                            "description": "Urgency level (low, medium, high, emergency)",
                            "enum": ["low", "medium", "high", "emergency"]
                        }
                    },
                    "required": ["reason"]
                }
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], reason: str, urgency: str = "medium") -> str:
        """Transfer to medical staff."""
        return f"Transferring to medical staff. Reason: {reason}. Urgency: {urgency}. A qualified medical professional will assist you shortly."