
from __future__ import annotations
from typing import TYPE_CHECKING

from typing import Dict
from traci import vehicle, edge,lane
from core.models.devices.common import DeviceInternalStatus, DeviceShapeStatus, DeviceType
from core.models.devices.vehicle import Vehicle




from core.models.events.simulation_events import SimulationEvent


from core.models.uniform.components.object_of_interest import ObjectOfInterest
from utils.simulation import is_object_in_simulation

from core.models.devices.device_handler import DevicesGroupHandler


if TYPE_CHECKING:

    from core.models.uniform.components.report import SendingPacket


def enable_accident_behaviour(collision : SimulationEvent):
    
    
    if not is_object_in_simulation(collision.catalyst_id):
        print(f"Vehicle {collision.catalyst_id} is not in the simulation anymore")
        return
    
    
    devices : DevicesGroupHandler = DevicesGroupHandler()
    vehicles : Dict[str, Vehicle] = devices.get_devices_by_group(DeviceType.VEHICLE)
    

    vehicle.setColor(collision.catalyst_id, (255, 0, 0, 255))
    
    
    vehicles[collision.catalyst_id]._internal_status = DeviceInternalStatus.INACTIVE
    vehicles[collision.catalyst_id]._shape_status = DeviceShapeStatus.DEFORMED
    
    
    vehicles[collision.catalyst_id]._shape_status = DeviceShapeStatus.DEFORMED
    
    
    
    
    edge_id = vehicle.getRoadID(collision.catalyst_id)
    
    # edge.setMaxSpeed(edge_id, AccidentSettings.ALLOWED_ACCIDENT_SPEED)
    # lane.setAllowed(collision.laneID, AccidentSettings.ALLOWED_EMERGENCY_VEHICLES)
    
    
    BRAKE_LIGHT_MASK = 0b1000
    EMERGENCY_BLINKER_MASK = 0b100
    
    accident_signals = BRAKE_LIGHT_MASK | EMERGENCY_BLINKER_MASK
    
    signals = int(accident_signals)
    
    vehicle.setSignals(collision.catalyst_id, signals)

    
def disable_accident_behaviour(accident_report: SendingPacket, color=(255, 255, 255, 255)):
    
    # A object may be not in the simulation anymore if the report has been a false prediction of the emergency center
    if not is_object_in_simulation(accident_report.object_of_interest.object_id):
        return
    
    devices : DevicesGroupHandler = DevicesGroupHandler()
    vehicles : Dict[str, Vehicle] = devices.get_devices_by_group(DeviceType.VEHICLE)
    
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


