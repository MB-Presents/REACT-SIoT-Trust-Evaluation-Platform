
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from core.models.devices.common import DeviceType, Service, Function



class IDeviceService(ABC):
    """Interface for device service operations"""

    @abstractmethod
    def execute_function(self, device: 'IDevice', function: 'Function', **kwargs) -> Any:
        pass

    @abstractmethod
    def get_service_for_device(self, device_type: 'DeviceType', service_type: 'Service') -> Optional['IService']:
        pass
