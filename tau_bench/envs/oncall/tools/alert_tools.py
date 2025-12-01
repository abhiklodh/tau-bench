# Copyright Sierra

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetAlertDetails(Tool):
    """Tool to get details of a specific alert."""

    @staticmethod
    def invoke(data: Dict[str, Any], alert_id: str) -> str:
        alerts = data["alerts"]
        if alert_id in alerts:
            return json.dumps(alerts[alert_id], indent=2)
        return f"Error: Alert {alert_id} not found"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_alert_details",
                "description": "Get the full details of a specific alert by its ID, including severity, metric values, and thresholds.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "alert_id": {
                            "type": "string",
                            "description": "The alert ID, such as 'ALT001'.",
                        },
                    },
                    "required": ["alert_id"],
                },
            },
        }


class ListFiringAlerts(Tool):
    """Tool to list all currently firing alerts."""

    @staticmethod
    def invoke(data: Dict[str, Any], severity: str = None, service: str = None) -> str:
        alerts = data["alerts"]
        firing_alerts = []
        
        for alert_id, alert in alerts.items():
            if alert["status"] != "firing":
                continue
            
            # Apply filters
            if severity and alert["severity"] != severity:
                continue
            if service and alert["service"] != service:
                continue
            
            firing_alerts.append({
                "id": alert_id,
                "name": alert["name"],
                "severity": alert["severity"],
                "service": alert["service"],
                "description": alert["description"],
                "triggered_at": alert["triggered_at"]
            })
        
        if not firing_alerts:
            return "No firing alerts found matching the criteria."
        
        return json.dumps(firing_alerts, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_firing_alerts",
                "description": "List all currently firing alerts, optionally filtered by severity or service.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "description": "Filter by alert severity: 'critical', 'warning', 'info'. Optional.",
                            "enum": ["critical", "warning", "info"],
                        },
                        "service": {
                            "type": "string",
                            "description": "Filter by service name. Optional.",
                        },
                    },
                    "required": [],
                },
            },
        }


class AcknowledgeAlert(Tool):
    """Tool to acknowledge an alert."""

    @staticmethod
    def invoke(data: Dict[str, Any], alert_id: str) -> str:
        alerts = data["alerts"]
        if alert_id not in alerts:
            return f"Error: Alert {alert_id} not found"
        
        alert = alerts[alert_id]
        if alert["status"] != "firing":
            return f"Alert {alert_id} is not in firing state (current status: {alert['status']})"
        
        alert["status"] = "acknowledged"
        alert["acknowledged_at"] = "2024-05-15T15:00:00Z"
        
        return f"Alert {alert_id} ({alert['name']}) has been acknowledged"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "acknowledge_alert",
                "description": "Acknowledge a firing alert to indicate that someone is investigating it. This prevents repeated notifications.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "alert_id": {
                            "type": "string",
                            "description": "The alert ID to acknowledge.",
                        },
                    },
                    "required": ["alert_id"],
                },
            },
        }


class SilenceAlert(Tool):
    """Tool to silence an alert for a specified duration."""

    @staticmethod
    def invoke(data: Dict[str, Any], alert_id: str, duration_minutes: int, reason: str) -> str:
        alerts = data["alerts"]
        if alert_id not in alerts:
            return f"Error: Alert {alert_id} not found"
        
        if duration_minutes < 5 or duration_minutes > 1440:
            return "Error: Silence duration must be between 5 minutes and 24 hours (1440 minutes)"
        
        alert = alerts[alert_id]
        alert["status"] = "silenced"
        alert["silenced_until"] = f"2024-05-15T{15 + duration_minutes // 60:02d}:{duration_minutes % 60:02d}:00Z"
        alert["silence_reason"] = reason
        
        return f"Alert {alert_id} silenced for {duration_minutes} minutes. Reason: {reason}"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "silence_alert",
                "description": "Silence an alert for a specified duration. Use this during planned maintenance or when working on a known issue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "alert_id": {
                            "type": "string",
                            "description": "The alert ID to silence.",
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Duration to silence the alert in minutes (5-1440).",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for silencing the alert.",
                        },
                    },
                    "required": ["alert_id", "duration_minutes", "reason"],
                },
            },
        }
