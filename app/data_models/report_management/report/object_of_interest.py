
from __future__ import annotations
from typing import TYPE_CHECKING






if TYPE_CHECKING:
    from data_models.events.simulation_events import SimulationEvent
    from data_models.iot_devices.vehicle import Vehicle
    from scenario.emergency_response.emergency_vehicle import EmergencyVehicle
    from scenario.emergency_response.emergency_response import EmergencyResponseCenter
    from data_models.iot_devices.traffic_light import TrafficLightSystem
    from data_models.iot_devices.smart_phone import SmartPhone
    

from typing import List







class ObjectOfInterest:

    object_id: str = None
    location: List[float] = None
    edge_id: str = None
    lane_position: float = None
    lane_id: str = None

    def __init__(self, object_id: str, location: List[float], edge_id: str = None, lane_position: float = None, lane_id: str = None) -> None:

        self.object_id: str = object_id
        self.location: List[float] = location
        self.edge_id: str = edge_id
        self.lane_position: float = lane_position
        self.lane_id: str = lane_id

        pass

   