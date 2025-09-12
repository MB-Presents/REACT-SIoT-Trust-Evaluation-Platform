
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional

from abc import ABC, abstractmethod
from typing import Dict, Union

from traitlets import Any

if TYPE_CHECKING:
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.vehicle import Vehicle
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
    from core.models.devices.induction_loop import InductionLoop
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.vehicle import Vehicle
    

class IService(ABC):

    @abstractmethod
    def get(self, device : Union[SmartPhone, Vehicle, EmergencyVehicle, InductionLoop, TrafficCamera, TrafficLightSystem, EmergencyResponseCenter]) -> Optional[Dict[str, Union[SmartPhone, Vehicle, EmergencyVehicle, InductionLoop, TrafficCamera, TrafficLightSystem, EmergencyResponseCenter]]]:
        pass

    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> None:
        pass
