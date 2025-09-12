


from enum import Enum, auto


class TrafficLightApplicationSettings:
    # DISTANCE_TO_REQUEST : int = 200
    
    SERVICE_REQUESTOR_DISTANCE : int = 300
    
    VEHICLE_DISTANCE_SENSING : int = 70
    SMART_PHONE_DISTANCE_SENSING : int = 70



class RequestLifecycleStatus(Enum):
    PENDING = auto()
    FINISHED = auto()
    VERIFIED = auto()
    IGNORE = auto()