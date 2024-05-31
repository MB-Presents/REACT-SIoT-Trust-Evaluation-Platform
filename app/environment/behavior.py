
from __future__ import annotations
from enum import Enum, auto
from typing import TYPE_CHECKING

from typing import Dict
from traci import vehicle, edge,lane
from data_models.iot_devices.common import DeviceInternalStatus, DeviceShapeStatus, DeviceType
from data_models.iot_devices.vehicle import Vehicle




from traci import constants as tc
from data_models.events.simulation_events import SimulationEvent


from scenario.emergency_response.constants import AccidentSettings
from utils.simulation import is_object_in_simulation

from data_models.iot_devices.device_handler import Devices_Group_Handler, get_devices_group_handler


if TYPE_CHECKING:
    from data_models.report_management.report.object_of_interest import ObjectOfInterest
    from data_models.report_management.report.report import SendingPacket


def enable_accident_behaviour(collision : SimulationEvent):
    
    
    if not is_object_in_simulation(collision.event_catalyst):
        print(f"Vehicle {collision.event_catalyst} is not in the simulation anymore")
        return
    
    
    devices : Devices_Group_Handler = get_devices_group_handler()
    vehicles : Dict[str, Vehicle] = devices.get(DeviceType.VEHICLE).all()
    

    vehicle.setColor(collision.event_catalyst, (255, 0, 0, 255))
    
    
    vehicles[collision.event_catalyst]._internal_status = DeviceInternalStatus.INACTIVE
    vehicles[collision.event_catalyst]._shape_status = DeviceShapeStatus.DEFORMED
    
    
    vehicles[collision.event_catalyst]._shape_status = DeviceShapeStatus.DEFORMED
    
    
    
    
    edge_id = vehicle.getRoadID(collision.event_catalyst)
    
    # edge.setMaxSpeed(edge_id, AccidentSettings.ALLOWED_ACCIDENT_SPEED)
    # lane.setAllowed(collision.laneID, AccidentSettings.ALLOWED_EMERGENCY_VEHICLES)
    
    
    BRAKE_LIGHT_MASK = 0b1000
    EMERGENCY_BLINKER_MASK = 0b100
    
    accident_signals = BRAKE_LIGHT_MASK | EMERGENCY_BLINKER_MASK
    
    signals = int(accident_signals)
    
    vehicle.setSignals(collision.event_catalyst, signals)

    
def disable_accident_behaviour(accident_report: SendingPacket, color=(255, 255, 255, 255)):
    
    # A object may be not in the simulation anymore if the report has been a false prediction of the emergency center
    if not is_object_in_simulation(accident_report.object_of_interest.object_id):
        return
    
    devices : Devices_Group_Handler = get_devices_group_handler()
    vehicles : Dict[str, Vehicle] = devices.get(DeviceType.VEHICLE).all()
    
    repaired_vehicle = accident_report.object_of_interest.object_id
    
    vehicles[repaired_vehicle]._internal_status = DeviceInternalStatus.ACTIVE
    vehicles[repaired_vehicle]._shape_status = DeviceShapeStatus.ORIGINAL_MANUFACTURED
    
    
    accident_vehicle : ObjectOfInterest = accident_report.object_of_interest
    vehicle.resume(accident_vehicle.object_id)
    
    vehicle.setColor(accident_vehicle.object_id, color)
    # lane.setAllowed(accident.laneID, AccidentSettings.ALLOWED_ROAD_VEHICLES)

    maxspeed = lane.getMaxSpeed(accident_vehicle.lane_id)
    edge.setMaxSpeed(accident_vehicle.edge_id, maxspeed)
    
    vehicle.setSignals(accident_vehicle.object_id,0)


