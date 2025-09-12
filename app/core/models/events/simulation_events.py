from __future__ import annotations
import re
from typing import TYPE_CHECKING, Dict, List, Tuple
import copy
import itertools
import json
from enum import Enum, auto

from traci import poi
import traci
from zmq import IMMEDIATE
from core.models.devices.common import DeviceType
from core.simulation.logging import ObjectType
from core.simulation.simulation_context import SimulationContext
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

import utils.logging as logger

if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler
    from core.models.devices.vehicle import Vehicle
    

class EventState(Enum):
    SCHEDULED = auto()
    TRIGGERED = auto()
    ONGOING = auto()
    ONGOING_15_MIN = auto()
    REPORTED = auto()
    VERIFIED = auto()
    SOLVED = auto()

class EventAuthenticity(Enum):
    TRUE = auto()
    FALSE = auto()

class VerificationState(Enum):
    AUTHENTIC = auto()
    NOT_AUTHENTIC = auto()
    UNVERIFIED = auto()
    NOT_VERIFIABLE = auto()


class EventPriority(Enum):
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()
    EMERGENCY = auto()

class EventTriggerType(Enum):
    IMMEDIATE = auto()
    INTERVAL = auto()
    CONDITION = auto()
    SCHEDULED = auto()


class EventType(Enum):
    COLLISION = auto()
    TRAFFIC_LIGHT_PRIORITY_REQUEST = auto()

class EventRecord:
    """A record capturing the state of an event at a specific time and location."""
    def __init__(self, event_id: int, state: EventState, time: float, location: Tuple[float, float]):
        self.event_id: int = event_id
        self.state: EventState = state
        self.time: float = time
        self.location: Tuple[float, float] = location

class SimulationEvent:
    """Represents a simulation event with state, type, and authenticity."""
    _id_counter = itertools.count()

    def __init__(self, catalyst_id: str, event_type: EventType, location: Tuple[float, float], 
                 time: int, is_authentic: bool, state: EventState = EventState.TRIGGERED):
        self.id: int = next(self._id_counter)
        self.catalyst_id: str = catalyst_id
        self.event_type: EventType = event_type
        self.location: Tuple[float, float] = location
        self.time: int = time
        self.is_authentic: bool = is_authentic
        self.state: EventState = state
        self.event_history: Dict[str, EventRecord] = {}
        self.poi_id: str | None = None

        initial_record = EventRecord(self.id, state, time, location)
        self._update_state(initial_record)

    def get_color_code(self) -> Tuple[float, float, float, float]:
        """Return the color code for the event based on type and authenticity."""
        color_map = {
            (EventType.COLLISION, True): (252.0, 186.0, 3.0, 255.0),
            (EventType.COLLISION, False): (252.0, 40.0, 3.0, 255.0),
            (EventType.TRAFFIC_LIGHT_PRIORITY_REQUEST, True): (78.0, 3.0, 252.0, 255.0),
            (EventType.TRAFFIC_LIGHT_PRIORITY_REQUEST, False): (215.0, 3.0, 252.0, 255.0),
        }
        return color_map.get((self.event_type, self.is_authentic), (252.0, 186.0, 3.0, 255.0))

    def _update_state(self, record: EventRecord) -> None:
        """Update the event's state and log the change."""
        if record.state == self.state:
            return

        if record.state == EventState.TRIGGERED:
            self.location = traci.vehicle.getPosition(self.catalyst_id)
            self._mark_as_triggered()

        self.event_history[record.state.name] = record
        self.state = record.state

        event_data = copy.copy(self)
        
        assert isinstance(self.event_type, EventType), "event_type is not an instance of EventType"
        assert isinstance(self.state, EventState), "state is not an instance of EventState"
        assert isinstance(event_data, SimulationEvent), "event_data is not an instance of EventType"

        event_data.catalyst_id = self.catalyst_id
        event_data.location = self.location
        event_data.time = self.time
        event_data.is_authentic = self.is_authentic
            
        event_dict = {k: v for k, v in event_data.__dict__.items() if k != 'event_history'}

        try:
            logger.info(ObjectType.EVENT.name, event_dict)
        except Exception as e:
            logger.error(ObjectType.EVENT.name, str(e))

    def _mark_as_triggered(self) -> None:
        """Mark the event as triggered and add it to the simulation as a point of interest."""
        self.poi_id = (
            f"event_{self.id}_time_{ScenarioParameters.TIME}"
            f"_vehId_{self.catalyst_id}_auth_{self.is_authentic}_type_{self.event_type.name}"
        )
        
        poi.add(
            self.poi_id, self.location[0], self.location[1], self.get_color_code(),
            poiType="accident_reporter_location", layer=5, width=50000, height=50000
        )
        
        
    def is_valid_accident(self) -> bool:
        """Determine if the event qualifies as a valid accident based on its state and elapsed time."""
        valid_states = {EventState.TRIGGERED, EventState.ONGOING, EventState.REPORTED}
        triggered_record = self.event_history.get(EventState.TRIGGERED.name)

        assert isinstance(self, SimulationEvent), "self is not an instance of SimulationEvent"
        assert isinstance(self.state, EventState), "state is not an instance of EventState"
        assert isinstance(triggered_record, EventRecord), "triggered_record is not an instance of EventRecord"
        
        if not self.is_authentic or  self.state not in valid_states or not triggered_record or ScenarioParameters.TIME - triggered_record.time <= 20:
            return False

        return True

