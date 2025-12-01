# Copyright Sierra

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetOnCallEngineer(Tool):
    """Tool to get the current on-call engineer for a service."""

    @staticmethod
    def invoke(data: Dict[str, Any], service_id: str = None, team: str = None) -> str:
        services = data["services"]
        engineers = data["engineers"]
        
        if service_id:
            if service_id not in services:
                return f"Error: Service {service_id} not found"
            
            service = services[service_id]
            oncall_id = service.get("oncall_schedule")
            
            if not oncall_id or oncall_id not in engineers:
                return f"No on-call engineer found for service {service_id}"
            
            engineer = engineers[oncall_id]
            return json.dumps({
                "service": service_id,
                "oncall_engineer": {
                    "id": oncall_id,
                    "name": engineer["name"],
                    "email": engineer["email"],
                    "phone": engineer["phone"],
                    "slack_handle": engineer["slack_handle"],
                    "shift": engineer["shift"],
                    "current_incidents": engineer.get("current_incidents", [])
                }
            }, indent=2)
        
        if team:
            team_engineers = []
            for eng_id, eng in engineers.items():
                if team in eng.get("teams", []):
                    team_engineers.append({
                        "id": eng_id,
                        "name": eng["name"],
                        "shift": eng.get("shift", "N/A"),
                        "current_incidents": eng.get("current_incidents", [])
                    })
            
            if not team_engineers:
                return f"No engineers found for team {team}"
            
            return json.dumps({"team": team, "engineers": team_engineers}, indent=2)
        
        return "Error: Please specify either service_id or team"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_oncall_engineer",
                "description": "Get the current on-call engineer for a specific service or team.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The service ID to find the on-call engineer for. Optional if team is specified.",
                        },
                        "team": {
                            "type": "string",
                            "description": "The team name to find engineers for. Optional if service_id is specified.",
                        },
                    },
                    "required": [],
                },
            },
        }


class PageEngineer(Tool):
    """Tool to page an engineer via multiple channels."""

    @staticmethod
    def invoke(data: Dict[str, Any], engineer_id: str, message: str, urgency: str = "high") -> str:
        engineers = data["engineers"]
        
        if engineer_id not in engineers:
            return f"Error: Engineer {engineer_id} not found"
        
        engineer = engineers[engineer_id]
        
        channels_used = []
        if urgency == "critical":
            channels_used = ["phone", "sms", "slack", "email"]
        elif urgency == "high":
            channels_used = ["slack", "sms"]
        else:
            channels_used = ["slack"]
        
        return f"Paged {engineer['name']} via {', '.join(channels_used)}. Message: {message}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "page_engineer",
                "description": "Page an engineer via their preferred notification channels based on urgency.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "engineer_id": {
                            "type": "string",
                            "description": "The engineer ID to page.",
                        },
                        "message": {
                            "type": "string",
                            "description": "The message to send in the page.",
                        },
                        "urgency": {
                            "type": "string",
                            "description": "Urgency level: 'critical' (all channels), 'high' (slack + sms), 'low' (slack only).",
                            "enum": ["critical", "high", "low"],
                        },
                    },
                    "required": ["engineer_id", "message"],
                },
            },
        }


class EscalateIncident(Tool):
    """Tool to escalate an incident to senior engineers or management."""

    @staticmethod
    def invoke(data: Dict[str, Any], incident_id: str, escalation_level: str, reason: str) -> str:
        incidents = data["incidents"]
        engineers = data["engineers"]
        
        if incident_id not in incidents:
            return f"Error: Incident {incident_id} not found"
        
        incident = incidents[incident_id]
        
        # Determine escalation target
        if escalation_level == "senior_engineer":
            target = "senior_engineer_1"
        elif escalation_level == "manager":
            target = "manager_1"
        elif escalation_level == "executive":
            target = "manager_1"  # In this simulation, goes to manager
        else:
            return "Error: Invalid escalation level. Must be 'senior_engineer', 'manager', or 'executive'"
        
        if target not in engineers:
            return f"Error: Escalation target not found"
        
        target_info = engineers[target]
        
        # Update incident
        incident["timeline"].append({
            "timestamp": "2024-05-15T15:00:00Z",
            "event": f"Incident escalated to {escalation_level}: {target_info['name']}. Reason: {reason}"
        })
        incident["updated_at"] = "2024-05-15T15:00:00Z"
        
        return f"Incident {incident_id} escalated to {escalation_level} ({target_info['name']}). They have been notified via phone and Slack."

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "escalate_incident",
                "description": "Escalate an incident to a higher level of support when additional expertise or authority is needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "The incident ID to escalate.",
                        },
                        "escalation_level": {
                            "type": "string",
                            "description": "The level to escalate to: 'senior_engineer', 'manager', or 'executive'.",
                            "enum": ["senior_engineer", "manager", "executive"],
                        },
                        "reason": {
                            "type": "string",
                            "description": "The reason for escalation.",
                        },
                    },
                    "required": ["incident_id", "escalation_level", "reason"],
                },
            },
        }


class TransferToHumanAgents(Tool):
    """Tool to transfer to human agents when the issue cannot be resolved."""

    @staticmethod
    def invoke(data: Dict[str, Any], summary: str) -> str:
        return f"Transferring to human on-call team. Summary: {summary}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "transfer_to_human_agents",
                "description": "Transfer the conversation to human on-call agents when the issue requires human intervention or is outside the scope of automated assistance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "A summary of the situation and why human intervention is needed.",
                        },
                    },
                    "required": ["summary"],
                },
            },
        }
