from __future__ import annotations
import copy
from typing import TYPE_CHECKING, Dict

import random
# from turtle import position


from traci import vehicle, simulation, person
from traci import constants as tc
from data.simulation.scenario_constants import Constants as sc
from typing import Dict, List
from data_alterantion_model.generate_device_profiles import generate_profiles
from data_alterantion_model.intial_device_behaviour import get_device_behaviour
from data_models.iot_devices.common import DeviceRecordType, DeviceType, Function, Service

from data_models.services.service import ServiceRegistry
from data_models.simulation.logging import ObjectType
from data_models.iot_devices.genric_iot_device import DeviceBehaviour
from data_models.iot_devices.genric_iot_device import GenericDevice

# if TYPE_CHECKING:

import utils.logging as logger




class SmartPhone(GenericDevice):

    def __init__(self, smart_phone_id: str, position: List[float], speed: float, lane_position, edge_id, lane_id, manufacturer: str, model: str, firmware_version: str, hardware_version: str, serial_number: str, date_of_manufacture: str, last_maintenance_date: str, next_maintenance_date: str, device_behaviour : DeviceBehaviour) -> None:
        
        super().__init__(device_id=smart_phone_id, position=position, device_type=DeviceType.SMART_PHONE, manufacturer=manufacturer, model=model, firmware_version=firmware_version, hardware_version=hardware_version, serial_number=serial_number, date_of_manufacture=date_of_manufacture, last_maintenance_date=last_maintenance_date, next_maintenance_date=next_maintenance_date, device_behaviour=device_behaviour)
        
        self._speed: float = speed
        self._lane_position : int = lane_position
        self._edge_id : str = edge_id
        self._lane_id : str = lane_id
        self._sensed_devices = {}


        self.add_service(ServiceRegistry.services[Service.Object_Position_Service])
        self.add_service(ServiceRegistry.services[Service.Object_Sensing_Service])
        
        # if self._behaviour == DeviceBehaviour.MALICIOUS:
        self._alternated_device_data = copy.deepcopy(self) 
        
        
    def update(self,smart_phone_object):
        
        self._services[Service.Object_Position_Service]._function[Function.GET_OBJECT_POSITION](self,smart_phone_object)
        self._services[Service.Object_Sensing_Service]._function[Function.GET_SENSED_OBJECTS](self,smart_phone_object)
        
        
    def to_dict(self):
        
        device_dict = super().to_dict()
        smart_phone = {
            'record_type': DeviceRecordType.STATUS.name,
            'speed': self._speed,
            'edge_id': self._edge_id,
            'lane_id': self._lane_id,
            'lane_position': self._lane_position,
        }
        device_dict['record_type'] = DeviceRecordType.STATUS.name

        device_dict.update(smart_phone)

        return device_dict
        
    
class Smart_Phone_Manager:
    
    def __init__(self, device_handler) -> None:
        self._smart_phones : Dict[str,SmartPhone]= {}
        self._devices = device_handler
        
        trustworthy_smartphone_profiles, untrustworthy_smartphone_profiles = generate_profiles('smartphone', 20, 20)
        
        self.trustworthy_smartphone_profiles = trustworthy_smartphone_profiles
        self.untrustworthy_smartphone_profiles = untrustworthy_smartphone_profiles
        
        self.profile_counter = 0
                
    def subscribe(self):

        for departed_person in simulation.getDepartedPersonIDList():
            person.subscribe(departed_person, sc.SMART_PHONE_FEATURES)
            
        for veh_id in simulation.getDepartedIDList():
            if veh_id.startswith("bike"):
                vehicle.subscribe(veh_id, sc.VEHICLE_FEATURES)
                
    def update(self):
        current_bicyclist_in_simulation = self.update_smart_phone_availability()
        
        for smart_phone_id, smart_phone in current_bicyclist_in_simulation.items():    
            if smart_phone_id not in self._smart_phones:                
                self.create_smart_phone(smart_phone_id, smart_phone)   
                # print(f'Device created: {smart_phone_id} with device mapping id: {self._smart_phones[smart_phone_id]._device_map_id}')     
            self._smart_phones[smart_phone_id].update(smart_phone)
            
    def create_smart_phone(self, smart_phone_id, smart_phone):
        speed = smart_phone[tc.VAR_SPEED]
        position = smart_phone[tc.VAR_POSITION]
        edge_id = smart_phone[tc.VAR_ROAD_ID]
        lane_id = smart_phone[tc.VAR_LANE_ID]
        lane_position = smart_phone[tc.VAR_LANEPOSITION]
        
        device_behaviour = get_device_behaviour(self._devices)
        
        if device_behaviour == DeviceBehaviour.TRUSTWORTHY:            
            profile = random.choice(self.trustworthy_smartphone_profiles)
        elif device_behaviour == DeviceBehaviour.MALICIOUS:
            profile = random.choice(self.untrustworthy_smartphone_profiles)
            self.profile_counter = (self.profile_counter + 1) % len(self.untrustworthy_smartphone_profiles)
    
        self._smart_phones[smart_phone_id] = SmartPhone(
            smart_phone_id, 
            position, 
            speed, 
            lane_position, 
            edge_id, 
            lane_id,
            manufacturer=profile['manufacturer'],
            model=profile['model'],
            firmware_version=profile['firmware_version'],
            hardware_version=profile['hardware_version'],
            serial_number=profile['serial_number'],  # You can add serial_number in your profiles
            date_of_manufacture=profile['manufacture_date'],  # You can add manufacture_date in your profiles
            last_maintenance_date=profile['last_maintenance_date'],  # You can add this in your profiles
            next_maintenance_date=profile['next_maintenance_date'],  
            device_behaviour=device_behaviour
        )


    def update_smart_phone_availability(self):
        
        pedestrians = person.getAllSubscriptionResults()
        bicyclists = { veh_id : bicycle for veh_id, bicycle in vehicle.getAllSubscriptionResults().items() if bicycle[tc.VAR_VEHICLECLASS] == 'bicycle'}
        
        current_bicyclist_in_simulation = {**pedestrians, **bicyclists}
        current_bicyclist_ids = list(self._smart_phones.keys())

        non_existing_bicyclist_ids = [bicyclist_id for bicyclist_id in current_bicyclist_ids if bicyclist_id not in current_bicyclist_in_simulation.keys()]
        
        for non_existing_bicyclist_id in non_existing_bicyclist_ids:
            del self._smart_phones[non_existing_bicyclist_id]
        return current_bicyclist_in_simulation


    def all(self):
        return self._smart_phones


    def log(self):
        
        for index, smart_phone_object in self._smart_phones.items():
 
            try:                                   
                object_message = smart_phone_object.to_dict()
                
                logger.info(ObjectType.SMART_PHONE, object_message,logger.LoggingBehaviour.STATUS)
            except TypeError as e:
                print(e)
            except Exception as e:
                print(e)
                logger.error(e)
        return