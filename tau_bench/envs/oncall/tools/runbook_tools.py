# Copyright Sierra

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRunbook(Tool):
    """Tool to get a runbook for troubleshooting a specific issue."""

    @staticmethod
    def invoke(data: Dict[str, Any], runbook_id: str) -> str:
        runbooks = data["runbooks"]
        if runbook_id in runbooks:
            return json.dumps(runbooks[runbook_id], indent=2)
        return f"Error: Runbook {runbook_id} not found"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_runbook",
                "description": "Get a specific runbook by ID containing investigation steps, remediation actions, and escalation procedures.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "runbook_id": {
                            "type": "string",
                            "description": "The runbook ID, such as 'RB001'.",
                        },
                    },
                    "required": ["runbook_id"],
                },
            },
        }


class SearchRunbooks(Tool):
    """Tool to search for relevant runbooks based on symptoms or service."""

    @staticmethod
    def invoke(data: Dict[str, Any], query: str = None, service: str = None, severity: str = None) -> str:
        runbooks = data["runbooks"]
        results = []
        
        query_lower = query.lower() if query else None
        
        for rb_id, rb in runbooks.items():
            match = True
            
            # Filter by service
            if service and rb["service"] != service:
                match = False
            
            # Filter by severity
            if severity and severity not in rb["severity"]:
                match = False
            
            # Search in title and symptoms
            if query_lower:
                searchable = (rb["title"] + " " + " ".join(rb["symptoms"])).lower()
                if query_lower not in searchable:
                    match = False
            
            if match:
                results.append({
                    "id": rb_id,
                    "title": rb["title"],
                    "service": rb["service"],
                    "severity": rb["severity"],
                    "symptoms": rb["symptoms"][:2]  # First 2 symptoms for preview
                })
        
        if not results:
            return "No runbooks found matching the criteria. Try broadening your search."
        
        return json.dumps(results, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_runbooks",
                "description": "Search for relevant runbooks based on keywords, service name, or severity level.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search keywords to find relevant runbooks (e.g., 'memory leak', 'timeout', 'disk space'). Optional.",
                        },
                        "service": {
                            "type": "string",
                            "description": "Filter runbooks by service name. Optional.",
                        },
                        "severity": {
                            "type": "string",
                            "description": "Filter by severity level: 'P1', 'P2', 'P3', 'P4'. Optional.",
                            "enum": ["P1", "P2", "P3", "P4"],
                        },
                    },
                    "required": [],
                },
            },
        }


class ExecuteRunbookStep(Tool):
    """Tool to execute a specific step from a runbook."""

    @staticmethod
    def invoke(data: Dict[str, Any], runbook_id: str, step_type: str, step_number: int) -> str:
        runbooks = data["runbooks"]
        
        if runbook_id not in runbooks:
            return f"Error: Runbook {runbook_id} not found"
        
        runbook = runbooks[runbook_id]
        
        if step_type == "investigation":
            steps = runbook.get("investigation_steps", [])
        elif step_type == "remediation":
            steps = runbook.get("remediation_steps", [])
        else:
            return "Error: step_type must be 'investigation' or 'remediation'"
        
        # Find the step
        target_step = None
        for step in steps:
            if step["step"] == step_number:
                target_step = step
                break
        
        if not target_step:
            return f"Error: Step {step_number} not found in {step_type} steps"
        
        # Simulate execution result
        command = target_step.get("command", "N/A")
        expected = target_step.get("expected", "N/A")
        note = target_step.get("note", "")
        
        result = {
            "step": step_number,
            "action": target_step["action"],
            "command_executed": command,
            "status": "completed",
            "output": f"[Simulated output for: {command}]",
            "expected_outcome": expected
        }
        
        if note:
            result["note"] = note
        
        return json.dumps(result, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "execute_runbook_step",
                "description": "Execute a specific investigation or remediation step from a runbook. Returns the simulated output of the command.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "runbook_id": {
                            "type": "string",
                            "description": "The runbook ID containing the step to execute.",
                        },
                        "step_type": {
                            "type": "string",
                            "description": "Type of step: 'investigation' or 'remediation'.",
                            "enum": ["investigation", "remediation"],
                        },
                        "step_number": {
                            "type": "integer",
                            "description": "The step number to execute.",
                        },
                    },
                    "required": ["runbook_id", "step_type", "step_number"],
                },
            },
        }
