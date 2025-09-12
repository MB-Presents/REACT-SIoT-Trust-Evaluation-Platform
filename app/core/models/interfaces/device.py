from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from core.models.devices.common import DeviceType, Service, Function


class IDevice(ABC):
    """Interface for device implementations"""

    @abstractmethod
    def get_device_id(self) -> str:
        pass

    @abstractmethod
    def get_device_type(self) -> 'DeviceType':
        pass

    @abstractmethod
    def update_position(self, position: List[float]) -> None:
        pass

    @abstractmethod
    def get_position(self) -> List[float]:
        pass
