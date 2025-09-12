from __future__ import annotations
from typing import TYPE_CHECKING

from core.models.devices.common import DeviceBehaviour, DeviceType


from experiments.settings import Settings

if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler

def determine_device_behavior() -> DeviceBehaviour:
    """Determine the behavior of devices based on the proportion of malicious nodes."""
    smart_phones = DevicesGroupHandler().get_devices_by_group(DeviceType.SMART_PHONE)
    vehicles = DevicesGroupHandler().get_devices_by_group(DeviceType.VEHICLE)
    
    total_dynamic_devices = len(vehicles) + len(smart_phones)
    malicious_ratio = 1 / Settings.PERCENTAGE_OF_MALICIOUS_VEHICLES
    
    return (DeviceBehaviour.MALICIOUS 
            if total_dynamic_devices % malicious_ratio == 0 
            else DeviceBehaviour.TRUSTWORTHY)