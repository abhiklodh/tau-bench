import json
import os
from typing import Any

FOLDER_PATH = os.path.dirname(__file__)


def load_data() -> dict[str, Any]:
    with open(os.path.join(FOLDER_PATH, "patients.json")) as f:
        patient_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "appointments.json")) as f:
        appointment_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "test_results.json")) as f:
        test_result_data = json.load(f)
    return {
        "patients": patient_data,
        "appointments": appointment_data,
        "test_results": test_result_data,
    }