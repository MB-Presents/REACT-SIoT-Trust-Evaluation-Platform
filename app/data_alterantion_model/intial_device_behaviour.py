
from __future__ import annotations
from typing import Any, Dict, Union, TYPE_CHECKING



from data_models.iot_devices.common import DeviceBehaviour, DeviceType
from data.simulation.scenario_constants import Constants as sc
from experiments.settings import Settings

if TYPE_CHECKING:
    from data_models.iot_devices.device_handler import Devices_Group_Handler


def get_device_behaviour(devices : Devices_Group_Handler):
        
        smart_phones = devices.get(DeviceType.SMART_PHONE).all()
        vehicles = devices.get(DeviceType.VEHICLE).all()
        
        num_vehicles = len(vehicles)
        num_smartphones = len(smart_phones)
        
        num_dynamic_devices = num_vehicles + num_smartphones
        
        DEGREE_OF_MALICIOUS_NODES = 1 / Settings.PERCENTAGE_OF_MALICIOUS_VEHICLES
        
        device_behaviour = DeviceBehaviour.TRUSTWORTHY
        
        if num_dynamic_devices % DEGREE_OF_MALICIOUS_NODES == 0:
            device_behaviour = DeviceBehaviour.MALICIOUS
        return device_behaviour
