
from sched import Event

from typing import Dict, Any, Tuple
from dataclasses import dataclass, field
import uuid

from core.models.devices.common import DeviceType
from core.models.events.simulation_events import EventPriority, EventRecord, EventState, EventTriggerType, EventType
from core.models.uniform.components import object_of_interest
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentStatus
from scenarios.canberra_case_study.apps.events import trigger



@dataclass
class BaseEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default=0.0)
    reporter: str = ""
    object_of_interest : str = ""
    location: Tuple[float, float] = (0.0, 0.0)
    priority : EventPriority = EventPriority.NORMAL
    trigger_type : EventTriggerType = EventTriggerType.IMMEDIATE
    event_history: Dict[EventState, EventRecord] = field(default_factory=dict)
    ground_truth: bool = True
    authenticity : bool = True
    
@dataclass
class CollisionEvent(Event):
    event_type: EventType = EventType.COLLISION

@dataclass
class CollisionDetectionEvent(CollisionEvent):
    event_type: EventType = EventType.COLLISION



@dataclass
class TrafficLightRequestEvent(BaseEvent):
    receiver: str = ""
    
class EmergencyVehicleDispatchEvent(BaseEvent):
    receiver: str = ""
    accident_id: str = ""



# @dataclass
# class DeviceStateChangedEvent(BaseEvent):
#     device_id: str = ""
#     device_type: DeviceType = None
#     old_state: Dict[str, Any] = field(default_factory=dict)
#     new_state: Dict[str, Any] = field(default_factory=dict)

# @dataclass
# class AccidentReportEvent(BaseEvent):
#     accident_id: str = ""
#     status: AccidentStatus = None
#     location: Tuple[float, float] = (0.0, 0.0)
#     report_data: Dict[str, Any] = field(default_factory=dict)
    
# @dataclass
# class DeviceCreatedEvent(BaseEvent):
#     device_id: str = ""
#     device_type: DeviceType = None



@dataclass
class TimeStepEvent(BaseEvent):
    step: int = 0
    dt: float = 0.0