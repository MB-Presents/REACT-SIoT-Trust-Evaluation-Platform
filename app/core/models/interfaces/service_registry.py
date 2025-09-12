from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from core.models.devices.common import DeviceType, Service, Function
    from core.models.devices.genric_iot_device import GenericDevice


class IServiceRegistry(ABC):
    """Interface for service registry"""

    @abstractmethod
    def get_services(self, device_type: DeviceType, device: GenericDevice) -> Optional[Any]:
        pass

    
    