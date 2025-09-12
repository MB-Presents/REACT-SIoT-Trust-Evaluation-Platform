

from __future__ import annotations
from typing import TYPE_CHECKING, Dict

import itertools
from typing import Callable, Dict, Union

import numpy as np

from core.data_alteration.alterations.data_alteration import get_alternated_data

from core.models.devices.common import DeviceBehaviour, DeviceType

from core.models.devices.device_handler import DevicesGroupHandler
from core.models.interfaces.function import IFunction
from core.models.interfaces.service import IService

from core.models.services.base_service import BaseService
from core.models.uniform.object_sensor_records import ObjectSensorRecords


if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
    from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import TrafficLightApplicationSettings
    from core.models.devices.induction_loop import InductionLoop
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.vehicle import Vehicle
    

class VehicleObjectDetectionService(BaseService):
    def __init__(self):
        
        self._functions: Dict[str, IFunction] = {}


    def get(self, device : Union[Vehicle, EmergencyVehicle]) -> Dict[str, IFunction]:
        assert device._type in [DeviceType.VEHICLE, DeviceType.EMERGENCY_VEHICLE], "VehicleObjectDetectionService can only be used by Vehicle or Emergency Vehicle devices."
        
        
        uniform_sensed_device_records = self.get_surrounding_objects(observer=device)


        return uniform_sensed_device_records

    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)



    def get_surrounding_objects(self, observer : Union[SmartPhone,Vehicle]) -> dict:
        
        assert observer._type in [DeviceType.VEHICLE, DeviceType.EMERGENCY_VEHICLE], "get_surrounding_objects can only be called by Vehicle, Emergency Vehicle or Smart Phone devices."
        
        object_sensor_records = ObjectSensorRecords()
        vehicles = DevicesGroupHandler().get_devices_by_group(DeviceType.VEHICLE)

        assert all(isinstance(v, Vehicle) for v in vehicles.values()), "All devices in vehicles must be instances of Vehicle class."
        

        observed_surrounding_vehicles = self._get_surrounding_vehicles_of(observer)



        for observed_vehicle_key, vehicle_object in observed_surrounding_vehicles.items():
            
            if observed_vehicle_key not in vehicles:
                continue
                
            if observer._device_behavior_profile._ground_truth == DeviceBehaviour.TRUSTWORTHY: 
                vehicle = vehicles[observed_vehicle_key]
                assert vehicle is not None, "Vehicle is None"
                assert isinstance(vehicle, Vehicle), "Vehicle must be an instance of Vehicle class."

                sensed_device = vehicle

            elif DeviceBehaviour.MALICIOUS == observer._device_behavior_profile._ground_truth:
                
                vehicle = vehicles[observed_vehicle_key]    
                assert vehicle is not None, "Vehicle is None"
                assert isinstance(vehicle, Vehicle), "Vehicle must be an instance of Vehicle class."
                
                sensed_device : Union[Vehicle, SmartPhone] = get_alternated_data(vehicle)
                
            assert observer, "Observer is None"
            assert sensed_device, "Sensed device is None"
            assert isinstance(sensed_device, (Vehicle, SmartPhone)), "Sensed device must be an instance of Vehicle or SmartPhone"
            
            object_sensor_records.add_record( observer, sensed_device)
            
        observer._sensed_devices = object_sensor_records.get_records_as_dict()
        
        
        return observer._sensed_devices


    def _get_surrounding_vehicles_of(self, monitoring_entity: Union[SmartPhone, Vehicle]) -> Dict[str, Vehicle]:
        # Pre-condition asserts
        assert monitoring_entity is not None, "Monitoring entity cannot be None"
        assert hasattr(monitoring_entity, '_position'), "Monitoring entity must have a '_position' attribute"
        assert isinstance(monitoring_entity._position, (list, tuple, np.ndarray)), "Monitoring entity's position must be a list, tuple, or numpy array"
        assert len(monitoring_entity._position) == 2, "Monitoring entity's position must have exactly two coordinates"

        vehicles = DevicesGroupHandler().get_devices_by_group(DeviceType.VEHICLE)
        assert isinstance(vehicles, dict), "Vehicles must be a dictionary"
        assert all(isinstance(v, Vehicle) for v in vehicles.values()), "All devices in vehicles must be instances of Vehicle class"

        observed_surrounding_vehicles = {}

        vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
        if vehicle_positions.shape[0] == 0:
            return observed_surrounding_vehicles

        assert vehicle_positions.shape[1] == 2, "Each vehicle position must have exactly two coordinates"

        distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
        assert isinstance(distance_threshold, (int, float)), "Distance threshold must be an integer or float"
        assert distance_threshold > 0, "Distance threshold must be positive"

        self_position = np.array(monitoring_entity._position)
        distances = np.linalg.norm(vehicle_positions - self_position, axis=1)
        

        observed_surrounding_vehicles = {
            veh_id: vehicles[veh_id]
            for veh_id, dist in zip(vehicles.keys(), distances)
            if dist <= distance_threshold and isinstance(vehicles[veh_id], Vehicle) and veh_id != monitoring_entity._id
        }

        # Post-condition asserts
        assert isinstance(observed_surrounding_vehicles, dict), "Observed surrounding vehicles must be a dictionary"
        assert all(isinstance(v, Vehicle) for v in observed_surrounding_vehicles.values()), "All observed vehicles must be instances of Vehicle class"

        return observed_surrounding_vehicles # type: ignore

