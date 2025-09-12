from __future__ import annotations
from typing import TYPE_CHECKING



from abc import ABC, abstractmethod

from core.models.devices.common import DeviceComputationCapabilityClass, DeviceType

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice




class IComputationCapability(ABC):

    @abstractmethod
    def create_capability_class(self) -> DeviceComputationCapabilityClass:
        pass


class ComputationCapabilityFactory:
    
    @staticmethod
    def create(device_type : DeviceType) -> DeviceComputationCapabilityClass:
        factory_map = {
            DeviceType.INDUCTION_LOOP: LowCapabilityFactory(),
            DeviceType.TRAFFIC_LIGHT: LowCapabilityFactory(),
            DeviceType.SMART_PHONE: MediumCapabilityFactory(),
            DeviceType.TRAFFIC_CAMERA: MediumCapabilityFactory(),
            DeviceType.VEHICLE: HighCapabilityFactory(),
            DeviceType.EMERGENCY_CENTER: HighCapabilityFactory(),
        }

        assert device_type in factory_map, f"Computation capability factory for {device_type} not found."

        capability_factory : IComputationCapability =  factory_map[device_type]
        return capability_factory.create_capability_class()


class LowCapabilityFactory(IComputationCapability):
    def create_capability_class(self) -> DeviceComputationCapabilityClass:
        return DeviceComputationCapabilityClass.LOW

class MediumCapabilityFactory(IComputationCapability):
    def create_capability_class(self) -> DeviceComputationCapabilityClass:
        return DeviceComputationCapabilityClass.MEDIUM

class HighCapabilityFactory(IComputationCapability):
    def create_capability_class(self) -> DeviceComputationCapabilityClass:
        return DeviceComputationCapabilityClass.HIGH

class UndefinedCapabilityFactory(IComputationCapability):
    def create_capability_class(self) -> DeviceComputationCapabilityClass:
        return DeviceComputationCapabilityClass.UNDEFINED

