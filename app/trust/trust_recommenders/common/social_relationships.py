

from __future__ import annotations
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice


class SocialRelationships:
    
    def __init__(self, value_co_location = 0.8, 
                 value_co_work = 0.8, 
                 value_object_owner_relationship = 0.9, 
                 value_social_object_relationship = 0.6, 
                 value_parental_object_relationship = 0.5, 
                 co_location_distance = 50.0, 
                 default_trust_value = 0) -> None:
        self.value_co_location : float = value_co_location
        self.value_co_work : float = value_co_work
        self.value_object_owner_relationship : float = value_object_owner_relationship
        self.value_social_object_relationship : float = value_social_object_relationship
        self.value_parental_object_relationship : float = value_parental_object_relationship
        
        self.co_location_distance : float = co_location_distance
        self.intial_trust_value : float = default_trust_value

    def get_social_relationship_value(self, trustor : GenericDevice, trustee : GenericDevice) -> float:
        
        
        initial_trust_value = self.intial_trust_value
        
        if self.objects_are_in_distance(trustor, trustee, self.co_location_distance):
            if initial_trust_value < self.value_co_location:
                initial_trust_value = self.value_co_location
            
        if self.devices_are_co_working_devices(trustor, trustee):
            if initial_trust_value < self.value_co_work:
                initial_trust_value = self.value_co_work
            
        if self.devices_are_social_devices(trustor, trustee):
            
            if initial_trust_value < self.value_social_object_relationship:
                initial_trust_value = self.value_social_object_relationship
            
        if self.devices_are_parental_devices(trustor, trustee):
            if initial_trust_value < self.value_parental_object_relationship:
                initial_trust_value = self.value_parental_object_relationship
                
        if self.devices_have_same_owner(trustor, trustee):
            if initial_trust_value < self.value_object_owner_relationship:
                initial_trust_value = self.value_object_owner_relationship
                
        return initial_trust_value

    def objects_are_in_distance(self, trustor : GenericDevice, trustee : GenericDevice, max_distance : float) -> bool:
        
        trustor_position = trustor._position
        trustee_position = trustee._position
        
        distance = math.sqrt((trustor_position[0] - trustee_position[0])**2 + (trustor_position[1] - trustee_position[1])**2)
        
        if distance <= max_distance:
            return True
        return False
        
    def devices_are_co_working_devices(self, trustor : GenericDevice, trustee : GenericDevice) -> bool:
        
        trustor_functionalities = list(trustor._properties.values())
        trustee_functionalities = list(trustee._properties.values())
        
        common_functionalities = set(trustor_functionalities).intersection(trustee_functionalities) 
        
        if len(common_functionalities) > 0:
            return True
        return False
        
        

    def devices_are_social_devices(self, trustor : GenericDevice, trustee : GenericDevice) -> bool:
        
        
        
        return False
        
        
    def devices_are_parental_devices(self, trustor : GenericDevice, trustee : GenericDevice) -> bool:
        
    
        return False

    def devices_have_same_owner(self, trustor : GenericDevice, trustee : GenericDevice) -> bool:
        
        trustor_affiliations = trustor._affiliations
        trustee_affiliations = trustee._affiliations
        
        common_affiliations = set(trustor_affiliations).intersection(trustee_affiliations)
        
        if len(common_affiliations) > 0:
            return True
        return False
        
    






