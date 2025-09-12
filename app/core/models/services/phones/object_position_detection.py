
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Union


from typing import Dict


from core.models.interfaces.function import IFunction
from core.models.interfaces.service import IService
from core.models.services.base_service import BaseService

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
    from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import TrafficLightApplicationSettings
    from core.models.devices.induction_loop import InductionLoop
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.vehicle import Vehicle

class ObjectPositionDetectionService(BaseService):
    """Service to handle object position detection for mobile devices."""

    def __init__(self):
        self._functions: Dict[str, IFunction] = {}

    
    def get(self, device : Union[SmartPhone, Vehicle, EmergencyVehicle, InductionLoop, TrafficCamera, TrafficLightSystem, EmergencyResponseCenter]):
        return super().get(device=device)
    
    
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)