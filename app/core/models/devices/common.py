from enum import Enum, auto
from pickle import GET

class Service(Enum):
    # Vehicle
    Vehicle_Status_Service = auto()
    Object_Detection_Service = auto()
    
    # Smart Phone
    Object_Position_Service = auto()
    Object_Proximity_Service = auto()
    
    # Traffic Light
    Vehicle_Detection_Service = auto()

    # Induction Loop
    Inductive_Vehicle_Detection_Service = auto()
    
    # Emergency Center
    Emergency_Report_Management_Service = auto()
    Emergency_Vehicle_Management_Service = auto()

class Function(Enum):
    GET_INDUCTIVE_OBJECT_COUNT = auto()
    GET_DETECTED_VEHICLES = auto()
    GET_OBJECT_POSITION = auto()
    GET_STATUS = auto()
    GET_SENSED_OBJECTS = auto()
    GET_SPEED = auto()
    GET_COLOR = auto()
    GET_POSITION = auto()
    GET_STREET = auto()
    GET_LANE = auto()
    GET_LANE_ID = auto()
    GET_SIGNAL = auto()
    GET_LANE_POSITION = auto()
    GET_DIMENSIONS = auto()


class DeviceInternalStatus(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    ERROR = auto()
    
class DeviceShapeStatus(Enum):
    ORIGINAL_MANUFACTURED = auto()
    # SCRATCHES = auto()
    # DENTS = auto()
    # HEAVILY_DAMAGED = auto()
    DEFORMED = auto()

 
class DeviceType(Enum):
    EMERGENCY_CENTER = auto()
    EMERGENCY_VEHICLE = auto()
    VEHICLE = auto()
    TRAFFIC_CAMERA = auto()
    INDUCTION_LOOP = auto()
    SMART_PHONE = auto()
    TRAFFIC_LIGHT = auto()
    
class DeviceRecordType(Enum):
    STATUS = auto() 
    SENSED = auto()

class DeviceBehaviour(Enum):
    TRUSTWORTHY = auto()
    MALICIOUS = auto()
    SELECTIVE_MALICIOUS = auto()
    
class DeviceComputationCapabilityClass(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    UNDEFINED = auto()