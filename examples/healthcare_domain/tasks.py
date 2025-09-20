# Copyright Sierra

"""
Healthcare domain sample tasks.
"""

from tau_bench.types import Task, Action

TASKS = [
    Task(
        user_id="PAT001",
        instruction="You are John Smith (Patient ID: PAT001). You want to check on your recent blood work test results and schedule a follow-up appointment with Dr. Williams for next week.",
        actions=[
            Action(
                name="get_patient_info",
                kwargs={"patient_id": "PAT001"}
            ),
            Action(
                name="get_test_results", 
                kwargs={"patient_id": "PAT001"}
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "PAT001",
                    "doctor": "Dr. Williams",
                    "date": "2024-02-22",
                    "time": "10:00 AM", 
                    "type": "Follow-up"
                }
            )
        ],
        outputs=["Normal", "APT003"]
    ),
    Task(
        user_id="PAT002",
        instruction="You are Sarah Johnson (Patient ID: PAT002). You need to cancel your upcoming appointment and want to know if there are any test results available.",
        actions=[
            Action(
                name="get_appointment_details",
                kwargs={"appointment_id": "APT002"}
            ),
            Action(
                name="cancel_appointment",
                kwargs={"appointment_id": "APT002"}
            ),
            Action(
                name="get_test_results",
                kwargs={"patient_id": "PAT002"}
            )
        ],
        outputs=["cancelled", "No test results"]
    )
]