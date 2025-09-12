from __future__ import annotations
from typing import TYPE_CHECKING, Dict

import itertools
from typing import Dict, Union
from unittest.mock import Base

import numpy as np

from core.data_alteration.alterations.data_alteration import get_alternated_data
from core.models.devices.common import DeviceBehaviour, DeviceType

from core.models.interfaces.function import IFunction
from core.models.interfaces.service import IService

from core.models.services.base_service import BaseService
from core.models.uniform.object_sensor_records import ObjectSensorRecords
from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import TrafficLightApplicationSettings


if TYPE_CHECKING:
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.vehicle import Vehicle


class ObjectProximityService(BaseService):
    """Service to handle object proximity detection for mobile devices."""

    def __init__(self):
        self._functions : Dict[str, IFunction] = {}
        
        from core.models.devices.device_handler import DevicesGroupHandler
        self.device_handler = DevicesGroupHandler
        
        
    
    def get(self, ):
        return super().get()
    
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)
        
    
    
    def get_surrounding_objects(self, observer : Union[SmartPhone,Vehicle], mobile_device : dict) -> dict:
        
        id: int = itertools.count()
        
        service_provider_table = {}

        object_sensor_records = ObjectSensorRecords()

        vehicles = self.device_handler.get_devices_by_group(DeviceType.VEHICLE)

        observed_surrounding_vehicles = self._get_surrounding_vehicles_of(observer)

        for observed_vehicle_key, vehicle_object in observed_surrounding_vehicles.items():
            
            if observed_vehicle_key not in vehicles:
                continue
                
            if observer._device_behavior_profile._ground_truth == DeviceBehaviour.TRUSTWORTHY: 
                sensed_device = vehicles[observed_vehicle_key]

            elif DeviceBehaviour.MALICIOUS == observer._device_behavior_profile._ground_truth:
                sensed_device = get_alternated_data(vehicles[observed_vehicle_key])
                
            object_sensor_records.add_record(observer, sensed_device)

        observer._sensed_devices = object_sensor_records.get_records_as_dict()

        return observer._sensed_devices
        

    def _get_surrounding_vehicles_of(self, monitoring_entity : Union[SmartPhone,Vehicle]):

        vehicles = self.device_handler.get_devices_by_group(DeviceType.VEHICLE)
        
        observed_surrounding_vehicles = {}
        
        vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
        if vehicle_positions.shape[0] == 0:
            observed_surrounding_vehicles = {}
        
        else:
            vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
            
            self_position = np.array(monitoring_entity._position)
            distances = np.linalg.norm(vehicle_positions - self_position, axis=1)
            distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
            observed_surrounding_vehicles = {veh_id: vehicles[veh_id] for veh_id, dist in zip(vehicles.keys(), distances) if dist <= distance_threshold}
        
        return observed_surrounding_vehicles