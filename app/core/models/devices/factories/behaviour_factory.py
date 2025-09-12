



from abc import ABC, abstractmethod
import re

from git import Optional
from core.data_alteration.common import AlterationType, SignificanceLevel
from core.models.devices.common import DeviceBehaviour


class IDeviceBehaviour(ABC):
    @abstractmethod
    def get_alteration_type(self) -> AlterationType:
        pass

    @abstractmethod
    def get_significance_level(self) -> SignificanceLevel:
        pass
    


class DeviceBehaviorProfile:
    def __init__(self, alteration_type: Optional[AlterationType], significance_level: Optional[SignificanceLevel], device_behaviour : DeviceBehaviour):
        self._alteration_type : Optional[AlterationType] = alteration_type
        self._significance_level : Optional[SignificanceLevel] = significance_level
        self._ground_truth : DeviceBehaviour = device_behaviour



class DeviceBehaviourFactory:


    @staticmethod
    def create(device_behaviour : DeviceBehaviour) -> DeviceBehaviorProfile:
        if DeviceBehaviour.TRUSTWORTHY == device_behaviour:
            return DeviceBehaviorProfile(alteration_type=None, significance_level=None, device_behaviour=DeviceBehaviour.TRUSTWORTHY)
        elif DeviceBehaviour.MALICIOUS == device_behaviour:
            return DeviceBehaviorProfile(AlterationType.DYNAMIC, SignificanceLevel.SIGNIFICANT, DeviceBehaviour.MALICIOUS)
        raise ValueError(f"Unknown device behaviour: {device_behaviour}")

