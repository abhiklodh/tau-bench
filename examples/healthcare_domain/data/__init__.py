# Copyright Sierra

"""
Healthcare domain data loader.
"""

def load_data():
    """Load healthcare domain data."""
    return {
        "patients": {
            "PAT001": {
                "name": "John Smith",
                "dob": "1985-03-15",
                "phone": "555-0123",
                "email": "john.smith@email.com",
                "address": "123 Main St, Anytown, ST 12345"
            },
            "PAT002": {
                "name": "Sarah Johnson", 
                "dob": "1992-07-22",
                "phone": "555-0456",
                "email": "sarah.j@email.com",
                "address": "456 Oak Ave, Anytown, ST 12345"
            }
        },
        "appointments": {
            "APT001": {
                "patient_id": "PAT001",
                "doctor": "Dr. Williams",
                "date": "2024-02-15",
                "time": "10:00 AM",
                "type": "General Checkup",
                "status": "scheduled"
            },
            "APT002": {
                "patient_id": "PAT002",
                "doctor": "Dr. Brown",
                "date": "2024-02-16", 
                "time": "2:00 PM",
                "type": "Follow-up",
                "status": "scheduled"
            }
        },
        "test_results": {
            "TEST001": {
                "patient_id": "PAT001",
                "test_type": "Blood Work",
                "date": "2024-01-30",
                "results": "Normal",
                "doctor": "Dr. Williams"
            }
        }
    }