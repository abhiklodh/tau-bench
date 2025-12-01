# Copyright Sierra

from tau_bench.types import Task, Action

TASKS = [
    # Task 1: Basic incident triage and investigation
    Task(
        user_id="oncall_engineer_1",
        instruction="You are the on-call engineer. There's a P1 incident INC001 that just came in about the payment service. You need to investigate it, find the related runbook, and start the investigation process. Acknowledge the related alerts and assign the incident to yourself.",
        actions=[
            Action(name="get_incident_details", kwargs={"incident_id": "INC001"}),
            Action(name="list_firing_alerts", kwargs={"service": "payment-service"}),
            Action(name="acknowledge_alert", kwargs={"alert_id": "ALT001"}),
            Action(name="acknowledge_alert", kwargs={"alert_id": "ALT002"}),
            Action(name="search_runbooks", kwargs={"service": "payment-service"}),
            Action(name="assign_incident", kwargs={"incident_id": "INC001", "engineer_id": "oncall_engineer_1"}),
            Action(name="update_incident_status", kwargs={"incident_id": "INC001", "status": "investigating"}),
        ],
        outputs=["RB001"],
    ),
    # Task 2: Service health check and dependency analysis
    Task(
        user_id="oncall_engineer_1",
        instruction="You are investigating a timeout issue. Check the health of the api-gateway service and understand its dependencies. Find out which downstream services might be causing the timeouts.",
        actions=[
            Action(name="get_service_health", kwargs={"service_id": "api-gateway"}),
            Action(name="get_service_dependencies", kwargs={"service_id": "api-gateway"}),
            Action(name="get_service_health", kwargs={"service_id": "payment-service"}),
        ],
        outputs=["degraded", "payment-service"],
    ),
    # Task 3: Follow runbook investigation steps
    Task(
        user_id="oncall_engineer_1",
        instruction="You're working on incident INC001 about database connection pool exhaustion. Get the runbook RB001 and execute the first two investigation steps. Document your findings in the incident timeline.",
        actions=[
            Action(name="get_runbook", kwargs={"runbook_id": "RB001"}),
            Action(name="execute_runbook_step", kwargs={"runbook_id": "RB001", "step_type": "investigation", "step_number": 1}),
            Action(name="execute_runbook_step", kwargs={"runbook_id": "RB001", "step_type": "investigation", "step_number": 2}),
            Action(name="add_incident_note", kwargs={"incident_id": "INC001", "note": "Executed investigation steps 1 and 2 from runbook RB001"}),
        ],
        outputs=[],
    ),
    # Task 4: Scale service during incident
    Task(
        user_id="oncall_engineer_1",
        instruction="The order-service is experiencing high CPU usage and a growing queue backlog (incident INC006). Check the service health, find the on-call engineer for this service, and scale it up to 6 replicas to handle the load.",
        actions=[
            Action(name="get_incident_details", kwargs={"incident_id": "INC006"}),
            Action(name="get_service_health", kwargs={"service_id": "order-service"}),
            Action(name="get_oncall_engineer", kwargs={"service_id": "order-service"}),
            Action(name="scale_service", kwargs={"service_id": "order-service", "replicas": 6}),
            Action(name="add_incident_note", kwargs={"incident_id": "INC006", "note": "Scaled order-service to 6 replicas"}),
        ],
        outputs=["92", "15000"],
    ),
    # Task 5: Restart service for memory leak
    Task(
        user_id="oncall_engineer_1",
        instruction="Incident INC002 is about memory leaks in the user-service. Check the current memory situation, get the relevant runbook, and perform a rolling restart to temporarily recover memory. Update the incident status to mitigating.",
        actions=[
            Action(name="get_incident_details", kwargs={"incident_id": "INC002"}),
            Action(name="get_service_health", kwargs={"service_id": "user-service"}),
            Action(name="search_runbooks", kwargs={"query": "memory leak"}),
            Action(name="restart_service", kwargs={"service_id": "user-service"}),
            Action(name="update_incident_status", kwargs={"incident_id": "INC002", "status": "mitigating", "note": "Rolling restart initiated"}),
        ],
        outputs=["85", "RB002"],
    ),
    # Task 6: Escalate a complex incident
    Task(
        user_id="oncall_engineer_1",
        instruction="Incident INC003 (API Gateway timeouts) is affecting multiple services and you've been investigating for 30 minutes without resolution. The issue is complex. Escalate to a senior engineer and explain the situation.",
        actions=[
            Action(name="get_incident_details", kwargs={"incident_id": "INC003"}),
            Action(name="get_service_dependencies", kwargs={"service_id": "api-gateway"}),
            Action(name="escalate_incident", kwargs={"incident_id": "INC003", "escalation_level": "senior_engineer", "reason": "Complex multi-service issue affecting API gateway with 30% timeout rate, multiple downstream services impacted"}),
        ],
        outputs=[],
    ),
    # Task 7: Handle certificate expiration alert
    Task(
        user_id="oncall_engineer_2",
        instruction="There's an alert ALT006 about an SSL certificate expiring soon for the CDN service. Investigate the alert, find the incident related to it, get the relevant runbook, and document your findings.",
        actions=[
            Action(name="get_alert_details", kwargs={"alert_id": "ALT006"}),
            Action(name="get_incident_details", kwargs={"incident_id": "INC004"}),
            Action(name="search_runbooks", kwargs={"query": "certificate"}),
            Action(name="get_runbook", kwargs={"runbook_id": "RB004"}),
        ],
        outputs=["2024-05-22", "cdn.example.com"],
    ),
    # Task 8: Review and resolve an incident
    Task(
        user_id="oncall_engineer_2",
        instruction="Incident INC005 about disk space was resolved earlier. Review the incident details and resolution, then close the incident officially.",
        actions=[
            Action(name="get_incident_details", kwargs={"incident_id": "INC005"}),
            Action(name="update_incident_status", kwargs={"incident_id": "INC005", "status": "closed", "note": "Confirmed disk space issue resolved, cleanup successful"}),
        ],
        outputs=["resolved", "65"],
    ),
    # Task 9: List and prioritize open incidents
    Task(
        user_id="oncall_engineer_1",
        instruction="At the start of your on-call shift, you need to get a view of all open incidents. List all P1 incidents first, then P2 incidents. Identify which ones are unassigned.",
        actions=[
            Action(name="list_open_incidents", kwargs={"severity": "P1"}),
            Action(name="list_open_incidents", kwargs={"severity": "P2"}),
        ],
        outputs=["INC001", "INC003", "INC002", "INC006"],
    ),
    # Task 10: Check recent deployments correlation
    Task(
        user_id="oncall_engineer_1",
        instruction="You suspect the user-service memory leak (INC002) might be related to a recent deployment. Check the recent deployments for user-service and compare the timing with when the incident started.",
        actions=[
            Action(name="get_incident_details", kwargs={"incident_id": "INC002"}),
            Action(name="get_recent_deployments", kwargs={"service_id": "user-service"}),
        ],
        outputs=["v4.1.2", "2024-05-15"],
    ),
    # Task 11: Silence alert during investigation
    Task(
        user_id="oncall_engineer_1",
        instruction="You're actively investigating alert ALT003 (User Service Memory High) and don't want to be repeatedly notified. Acknowledge it first, then silence it for 60 minutes while you investigate.",
        actions=[
            Action(name="acknowledge_alert", kwargs={"alert_id": "ALT003"}),
            Action(name="silence_alert", kwargs={"alert_id": "ALT003", "duration_minutes": 60, "reason": "Actively investigating memory issue"}),
        ],
        outputs=[],
    ),
    # Task 12: Page engineer for help
    Task(
        user_id="oncall_engineer_2",
        instruction="You need help from the database team for incident INC001 which involves database connection pool issues. Find out who's on-call for the database-cluster service and page them with high urgency.",
        actions=[
            Action(name="get_oncall_engineer", kwargs={"service_id": "database-cluster"}),
            Action(name="page_engineer", kwargs={"engineer_id": "oncall_engineer_3", "message": "Need help with database connection pool exhaustion affecting payment-service. Incident INC001.", "urgency": "high"}),
        ],
        outputs=["Carol Johnson"],
    ),
    # Task 13: Complete incident resolution workflow
    Task(
        user_id="oncall_engineer_1",
        instruction="Incident INC006 (high CPU in order-service) has been mitigated by scaling. After verification, the service is healthy. Update the incident to resolved status and add a resolution note.",
        actions=[
            Action(name="get_service_health", kwargs={"service_id": "order-service"}),
            Action(name="add_incident_note", kwargs={"incident_id": "INC006", "note": "Service scaled to 6 replicas, CPU usage normalized, queue backlog clearing"}),
            Action(name="update_incident_status", kwargs={"incident_id": "INC006", "status": "resolved", "note": "Issue resolved by horizontal scaling"}),
        ],
        outputs=[],
    ),
    # Task 14: Complex multi-service investigation
    Task(
        user_id="oncall_engineer_1",
        instruction="You received a report that the API gateway is timing out. You need to investigate the full dependency chain to find the root cause. Start with api-gateway, check its health, then check each degraded dependency.",
        actions=[
            Action(name="list_services", kwargs={"health_status": "degraded"}),
            Action(name="get_service_health", kwargs={"service_id": "api-gateway"}),
            Action(name="get_service_dependencies", kwargs={"service_id": "api-gateway"}),
            Action(name="get_service_health", kwargs={"service_id": "payment-service"}),
            Action(name="get_service_dependencies", kwargs={"service_id": "payment-service"}),
        ],
        outputs=["payment-service", "api-gateway", "database-cluster"],
    ),
    # Task 15: Transfer to human agents
    Task(
        user_id="oncall_engineer_1",
        instruction="A user is reporting a potential data breach where customer data may have been exposed. This is outside your scope of automated tools. Transfer to human agents with a summary.",
        actions=[
            Action(name="transfer_to_human_agents", kwargs={"summary": "Potential data breach reported - customer data may have been exposed. This requires security team investigation and potentially legal/compliance involvement. User needs immediate human assistance."}),
        ],
        outputs=[],
    ),
]
