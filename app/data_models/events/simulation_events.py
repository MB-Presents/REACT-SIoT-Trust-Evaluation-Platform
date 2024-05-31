

from __future__ import annotations
import copy
from enum import Enum, auto
import itertools
import json
from typing import Dict, List, Tuple, TYPE_CHECKING
from data.simulation.scenario_constants import Constants as sc
from traci import poi
from data_models.iot_devices.common import DeviceType
if TYPE_CHECKING:
    from data_models.iot_devices.device_handler import Devices_Group_Handler
    from data_models.iot_devices.vehicle import Vehicle


from data_models.simulation.logging import ObjectType

from traci import vehicle

import utils.logging as logger



class EventState(Enum):
    TRIGGERED = auto()
    ONGOING = auto()
    ONGING_FOR_15_MIN = auto()
    SOLVED = auto()
    REPORTED = auto()
    
class EventAuthenticity(Enum):
    TRUE = auto()
    FALSE = auto()




class VerificationState(Enum):
    AUTHENTIC = auto()
    NOT_AUTHENTIC = auto()
    UNVERIFIED = auto()
    NOT_VERIFIEDABLE = auto() # has left already


class EventType(Enum):
    COLLISION = auto()
    TRAFFIC_LIGHT_PRIORITY_REQUEST = auto()


class EventState(Enum):
    SCHEDULED = auto()
    TRIGGERED = auto()
    ONGOING = auto()
    ONGING_FOR_15_MIN = auto()
    REPORTED = auto()
    VERIFIED = auto()
    SOLVED = auto()

class EventRecord:
    
    def __init__(self, event_id : int, event_state : EventState, time : int, location : List[float]):
        self.event_id : int = event_id
        self.event_state : EventState = event_state
        self.time : int = time
        self.location : List[float] = location
    


class SimulationEvent:

    id : int = itertools.count() 
    
    def __init__(self, event_catalyst : str, eventType : EventType, event_location : List[float], time : str, authenticity : bool, event_state : EventState = EventState.TRIGGERED):
        
        self.id : int = next(SimulationEvent.id)
        self.event_catalyst : str = event_catalyst
        self.situation : EventType = eventType
        self.location : List[float] = event_location
        self.time : int = time
        self.is_authentic : bool = authenticity
        self.state : EventState = None
        
            
        self.event_history : Dict[str,EventRecord] = {}
        event_record: EventRecord = EventRecord(self.id, event_state, self.time, self.location)
        
        self.update_state(event_record)
        
        
    def get_color_code(self, event_type : EventType, authenticity : bool) -> List[Tuple]:
        
        color: List[Tuple] = (252.0, 186.0, 3.0, 255.0)
        
        if event_type == EventType.COLLISION and self.is_authentic:
            color = (252.0, 186.0, 3.0, 255.0)
            
        elif event_type == EventType.COLLISION and not self.is_authentic:
            color = (252.0, 40.0, 3.0, 255.0)  
            
        elif event_type == EventType.TRAFFIC_LIGHT_PRIORITY_REQUEST and self.is_authentic:
            color = (78.0, 3.0, 252.0, 255.0)
            
        elif event_type == EventType.TRAFFIC_LIGHT_PRIORITY_REQUEST and not self.is_authentic:
            color = (215.0, 3.0, 252.0,255.0)
        
        
        return color
        
        
    def update_state(self, event_record : EventRecord):
        
        if event_record.event_state == self.state:
            return
        
        if event_record.event_state == EventState.TRIGGERED:
                
            self.location = vehicle.getPosition(self.event_catalyst)
            self.mark_as_triggered()
            
        
        self.event_history[event_record.event_state.name] = event_record
        self.state = event_record.event_state
        
        
        event  = copy.copy(self)
        
        
        
        try:
            del event.event_history
            
            # del event.poi_id
            
            event.situation = event.situation.name
            event.state = event.state.name
            
            event_dict = event.__dict__
            
            
            # event_json = json.dumps(event_dict)
            logger.info(ObjectType.EVENT, event_dict)
        
            
        except Exception as e:
            logger.error(ObjectType.EVENT,e.__dict__)
            
    def mark_as_triggered(self):
        
        self.poi_id: str = "event_" + str(self.id) + "_time_" + sc.TIME_STRING + "_vehId_" + self.event_catalyst + "_auth_" + str(self.is_authentic) + "_type_" + self.situation.name

        type   : str = 'accident_reporter_location'

        x: float = self.location[0]
        y: float = self.location[1]

        color: List[Tuple] = self.get_color_code(self.situation, self.is_authentic)

        poi.add(self.poi_id, x, y, color, type, layer=5, width=50000, height=50000)
        
            
    def is_valid_accident_event(self):
    
        valid_states = {EventState.TRIGGERED, EventState.ONGOING, EventState.REPORTED}
        return self.is_authentic and self.state in valid_states and sc.TIME - self.event_history[EventState.TRIGGERED.name].time > 20
            