class SimulationEventManager:
    """Manages simulation events, including creation, updates, and filtering."""

    
    def __init__(self, simulation_context : SimulationContext) -> None:
        self.events: Dict[int, SimulationEvent] = {}
        self.context = simulation_context   
        
        self.context.register_simulation_event_manager(self)
                
    def get_all_events(self) -> Dict[int, SimulationEvent]:
        """Return all simulation events."""
        return self.events

    def get_events_by_type(self, event_type: EventType) -> Dict[int, SimulationEvent]:
        """Return events filtered by event type."""
        return {eid: event for eid, event in self.events.items() if event.event_type == event_type}

    def get_authentic_events_by_type(self, event_type: EventType) -> Dict[int, SimulationEvent]:
        """Return authentic events filtered by event type."""
        return {
            eid: event for eid, event in self.events.items()
            if event.event_type == event_type and event.is_authentic
        }

    def get_catalyst_vehicle(self, event: SimulationEvent) -> Vehicle | None:
        """Return the vehicle associated with the event's catalyst, if stopped."""
        assert self.context is not None, "Simulation context is None"
        assert self.context._device_registry is not None, "Device registry is None in simulation context"
        

        devices = self.context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        assert all(isinstance(v, Vehicle) for v in devices.values()), "Not all devices in vehicles are of type Vehicle"
        vehicles: Dict[str, Vehicle] = {k: v for k, v in devices.items() if isinstance(v, Vehicle)}
        

        assert event.catalyst_id in vehicles, f"Vehicle with ID {event.catalyst_id} not found in devices"
        vehicle: Vehicle = vehicles[event.catalyst_id]

        assert isinstance(vehicle, Vehicle), f"Device with ID {event.catalyst_id} is not of type Vehicle"

        if event.catalyst_id not in vehicles or not traci.vehicle.isStopped(event.catalyst_id):
            return None

        vehicle = vehicles[event.catalyst_id]
        assert isinstance(vehicle, Vehicle), f"Device with ID {event.catalyst_id} is not of type Vehicle"

        return vehicle

    def has_event_for_vehicle(self, vehicle_id: str) -> bool:
        """Check if an event exists for the given vehicle ID."""
        return any(event.catalyst_id == vehicle_id for event in self.events.values())

    def get_scheduled_events(self, event_type: EventType) -> Dict[int, SimulationEvent]:
        """Return scheduled events filtered by event type."""
        return {
            eid: event for eid, event in self.events.items()
            if event.event_type == event_type and event.state == EventState.SCHEDULED
        }
        
    def get_event_by_id(self, id : int) -> SimulationEvent:
        return self.events[id]
        
        
    

    def create_event(self, reporter_id: str, vehicle: Vehicle, event_type: EventType, 
                     is_authentic: bool, state: EventState) -> SimulationEvent:
        """Create a new simulation event and add it to the manager."""
        
        assert isinstance(vehicle, Vehicle), f"Device with ID {reporter_id} is not of type Vehicle"
        assert isinstance(vehicle._position, tuple), f"Vehicle position is not a tuple for vehicle {reporter_id} at time {ScenarioParameters.TIME}"
        assert isinstance(ScenarioParameters.TIME, int), "ScenarioParameters.TIME is not an integer"
        
        
        event = SimulationEvent(
            catalyst_id=reporter_id,
            event_type=event_type,
            location=vehicle._position,
            time=ScenarioParameters.TIME,
            is_authentic=is_authentic,
            state=state
        )
        self.add_event(event)
        return event

    def add_event(self, event: SimulationEvent) -> None:
        """Add an event to the manager."""
        self.events[event.id] = event

    def update_events(self) -> None:
        """Update the state of all managed events based on time and conditions."""
        for event in self.events.values():
            if event.state == EventState.TRIGGERED and event.is_authentic:
                record = EventRecord(event.id, EventState.ONGOING, ScenarioParameters.TIME, event.location)
                event._update_state(record)
            elif event.state == EventState.ONGOING and (ScenarioParameters.TIME - event.time) > 900:
                record = EventRecord(event.id, EventState.ONGOING_15_MIN, ScenarioParameters.TIME, event.location)
                event._update_state(record)

    def remove_event(self, event_id: int) -> None:
        """Remove an event by its ID."""
        self.events.pop(event_id, None)

    def get_new_collision_events(self, vehicle_id: str, scheduled_collisions: Dict[int, SimulationEvent]) -> Dict[int, SimulationEvent]:
        """Return new collision events for the specified vehicle from scheduled collisions."""
        return {
            eid: event for eid, event in scheduled_collisions.items()
            if event.catalyst_id == vehicle_id
        }