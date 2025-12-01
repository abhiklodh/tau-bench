# Copyright Sierra

from .incident_management import (
    GetIncidentDetails,
    ListOpenIncidents,
    UpdateIncidentStatus,
    AssignIncident,
    AddIncidentNote,
)
from .service_management import (
    GetServiceHealth,
    ListServices,
    GetServiceDependencies,
    GetRecentDeployments,
    ScaleService,
    RestartService,
)
from .runbook_tools import (
    GetRunbook,
    SearchRunbooks,
    ExecuteRunbookStep,
)
from .alert_tools import (
    GetAlertDetails,
    ListFiringAlerts,
    AcknowledgeAlert,
    SilenceAlert,
)
from .escalation_tools import (
    GetOnCallEngineer,
    PageEngineer,
    EscalateIncident,
    TransferToHumanAgents,
)
from .utility_tools import (
    Calculate,
    Think,
)

ALL_TOOLS = [
    # Incident Management
    GetIncidentDetails,
    ListOpenIncidents,
    UpdateIncidentStatus,
    AssignIncident,
    AddIncidentNote,
    # Service Management
    GetServiceHealth,
    ListServices,
    GetServiceDependencies,
    GetRecentDeployments,
    ScaleService,
    RestartService,
    # Runbooks
    GetRunbook,
    SearchRunbooks,
    ExecuteRunbookStep,
    # Alerts
    GetAlertDetails,
    ListFiringAlerts,
    AcknowledgeAlert,
    SilenceAlert,
    # Escalation
    GetOnCallEngineer,
    PageEngineer,
    EscalateIncident,
    TransferToHumanAgents,
    # Utilities
    Calculate,
    Think,
]
