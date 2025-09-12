from enum import Enum, auto
from typing import Any, List


   



class ObjectType(Enum):

    EMERGENCY_CENTER = auto()
    VEHICLE = auto()
    EMERGENCY_VEHICLE = auto()
    TRAFFIC_CAMERA = auto()
    INDUCTION_LOOP = auto()
    SMART_PHONE = auto()
    ROUTE_MESSAGE = auto()
    TRAFFIC_LIGHT = auto()

    EVENT = auto()
    COLLISION = auto()
    
    TRUST_TRANSACTION = auto()
    RECOMMENDATION_TRANSACTION = auto()
    
    DEBUG_ACCIDENT_STATUS = auto()

    # REPORTED_ACCIDENT = auto()
    # REPORTED_ACCIDENT_GENERAL = auto()
    REPORT = auto()