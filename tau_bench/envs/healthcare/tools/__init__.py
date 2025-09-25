from .appointment_management import GetAppointmentDetails, ScheduleAppointment, CancelAppointment
from .escalation import TransferToMedicalStaff
from .medical_records import GetTestResults
from .patient_management import GetPatientInfo

ALL_TOOLS = [
    GetPatientInfo,
    ScheduleAppointment,
    GetAppointmentDetails,
    CancelAppointment,
    GetTestResults,
    TransferToMedicalStaff,
]