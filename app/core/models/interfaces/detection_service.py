



from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, Tuple, Union
from core.models.devices.genric_iot_device import GenericDevice
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.vehicle import Vehicle


class IDetectionService(ABC):
    
    
    @abstractmethod
    def get_color(self, device: GenericDevice) -> Optional[str]:
        pass
    
    @abstractmethod
    def get_position(self, device: GenericDevice) -> Optional[Tuple[float, float, float]]:
        pass

    @abstractmethod
    def get_objects(self, device: Union[SmartPhone, Vehicle]) -> Dict[str, GenericDevice]:
        pass