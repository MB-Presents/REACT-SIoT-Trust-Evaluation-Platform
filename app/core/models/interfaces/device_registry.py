from typing import Dict, Any, Optional, Protocol, Union

from core.models.devices.common import DeviceType
from core.models.devices.induction_loop import InductionLoop
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.traffic_camera import TrafficCamera
from core.models.devices.traffic_light import TrafficLightSystem
from core.models.devices.vehicle import Vehicle
from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle



class IDeviceRegistry(Protocol):
    """Interface for device discovery and state access"""
    def get_devices_by_group(self, device_type: DeviceType) -> Dict[str, TrafficCamera | Vehicle | InductionLoop | EmergencyVehicle | SmartPhone | EmergencyResponseCenter | TrafficLightSystem]: ...
    def get_device(self, device_id: str) -> TrafficCamera | Vehicle | InductionLoop | EmergencyVehicle | SmartPhone | EmergencyResponseCenter | TrafficLightSystem: ...
    def get_devices(self) -> Dict[str, TrafficCamera | Vehicle | InductionLoop | EmergencyVehicle | SmartPhone | EmergencyResponseCenter | TrafficLightSystem]: ...

