from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from core.models.devices.common import DeviceType, Service, Function


class IDeviceHandler(ABC):
    """Interface for device handling operations"""

    @abstractmethod
    def get_device_by_key(self, key: str) -> Any:
        pass

    @abstractmethod
    def get_devices(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get(self, device_type: 'DeviceType') -> Any:
        pass
