from core.models.uniform.components.report import SendingPacket
from core.simulation.logging import ObjectType
 
import utils.logging as logger
from traci import vehicle, simulation

import utils.logging as logger



def log_status(accident: SendingPacket):
    message = {
        'accident_id': str(accident._id),
        'accident_status': accident.event_status.name,
        'accident_vehicle': accident.object_of_interest.object_id,
        'accident_location': accident.object_of_interest.location,
    }
    logger.info(ObjectType.DEBUG_ACCIDENT_STATUS.name, message)

def set_vehicle_stop(self, emergency_veh_id, selected_edge: str, lane_position: float, laneIndex: int, parking_duration: int):
    vehicle_method = vehicle.resume if vehicle.isStopped(emergency_veh_id) else vehicle.replaceStop(emergency_veh_id, nextStopIndex=0, edgeID=selected_edge,
                pos=lane_position, laneIndex=laneIndex, duration=parking_duration)
    if len(vehicle.getStops(emergency_veh_id)) > 1:
        raise Exception(f"Emergency vehicle {emergency_veh_id} has more than one stop at time {simulation.getTime()} ")