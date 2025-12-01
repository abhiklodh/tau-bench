# Copyright Sierra

import json
import os
from typing import Any

FOLDER_PATH = os.path.dirname(__file__)


def load_data() -> dict[str, Any]:
    with open(os.path.join(FOLDER_PATH, "incidents.json")) as f:
        incident_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "services.json")) as f:
        service_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "runbooks.json")) as f:
        runbook_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "alerts.json")) as f:
        alert_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "engineers.json")) as f:
        engineer_data = json.load(f)
    return {
        "incidents": incident_data,
        "services": service_data,
        "runbooks": runbook_data,
        "alerts": alert_data,
        "engineers": engineer_data,
    }