class SimulationEventManager:


    
    simulation_events : Dict[str,SimulationEvent] = {}
    
    
    def __init__(self, devices) -> None:
        self.simulation_events = {}
        self.devices : Devices_Group_Handler = devices
        
    def get_simulation_events(self) -> Dict[str,SimulationEvent]:
        return self.simulation_events

    def get_simulation_events_by_event(self, type : EventType) -> Dict[str,SimulationEvent]:
        
        filtered_events : Dict[str,SimulationEvent] = {}
        
        for event_id, event in self.simulation_events.items():
            if event.situation == type:
                filtered_events[event.id]=event
        
        return filtered_events


    def get_simulation_events_by_event_and_authenticity(self, type : EventType) -> Dict[str,SimulationEvent]:
        
        filtered_events : Dict[str,SimulationEvent] = {}
        
        for event_id, event in self.simulation_events.items():
            if event.situation == type and event.is_authentic == True:
                filtered_events[event.id]=event
        
        return filtered_events


    def get_event_catalyst_object(self,  event: SimulationEvent) -> Vehicle:
        
        
        
        vehicles = self.devices.get(DeviceType.VEHICLE).all()
        vehicle_id = event.event_catalyst

        if vehicle_id not in vehicles or not vehicle.isStopped(vehicle_id):
            return None

        return vehicles[vehicle_id]






    def exists_for_vehicle(self, vehicle_id : str) -> bool:
        
        for event_id, event in self.simulation_events.items():
            if event.event_catalyst == vehicle_id:
                return True
        return False

    def filter_events(self, event_type : EventType) -> Dict[str,SimulationEvent]:
        
        filtered_events : Dict[str,SimulationEvent] = {}
        
        for event_id, event in self.simulation_events.items():
            if event.situation == event_type:
                filtered_events[event.id] = event
        
        return filtered_events
    
    
    def add(self, event : SimulationEvent):
        self.simulation_events[event.id] = event
        
        
    
    def update_events(self):
        
        for event_id, event in self.simulation_events.items():
            
            if event.state == EventState.TRIGGERED and event.is_authentic == True:
                
                event_record: EventRecord = EventRecord(event.id, EventState.ONGOING, sc.TIME, event.location)
                event.update_state(event_record)
                
    
            elif event.state == EventState.ONGOING and (sc.TIME - float(event.time)) > 900:
                event_record: EventRecord = EventRecord(event.id, EventState.ONGING_FOR_15_MIN, sc.TIME, event.location)
                event.update_state(event_record)
         
               
            elif event.state == EventState.REPORTED:
                pass
            
            elif event.state == EventState.SOLVED:
                pass
            
            elif event.state == EventState.ONGOING:
                pass
    
    def remove(self, event_id : int):
        self.simulation_events.pop(event_id)
    
    
    def get_scheduled_events(self,event_type : EventType) -> Dict[str,SimulationEvent]:
        
        filtered_events : Dict[str,SimulationEvent] = {}
        
        for event_id, event in self.simulation_events.items():
            if event.situation == event_type and event.state == EventState.SCHEDULED:
                filtered_events[event.id] = event
        
        return filtered_events
    
    
    def create_event(self,reporter_id , vehicle : Vehicle, event_type : EventType, authenticity : bool, event_state : EventState):
        
        
        event = SimulationEvent(event_catalyst=reporter_id,
                                eventType=event_type,
                                event_location=vehicle._position,
                                time=sc.TIME,
                                authenticity=authenticity,
                                event_state=event_state)
        return event
    
    
    
    def get_new_collision_events(self, veh_id : str, schedulued_collisions : Dict[str, SimulationEvent], vehicle : Vehicle):
        new_events = {}
        
        for event_id, event in schedulued_collisions.items():
            if veh_id == event.event_catalyst:
                            
                new_events[event_id] = event

        return new_events 