# Copyright Sierra

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetIncidentDetails(Tool):
    """Tool to get details of a specific incident."""

    @staticmethod
    def invoke(data: Dict[str, Any], incident_id: str) -> str:
        incidents = data["incidents"]
        if incident_id in incidents:
            return json.dumps(incidents[incident_id], indent=2)
        return f"Error: Incident {incident_id} not found"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_incident_details",
                "description": "Get the full details of a specific incident by its ID, including title, severity, status, description, timeline, and related information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID, such as 'INC001'.",
                        },
                    },
                    "required": ["incident_id"],
                },
            },
        }


class ListOpenIncidents(Tool):
    """Tool to list all open incidents."""

    @staticmethod
    def invoke(data: Dict[str, Any], severity: str = None, service: str = None) -> str:
        incidents = data["incidents"]
        open_incidents = []
        
        for inc_id, inc in incidents.items():
            if inc["status"] in ["open", "investigating"]:
                # Apply filters
                if severity and inc["severity"] != severity:
                    continue
                if service and inc["service"] != service:
                    continue
                open_incidents.append({
                    "id": inc_id,
                    "title": inc["title"],
                    "severity": inc["severity"],
                    "status": inc["status"],
                    "service": inc["service"],
                    "created_at": inc["created_at"]
                })
        
        if not open_incidents:
            return "No open incidents found matching the criteria."
        
        return json.dumps(open_incidents, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_open_incidents",
                "description": "List all open incidents, optionally filtered by severity or service.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "description": "Filter by severity level: 'P1' (critical), 'P2' (high), 'P3' (medium), 'P4' (low). Optional.",
                            "enum": ["P1", "P2", "P3", "P4"],
                        },
                        "service": {
                            "type": "string",
                            "description": "Filter by service name, such as 'payment-service' or 'api-gateway'. Optional.",
                        },
                    },
                    "required": [],
                },
            },
        }


class UpdateIncidentStatus(Tool):
    """Tool to update the status of an incident."""

    @staticmethod
    def invoke(data: Dict[str, Any], incident_id: str, status: str, note: str = None) -> str:
        incidents = data["incidents"]
        if incident_id not in incidents:
            return f"Error: Incident {incident_id} not found"
        
        valid_statuses = ["open", "investigating", "mitigating", "resolved", "closed"]
        if status not in valid_statuses:
            return f"Error: Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        old_status = incidents[incident_id]["status"]
        incidents[incident_id]["status"] = status
        incidents[incident_id]["updated_at"] = "2024-05-15T15:00:00Z"  # Current time in scenario
        
        timeline_entry = {
            "timestamp": "2024-05-15T15:00:00Z",
            "event": f"Status changed from {old_status} to {status}"
        }
        if note:
            timeline_entry["event"] += f": {note}"
        
        incidents[incident_id]["timeline"].append(timeline_entry)
        
        return f"Incident {incident_id} status updated from {old_status} to {status}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_incident_status",
                "description": "Update the status of an incident. Status transitions should follow the incident lifecycle: open -> investigating -> mitigating -> resolved -> closed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the incident.",
                            "enum": ["open", "investigating", "mitigating", "resolved", "closed"],
                        },
                        "note": {
                            "type": "string",
                            "description": "Optional note explaining the status change.",
                        },
                    },
                    "required": ["incident_id", "status"],
                },
            },
        }


class AssignIncident(Tool):
    """Tool to assign an incident to an engineer."""

    @staticmethod
    def invoke(data: Dict[str, Any], incident_id: str, engineer_id: str) -> str:
        incidents = data["incidents"]
        engineers = data["engineers"]
        
        if incident_id not in incidents:
            return f"Error: Incident {incident_id} not found"
        
        if engineer_id not in engineers:
            return f"Error: Engineer {engineer_id} not found"
        
        old_assignee = incidents[incident_id]["assigned_to"]
        incidents[incident_id]["assigned_to"] = engineer_id
        incidents[incident_id]["updated_at"] = "2024-05-15T15:00:00Z"
        
        engineer_name = engineers[engineer_id]["name"]
        
        timeline_entry = {
            "timestamp": "2024-05-15T15:00:00Z",
            "event": f"Incident assigned to {engineer_name} ({engineer_id})"
        }
        if old_assignee:
            timeline_entry["event"] = f"Incident reassigned from {old_assignee} to {engineer_name}"
        
        incidents[incident_id]["timeline"].append(timeline_entry)
        
        # Update engineer's current incidents
        if "current_incidents" in engineers[engineer_id]:
            if incident_id not in engineers[engineer_id]["current_incidents"]:
                engineers[engineer_id]["current_incidents"].append(incident_id)
        
        return f"Incident {incident_id} assigned to {engineer_name}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_incident",
                "description": "Assign an incident to an on-call engineer for investigation and resolution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID to assign.",
                        },
                        "engineer_id": {
                            "type": "string",
                            "description": "The engineer ID to assign the incident to, such as 'oncall_engineer_1'.",
                        },
                    },
                    "required": ["incident_id", "engineer_id"],
                },
            },
        }


class AddIncidentNote(Tool):
    """Tool to add a note to an incident timeline."""

    @staticmethod
    def invoke(data: Dict[str, Any], incident_id: str, note: str) -> str:
        incidents = data["incidents"]
        
        if incident_id not in incidents:
            return f"Error: Incident {incident_id} not found"
        
        timeline_entry = {
            "timestamp": "2024-05-15T15:00:00Z",
            "event": note
        }
        
        incidents[incident_id]["timeline"].append(timeline_entry)
        incidents[incident_id]["updated_at"] = "2024-05-15T15:00:00Z"
        
        return f"Note added to incident {incident_id}: {note}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_incident_note",
                "description": "Add a note to an incident's timeline to document investigation progress, actions taken, or findings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID to add a note to.",
                        },
                        "note": {
                            "type": "string",
                            "description": "The note content to add to the incident timeline.",
                        },
                    },
                    "required": ["incident_id", "note"],
                },
            },
        }
