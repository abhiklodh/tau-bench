# Copyright Sierra

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetServiceHealth(Tool):
    """Tool to get the health status and metrics of a service."""

    @staticmethod
    def invoke(data: Dict[str, Any], service_id: str) -> str:
        services = data["services"]
        if service_id in services:
            service = services[service_id]
            return json.dumps({
                "id": service["id"],
                "name": service["name"],
                "health_status": service["health_status"],
                "tier": service["tier"],
                "team": service["team"],
                "metrics": service.get("metrics", {}),
                "dependencies": service.get("dependencies", []),
                "pods": service.get("pods", service.get("nodes", [])),
            }, indent=2)
        return f"Error: Service {service_id} not found"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_service_health",
                "description": "Get the current health status, metrics, and resource utilization of a specific service.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The service ID, such as 'payment-service', 'api-gateway', or 'database-cluster'.",
                        },
                    },
                    "required": ["service_id"],
                },
            },
        }


class ListServices(Tool):
    """Tool to list all services and their health status."""

    @staticmethod
    def invoke(data: Dict[str, Any], health_status: str = None, tier: str = None) -> str:
        services = data["services"]
        result = []
        
        for svc_id, svc in services.items():
            # Apply filters
            if health_status and svc["health_status"] != health_status:
                continue
            if tier and svc["tier"] != tier:
                continue
            
            result.append({
                "id": svc_id,
                "name": svc["name"],
                "health_status": svc["health_status"],
                "tier": svc["tier"],
                "team": svc["team"],
            })
        
        if not result:
            return "No services found matching the criteria."
        
        return json.dumps(result, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_services",
                "description": "List all services with their current health status, optionally filtered by health status or tier.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "health_status": {
                            "type": "string",
                            "description": "Filter by health status: 'healthy', 'warning', 'degraded', 'critical'. Optional.",
                            "enum": ["healthy", "warning", "degraded", "critical"],
                        },
                        "tier": {
                            "type": "string",
                            "description": "Filter by service tier: 'critical', 'high', 'medium', 'low'. Optional.",
                            "enum": ["critical", "high", "medium", "low"],
                        },
                    },
                    "required": [],
                },
            },
        }


class GetServiceDependencies(Tool):
    """Tool to get the dependency graph of a service."""

    @staticmethod
    def invoke(data: Dict[str, Any], service_id: str) -> str:
        services = data["services"]
        if service_id not in services:
            return f"Error: Service {service_id} not found"
        
        service = services[service_id]
        dependencies = service.get("dependencies", [])
        
        result = {
            "service": service_id,
            "dependencies": [],
            "dependents": []
        }
        
        # Get dependency details
        for dep_id in dependencies:
            if dep_id in services:
                dep = services[dep_id]
                result["dependencies"].append({
                    "id": dep_id,
                    "name": dep["name"],
                    "health_status": dep["health_status"],
                })
            else:
                result["dependencies"].append({
                    "id": dep_id,
                    "name": dep_id,
                    "health_status": "external"
                })
        
        # Find services that depend on this service
        for svc_id, svc in services.items():
            if service_id in svc.get("dependencies", []):
                result["dependents"].append({
                    "id": svc_id,
                    "name": svc["name"],
                    "health_status": svc["health_status"],
                })
        
        return json.dumps(result, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_service_dependencies",
                "description": "Get the upstream dependencies and downstream dependents of a service to understand blast radius and root cause analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The service ID to analyze dependencies for.",
                        },
                    },
                    "required": ["service_id"],
                },
            },
        }


class GetRecentDeployments(Tool):
    """Tool to get recent deployments for a service."""

    @staticmethod
    def invoke(data: Dict[str, Any], service_id: str) -> str:
        services = data["services"]
        if service_id not in services:
            return f"Error: Service {service_id} not found"
        
        service = services[service_id]
        deployments = service.get("recent_deployments", [])
        
        if not deployments:
            return f"No recent deployments found for {service_id}"
        
        return json.dumps({
            "service": service_id,
            "recent_deployments": deployments
        }, indent=2)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_recent_deployments",
                "description": "Get the recent deployment history for a service to help correlate issues with code changes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The service ID to get deployment history for.",
                        },
                    },
                    "required": ["service_id"],
                },
            },
        }


class ScaleService(Tool):
    """Tool to scale a service up or down."""

    @staticmethod
    def invoke(data: Dict[str, Any], service_id: str, replicas: int) -> str:
        services = data["services"]
        if service_id not in services:
            return f"Error: Service {service_id} not found"
        
        if replicas < 1 or replicas > 20:
            return "Error: Replica count must be between 1 and 20"
        
        service = services[service_id]
        
        if "pods" not in service:
            return f"Error: Service {service_id} does not support scaling (may be a database or external service)"
        
        current_replicas = len(service["pods"])
        
        # Simulate scaling by adjusting pod count
        if replicas > current_replicas:
            # Add new pods
            for i in range(current_replicas + 1, replicas + 1):
                service["pods"].append({
                    "name": f"{service_id}-pod-{i}",
                    "status": "starting",
                    "cpu": 10,
                    "memory": 20
                })
            action = f"scaled up from {current_replicas} to {replicas} replicas"
        elif replicas < current_replicas:
            # Remove pods
            service["pods"] = service["pods"][:replicas]
            action = f"scaled down from {current_replicas} to {replicas} replicas"
        else:
            return f"Service {service_id} already has {replicas} replicas"
        
        return f"Service {service_id} {action}. New pods may take 30-60 seconds to become ready."

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "scale_service",
                "description": "Scale a service horizontally by adjusting the number of replicas. Use this to add capacity during incidents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The service ID to scale.",
                        },
                        "replicas": {
                            "type": "integer",
                            "description": "The target number of replicas (1-20).",
                        },
                    },
                    "required": ["service_id", "replicas"],
                },
            },
        }


class RestartService(Tool):
    """Tool to perform a rolling restart of a service."""

    @staticmethod
    def invoke(data: Dict[str, Any], service_id: str) -> str:
        services = data["services"]
        if service_id not in services:
            return f"Error: Service {service_id} not found"
        
        service = services[service_id]
        
        if "pods" not in service:
            return f"Error: Service {service_id} does not support restart (may be a database or external service)"
        
        pod_count = len(service["pods"])
        
        return f"Rolling restart initiated for {service_id}. {pod_count} pods will be restarted one at a time. Estimated completion time: {pod_count * 30} seconds."

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "restart_service",
                "description": "Perform a rolling restart of a service. This restarts pods one at a time to avoid downtime. Use this to recover from memory leaks or reset connection pools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The service ID to restart.",
                        },
                    },
                    "required": ["service_id"],
                },
            },
        }
