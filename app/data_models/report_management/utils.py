from __future__ import annotations
from typing import TYPE_CHECKING, Dict




from typing import Dict, List, Union
from data_models.iot_devices.smart_phone import SmartPhone
from data_models.iot_devices.vehicle import Vehicle
from data_models.events.simulation_events import SimulationEvent
import traci.constants as tc
from data.simulation.scenario_constants import Constants as sc

from data_models.report_management.report.report_models import AuthenticityRole
from data_models.report_management.report.reporter import SendersEntity

from scenario.emergency_response.constants import AccidentSettings

if TYPE_CHECKING:
    from data_models.report_management.report.report import SendingPacket



def get_suitable_reporters(reporters: Dict[str, Union[SmartPhone,Vehicle]], collisions : Dict[str,SimulationEvent]) -> Dict[str, SendersEntity]:
    
    filtered_reporters : Dict[str,SendersEntity]= {}
    
    for reporter_id, reporter in reporters.items():
        if reporter._type not in AccidentSettings.ALLOWED_VEHICLE_REPORTER_TYPES:
            continue
        
        is_accident_vehicle = { collision.event_catalyst : collision for collision_key, collision in collisions.items() if collision.is_authentic}
        if reporter_id in is_accident_vehicle.keys(): 
            continue       
                 
    
        filtered_reporters[reporter_id] = SendersEntity(reporter,AuthenticityRole.AUTHENTIC,sc.TIME)
    return filtered_reporters


def can_report_accident(collision: SimulationEvent, reporter_id : str, reporter_object : dict, collisions : List[SimulationEvent]) -> bool:
    
    is_correct_object = reporter_object[tc.VAR_TYPE] in AccidentSettings.ALLOWED_VEHICLE_REPORTER_TYPES
    is_different_object = (reporter_id != collision.event_catalyst)
    collisions_vehicles = [collision.event_catalyst for collision in collisions]
    reporter_has_not_collision = reporter_id not in collisions_vehicles
    
    return is_different_object or is_correct_object or reporter_has_not_collision

def get_new_reporters(reporters : Dict[str, SendersEntity], report : SendingPacket) -> Dict[str, SendersEntity]:
    new_reporters : Dict[str, SendersEntity] = {}    
    for reporter_id, reporter_object in reporters.items():
        if reporter_id not in report.sending_entities.keys():
            new_reporters[reporter_id] = reporter_object
    
    return new_reporters