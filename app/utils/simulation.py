

from __future__ import annotations
from typing import TYPE_CHECKING


from core.models.events.simulation_events import VerificationState
from core.models.devices.common import DeviceType
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings


if TYPE_CHECKING:

    from core.models.uniform.components.report import SendingPacket
    from core.models.events.simulation_events import SimulationEvent, SimulationEventManager
    from core.models.devices.device_handler import DevicesGroupHandler, get_devices_group_handler
import core.models.devices.device_handler as handler
from traci import vehicle
from traci.exceptions import TraCIException


def is_object_in_simulation(object_id: str) -> bool:
    """Checks if the object is in the simulation.

    Args:
        object_id (str): The object id.

    Returns:
        bool: True if the object is in the simulation, False otherwise.
    """
    
    devices : DevicesGroupHandler = handler.get_devices_group_handler()
    existing_vehicles = devices.get_devices_by_group(DeviceType.VEHICLE)
    existing_smart_phones = devices.get_devices_by_group(DeviceType.VEHICLE)
    
    object_in_vehicles = object_id in existing_vehicles.keys()
    object_in_smart_phones = object_id  in existing_smart_phones.keys()
        
    
    return object_in_vehicles or object_in_smart_phones
    



def evaluate_authenticity(priorization_request_report : SendingPacket, trust_decision : VerificationState, simulation_manager: SimulationEventManager):
    events = simulation_manager.get_simulation_events()

    event : SimulationEvent = events[priorization_request_report.simulation_event.id]
    
    is_authentic = trust_decision == VerificationState.AUTHENTIC
    is_not_authentic = trust_decision == VerificationState.NOT_AUTHENTIC
    
    if event.is_authentic == True and is_authentic == True:
        return True
    if event.is_authentic == False and is_authentic == False: # True Negative
        return True
    if event.is_authentic == True and is_authentic == False :
        # False Positive: Emergency Call classified as wrong even though it was authenti
        return False 
    
    if event.is_authentic == False and is_authentic == True:
        # False Negative
        return False
    
    
def stop_vehicle(vehicle_key: str, stopping_edge: str, stopping_position: float):
    try:
        vehicle.slowDown(vehicle_key, 0, 1)
        if stopping_edge.startswith("666660152"):
            pass
        vehicle.insertStop(vehicle_key, nextStopIndex=0, edgeID=stopping_edge, pos=stopping_position, laneIndex=0, duration=AccidentSettings.INITIAL_EMEREGENCY_PARKING_TIME, teleport=0)
    
    except TraCIException as e:
        e.with_traceback(e.__traceback__)