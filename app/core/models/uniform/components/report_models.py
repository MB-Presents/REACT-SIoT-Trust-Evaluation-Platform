from enum import Enum, auto


class Situation(Enum):

    EMERGENCY_REPORT = auto()
    TRAFFIC_PRIORITY_REQUEST = auto()


class ReportType(Enum):
    EmergencyReport = auto()
    TraffiCPriorityRequest = auto()
    
class AuthenticityRole(Enum):
    AUTHENTIC = auto()
    UNAUTHENTIC = auto()
    
    
class ReporterType(Enum):
    VEHICLE = auto()
    PEDESTRIAN = auto()
    