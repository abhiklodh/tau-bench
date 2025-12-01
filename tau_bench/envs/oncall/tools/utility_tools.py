# Copyright Sierra

from typing import Any, Dict
from tau_bench.envs.tool import Tool


class Calculate(Tool):
    """Tool for basic calculations."""

    @staticmethod
    def invoke(data: Dict[str, Any], expression: str) -> str:
        try:
            # Only allow safe mathematical operations
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "Error: Expression contains invalid characters. Only numbers and basic operators (+, -, *, /, .) are allowed."
            
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error calculating expression: {e}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform basic mathematical calculations. Use this for computing metrics, percentages, or time calculations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate, such as '(100 - 85) * 1.5' or '98 / 100 * 100'.",
                        },
                    },
                    "required": ["expression"],
                },
            },
        }


class Think(Tool):
    """Tool for internal reasoning and analysis."""

    @staticmethod
    def invoke(data: Dict[str, Any], thought: str) -> str:
        return f"Thought recorded: {thought}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "think",
                "description": "Use this tool to think through complex problems, analyze situations, or plan your next steps. This helps with incident analysis and decision making.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "thought": {
                            "type": "string",
                            "description": "Your analysis, reasoning, or planned next steps.",
                        },
                    },
                    "required": ["thought"],
                },
            },
        }
