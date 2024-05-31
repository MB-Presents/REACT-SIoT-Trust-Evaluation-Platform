from enum import Enum, auto

class Service(Enum):
    Inductive_Vehicle_Detection_Service = auto()
    Object_Position_Service = auto()
    Vehicle_Status_Service = auto()
    Vehicle_Detection_Service = auto()
    Object_Sensing_Service = auto()

class Function(Enum):
    GET_INDUCTIVE_OBJECT_COUNT = auto()
    GET_DETECTED_VEHICLES = auto()
    GET_OBJECT_POSITION = auto()
    GET_STATUS = auto()
    GET_SENSED_OBJECTS = auto()

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

class SerivceEntities(Enum):
    EMERGENCY_CENTER = auto()
    TRAFFIC_LIGHT = auto()
    EMERGENCY_VEHICLE = auto()
    VEHICLE = auto()
    INDUCTION_LOOP = auto()
    TRAFFIC_CAMERA = auto()
    SMART_PHONE = auto()
    
    

class DeviceType(Enum):
    EMERGENCY_CENTER = auto()
    # EMERGENCY_VEHICLE = auto()
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