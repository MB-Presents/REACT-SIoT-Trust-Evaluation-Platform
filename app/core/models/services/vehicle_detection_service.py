from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING


import itertools
from git import Union
import numpy as np
from core.data_alteration.alterations.data_alteration import get_alternated_data
from core.models.devices import device_handler
from core.models.devices.common import DeviceBehaviour, DeviceType
from core.models.devices.common import DeviceType
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.vehicle import Vehicle
from core.models.interfaces.detection_service import IDetectionService
from core.models.uniform.device_sensor_records_manager import ObjectSensorRecordManager, ObjectSensorRecords
from core.models.uniform.sensed_object_record import SensedDeviceRecord

from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import TrafficLightApplicationSettings
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler
    


class VehicleDetectionService(IDetectionService):
    
    def get_color(self, device):
        return super().get_color(device)
    
    def get_position(self, device):
        return super().get_position(device)
    
    def get_objects(self, device : Union[SmartPhone, Vehicle]):
        
        id: int = itertools.count()

        
        object_sensor_records = ObjectSensorRecords()
    
        # service_provider_table = {}

        devices : DevicesGroupHandler  = device_handler.get_device_handler()
        vehicles : Dict[str, Union[Vehicle]] = devices.get_devices_by_group(DeviceType.VEHICLE)

        observed_surrounding_vehicles = self.get_surrounding_vehicles_of(self, vehicles)

        for observed_vehicle_key, vehicle_object in observed_surrounding_vehicles.items():
        
            if observed_vehicle_key not in vehicles:
                continue
                
            if device._device_behavior_profile._ground_truth == DeviceBehaviour.TRUSTWORTHY: 
                sensed_device = vehicles[observed_vehicle_key]
                
            elif DeviceBehaviour.MALICIOUS == device._device_behavior_profile._ground_truth:
                sensed_device = get_alternated_data(vehicles[observed_vehicle_key])
            
           
        
        object_sensor_records.add_record(SensedDeviceRecord(self, sensed_device)) 
        
        self._sensed_devices = object_sensor_records.get_records_as_dict()




    def get_surrounding_vehicles_of(self, vehicles : Dict[str, Vehicle]) -> Dict[str, Vehicle]:
    
        
        observed_surrounding_vehicles = {}
        
        vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
        if vehicle_positions.shape[0] == 0:
            observed_surrounding_vehicles = {}
        
        else:
            vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
            
            self_position = np.array(self._position)
            distances = np.linalg.norm(vehicle_positions - self_position, axis=1)
            distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
            observed_surrounding_vehicles = {veh_id: vehicles[veh_id] for veh_id, dist in zip(vehicles.keys(), distances) if dist <= distance_threshold}
        
        return observed_surrounding_vehicles






    # def add_sensed_device(service_provider_table, id, service_provider, sensed_device):
    #     record = SensedDeviceRecord(service_provider, sensed_device)
    #     key = (ScenarioParameters.TIME, service_provider._id, sensed_device._id)
    #     service_provider_table[key] = record.__dict__




# def get_detected_vehicles(traffic_camera: TrafficCamera, devices: DevicesGroupHandler) -> Dict[str, Vehicle]:
#     """Retrieve vehicles detected by a traffic camera across observed streets."""
#     traffic_camera._captured_vehicles = {}

#     vehicles = devices.get(DeviceType.VEHICLE)

#     for observed_edge in traffic_camera._observed_streets:
#         veh_id : str
#         for veh_id in edge.getLastStepVehicleIDs(observed_edge):
#             if veh_id.startswith("ped") or veh_id.startswith("bike"):
#                 continue
#             if veh_id in vehicles:
#                 traffic_camera._captured_vehicles[veh_id] = vehicles[veh_id]
    
#     return traffic_camera._captured_vehicles