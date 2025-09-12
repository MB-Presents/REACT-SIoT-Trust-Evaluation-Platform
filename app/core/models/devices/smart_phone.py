from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
import copy

import random
# from turtle import position


from traci import vehicle, person
from traci import constants as tc
from core.simulation.logging import ObjectType
from typing import Dict, List
from core.data_alteration.profiles.device_profile_generator import generate_device_profiles
from core.data_alteration.behaviour.device_behaviour_determinator import determine_device_behavior
from core.models.devices.common import DeviceRecordType, DeviceType


from core.models.devices.genric_iot_device import GenericDevice


from core.simulation.simulation_context import SimulationContext
import utils.logging as logger

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import DeviceBehaviour
#     from core.models.devices.device_handler import DevicesGroupHandler



class SmartPhone(GenericDevice):

    def __init__(self,
                 smart_phone_id: str,
                 position: Tuple[float,float],
                 speed: float,
                 lane_position: float,
                 edge_id: str,
                 lane_id: str,
                 device_behaviour : DeviceBehaviour,
                 simulation_context: Optional[SimulationContext]= None) -> None:

        super().__init__(
            device_id=smart_phone_id,
            device_type=DeviceType.SMART_PHONE,
            device_behaviour=device_behaviour,
            simulation_context=simulation_context
        )
        
        self.with_position(position=position)

        self._speed: float = speed
        self._lane_position : float = lane_position
        self._edge_id : str = edge_id
        self._lane_id : str = lane_id
        self._sensed_devices = {}


        # self.add_service(BaseService.services[Service.Object_Position_Service])
        # self.add_service(BaseService.services[Service.Object_Sensing_Service])
        
        # if self._behaviour == DeviceBehaviour.MALICIOUS:
        self._alternated_device_data = copy.deepcopy(self) 

        
    # def update(self, smart_phone_object):
    #     """Update using service layer instead of direct service calls"""
    #     try:
    #         self.execute_device_function(Function.GET_OBJECT_POSITION, smart_phone_object=smart_phone_object)
    #         self.execute_device_function(Function.GET_SENSED_OBJECTS, smart_phone_object=smart_phone_object)
    #     except Exception as e:
    #         print(f"Error updating smart phone {self._id}: {e}")
    
    def to_dict(self)-> Dict[str, Any]:
        
        device_dict = super().to_dict()
        
        assert device_dict is not None, "super().to_dict() returned None"
        assert isinstance(device_dict, dict), "to_dict() must return a dictionary"
        
        smart_phone = {
            'record_type': DeviceRecordType.STATUS.name,
            'speed': self._speed,
            'edge_id': self._edge_id,
            'lane_id': self._lane_id,
            'lane_position': self._lane_position,
        }
        # device_dict['record_type'] = DeviceRecordType.STATUS.name

        device_dict.update(smart_phone)

        return device_dict
        
    
class Smart_Phone_Manager:
    
    def __init__(self, device_handler) -> None:
        self._smart_phones : Dict[str,SmartPhone]= {}
        # Store as interface instead of concrete type
 
        trustworthy_smartphone_profiles, untrustworthy_smartphone_profiles = generate_device_profiles('smartphone', 20, 20)
        
        self.trustworthy_smartphone_profiles = trustworthy_smartphone_profiles
        self.untrustworthy_smartphone_profiles = untrustworthy_smartphone_profiles
        
        self.profile_counter = 0
                
    # def subscribe(self):

    #     for departed_person in simulation.getDepartedPersonIDList():
    #         person.subscribe(departed_person, ScenarioDeviceConfiguration.SMART_PHONE_FEATURES)
            
    #     for veh_id in simulation.getDepartedIDList():
    #         if veh_id.startswith("bike"):
    #             vehicle.subscribe(veh_id, ScenarioDeviceConfiguration.VEHICLE_FEATURES)
                
    # def update(self):
    #     current_bicyclist_in_simulation = self.update_smart_phone_availability()
        
    #     for smart_phone_id, smart_phone in current_bicyclist_in_simulation.items():    
    #         if smart_phone_id not in self._smart_phones:                
    #             self.create_smart_phone(smart_phone_id, smart_phone)   
    #             # print(f'Device created: {smart_phone_id} with device mapping id: {self._smart_phones[smart_phone_id]._device_map_id}')     
    #         self._smart_phones[smart_phone_id].update(smart_phone)
            
    # def create_smart_phone(self, smart_phone_id, smart_phone):
    #     speed = smart_phone[tc.VAR_SPEED]
    #     position = smart_phone[tc.VAR_POSITION]
    #     edge_id = smart_phone[tc.VAR_ROAD_ID]
    #     lane_id = smart_phone[tc.VAR_LANE_ID]
    #     lane_position = smart_phone[tc.VAR_LANEPOSITION]
        
    #     device_behaviour = determine_device_behavior(self._devices)
        
    #     if device_behaviour == DeviceBehaviour.TRUSTWORTHY:            
    #         profile = random.choice(self.trustworthy_smartphone_profiles)
    #     elif device_behaviour == DeviceBehaviour.MALICIOUS:
    #         profile = random.choice(self.untrustworthy_smartphone_profiles)
    #         self.profile_counter = (self.profile_counter + 1) % len(self.untrustworthy_smartphone_profiles)
    
    #     self._smart_phones[smart_phone_id] = SmartPhone(
    #         smart_phone_id, 
    #         position, 
    #         speed, 
    #         lane_position, 
    #         edge_id, 
    #         lane_id,
    #         manufacturer=profile['manufacturer'],
    #         model=profile['model'],
    #         firmware_version=profile['firmware_version'],
    #         hardware_version=profile['hardware_version'],
    #         serial_number=profile['serial_number'],
    #         date_of_manufacture=profile['manufacture_date'],
    #         last_maintenance_date=profile['last_maintenance_date'],
    #         next_maintenance_date=profile['next_maintenance_date'],
    #         device_behaviour=device_behaviour
    #     )


    def update_smart_phone_availability(self):
        
        pedestrians = person.getAllSubscriptionResults()
        bicyclists = { veh_id : bicycle for veh_id, bicycle in vehicle.getAllSubscriptionResults().items() if bicycle[tc.VAR_VEHICLECLASS] == 'bicycle'}
        
        current_bicyclist_in_simulation = {**pedestrians, **bicyclists}
        current_bicyclist_ids = list(self._smart_phones.keys())

        non_existing_bicyclist_ids = [bicyclist_id for bicyclist_id in current_bicyclist_ids if bicyclist_id not in current_bicyclist_in_simulation.keys()]
        
        for non_existing_bicyclist_id in non_existing_bicyclist_ids:
            del self._smart_phones[non_existing_bicyclist_id]
        return current_bicyclist_in_simulation


    # def all(self):
    #     return self._smart_phones


    # def log(self):
        
    #     for index, smart_phone_object in self._smart_phones.items():
 
    #         try:                                   
    #             object_message = smart_phone_object.to_dict()
                
    #             logger.info(ObjectType.SMART_PHONE, object_message,logger.LoggingBehaviour.STATUS)
    #         except TypeError as e:
    #             print(e)
    #         except Exception as e:
    #             print(e)
    #             logger.error(e)
    #     return