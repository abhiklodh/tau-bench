"""
Healthcare domain tools for appointment management.
"""

from tau_bench.envs.tool import Tool
from typing import Dict, Any


class GetAppointmentDetails(Tool):
    """Tool to get appointment details."""
    
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_appointment_details",
                "description": "Get appointment details by patient ID or appointment ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": "The patient ID"
                        },
                        "appointment_id": {
                            "type": "string",
                            "description": "The appointment ID (optional)"
                        }
                    },
                    "required": ["patient_id"]
                }
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], patient_id: str, appointment_id: str = None) -> str:
        """Get appointment details."""
        appointments = data.get("appointments", {})
        
        if appointment_id:
            if appointment_id not in appointments:
                return f"Appointment {appointment_id} not found."
            
            appt = appointments[appointment_id]
            if appt["patient_id"] != patient_id:
                return f"Appointment {appointment_id} does not belong to patient {patient_id}."
            
            return f"Appointment {appointment_id}: Patient {appt['patient_id']}, Doctor: {appt['doctor']}, Date: {appt['date']}, Time: {appt['time']}, Type: {appt['type']}, Status: {appt['status']}"
        else:
            # Return all appointments for the patient
            patient_appointments = [appt for appt in appointments.values() if appt["patient_id"] == patient_id]
            
            if not patient_appointments:
                return f"No appointments found for patient {patient_id}."
            
            results = []
            for appt_id, appt in appointments.items():
                if appt["patient_id"] == patient_id:
                    results.append(f"Appointment {appt_id}: Doctor: {appt['doctor']}, Date: {appt['date']}, Time: {appt['time']}, Type: {appt['type']}, Status: {appt['status']}")
            
            return "\n".join(results)


class ScheduleAppointment(Tool):
    """Tool to schedule a new appointment."""
    
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "schedule_appointment",
                "description": "Schedule a new patient appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string", 
                            "description": "The patient ID"
                        },
                        "doctor": {
                            "type": "string",
                            "description": "The doctor name"
                        },
                        "date": {
                            "type": "string",
                            "description": "Appointment date (YYYY-MM-DD)"
                        },
                        "time": {
                            "type": "string", 
                            "description": "Appointment time (HH:MM AM/PM)"
                        },
                        "type": {
                            "type": "string",
                            "description": "Appointment type"
                        }
                    },
                    "required": ["patient_id", "doctor", "date", "time", "type"]
                }
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], patient_id: str, doctor: str, date: str, time: str, type: str) -> str:
        """Schedule a new appointment."""
        appointments = data.get("appointments", {})
        
        # Generate new appointment ID
        appt_id = f"APT{len(appointments) + 1:03d}"
        
        appointments[appt_id] = {
            "patient_id": patient_id,
            "doctor": doctor, 
            "date": date,
            "time": time,
            "type": type,
            "status": "scheduled"
        }
        
        return f"Appointment {appt_id} scheduled for patient {patient_id} with {doctor} on {date} at {time} for {type}."


class CancelAppointment(Tool):
    """Tool to cancel an appointment."""
    
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "cancel_appointment",
                "description": "Cancel an existing appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": "The appointment ID to cancel"
                        }
                    },
                    "required": ["appointment_id"]
                }
            }
        }
    
    @classmethod
    def invoke(cls, data: Dict[str, Any], appointment_id: str) -> str:
        """Cancel an appointment."""
        appointments = data.get("appointments", {})
        
        if appointment_id not in appointments:
            return f"Appointment {appointment_id} not found."
        
        appointments[appointment_id]["status"] = "cancelled"
        return f"Appointment {appointment_id} has been cancelled."