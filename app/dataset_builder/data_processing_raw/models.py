from enum import Enum, auto
from typing import List, NamedTuple
from core.models.events.simulation_events import EventState, EventType


class Event(NamedTuple):
    event_id: int
    status: EventState
    event_type: EventType
    event_catalyst: str
    time: float
    coordinates: List[float]
    authenticity: bool

class SituationClasses(Enum):
    
    AUTHENTIC_COLLISION = auto()
    UNAUTHENTIC_COLLISION = auto()
    
    AUTHENTIC_TRAFFIC_LIGHT_PRIORITY_REQUEST = auto()
    UNAUTHENTIC_TRAFFIC_LIGHT_PRIORITY_REQUEST = auto()
    
    OTHER_SITUATION = auto()
