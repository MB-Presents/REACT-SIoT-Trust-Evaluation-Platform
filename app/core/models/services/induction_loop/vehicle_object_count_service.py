from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING






from typing import Dict, Union
from core.models.devices.common import DeviceType, Function
# from core.models.devices.device_handler import DevicesGroupHandler
from core.models.functions.measure.dimension import ObjectDimensionFunction
from core.models.functions.measure.speed import SpeedMeasurementFunction
from core.models.functions.measure.lane_position import LanePositionMeasurementFunction
from core.models.functions.detect.lane_id import LaneIDDetectionFunction
from core.models.functions.detect.street import StreetDetectionFunction

from core.models.interfaces.function import IFunction
from core.models.interfaces.service import IService
import traci

from core.models.services.base_service import BaseService

if TYPE_CHECKING:
    from core.models.devices.induction_loop import InductionLoop
    from core.models.devices.vehicle import Vehicle

class VehicleObjectCountService(BaseService):
    
    
    def __init__(self):

        from core.models.devices.device_handler import DevicesGroupHandler
        self.device_group_handler = DevicesGroupHandler()

        self._functions : Dict[str, IFunction] = {
            Function.GET_DIMENSIONS: ObjectDimensionFunction(),
            Function.GET_SPEED: SpeedMeasurementFunction(),
            Function.GET_LANE_POSITION: LanePositionMeasurementFunction(),
            Function.GET_LANE_ID: LaneIDDetectionFunction(),
            Function.GET_STREET: StreetDetectionFunction()
        }
        
        
    # def get_inductive_object_count(induction_loop: InductionLoop, devices: DevicesGroupHandler) -> Dict[str, Dict]:
    def get(self, induction_loop : InductionLoop) -> Dict[str, Dict]:
        """Retrieve vehicles detected by an induction loop with their attributes."""
        
        
        
        vehicles: Dict[str, Vehicle] = self.device_group_handler.get_devices_by_group(DeviceType.VEHICLE)
        vehicle_ids : Dict[str,Union[str,float]] = traci.edge.getLastStepVehicleIDs(induction_loop._observed_street)
        
        captured_vehicles = {
            veh_id: {
                'device_id': veh_id,
                'dimension': self._functions[Function.GET_DIMENSIONS].execute(veh_id),
                'speed': self._functions[Function.GET_SPEED].execute(veh_id),
                'lanePosition': self._functions[Function.GET_LANE_POSITION].execute(veh_id),
                'laneIndex': self._functions[Function.GET_LANE_ID].execute(veh_id),
                'laneID': self._functions[Function.GET_LANE].execute(veh_id),
                'edgeID': self._functions[Function.GET_STREET].execute(veh_id)
            }
            for veh_id in vehicle_ids if veh_id in vehicles
        }
        
        induction_loop._captured_vehicles_features = captured_vehicles
        return captured_vehicles
            

    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)