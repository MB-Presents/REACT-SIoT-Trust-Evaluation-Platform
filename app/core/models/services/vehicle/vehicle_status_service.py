


from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict


from typing import Dict, Union



from core.models.devices.common import Function
from core.models.functions.detect.color import ColorDetectionFunction
from core.models.functions.detect.lane import LaneDetectionFunction
from core.models.functions.detect.lane_id import LaneIDDetectionFunction
from core.models.functions.detect.signal import SignalDetectionFunction
from core.models.functions.detect.street import StreetDetectionFunction
from core.models.functions.measure.lane_position import LanePositionMeasurementFunction
from core.models.functions.measure.object_position import PositioningFunction
from core.models.functions.measure.speed import SpeedMeasurementFunction
from core.models.interfaces.function import IFunction
from core.models.interfaces.service import IService
from core.models.services.base_service import BaseService


if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.vehicle import Vehicle
    from core.models.devices.induction_loop import InductionLoop
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle

class VehicleStatusService(BaseService):
    def __init__(self):
        
        self._functions : Dict[Function, IFunction] = {
            Function.GET_SPEED: SpeedMeasurementFunction(),
            Function.GET_POSITION: PositioningFunction(),
            Function.GET_STREET: StreetDetectionFunction(),
            Function.GET_LANE: LaneDetectionFunction(),
            Function.GET_LANE_ID: LaneIDDetectionFunction(),
            Function.GET_SIGNAL: SignalDetectionFunction(),
            Function.GET_LANE_POSITION: LanePositionMeasurementFunction(),
            Function.GET_COLOR: ColorDetectionFunction()
        }
        
    def get(self, device : Union[SmartPhone, Vehicle, EmergencyVehicle, InductionLoop, TrafficCamera, TrafficLightSystem, EmergencyResponseCenter]) -> Dict[str, Union[float,str,int]]:
        
        assert isinstance(device, (Vehicle, EmergencyVehicle)), "VehicleStatusService can only be used by Vehicle or Emergency Vehicle devices."
        result = {}
        for key, function in self._functions.items():
            
            result[key] = function.execute(device=device)
        return result
    
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)