from __future__ import annotations
from copy import copy
# from typing import TYPE_CHECKING
import json
from typing import TYPE_CHECKING, Tuple, Union

from typing import List, Dict, Tuple

from data_alterantion_model.common import AlterationType, SignificanceLevel
from data_models.iot_devices.common import DeviceBehaviour, DeviceComputationCapabilityClass, DeviceInternalStatus, DeviceShapeStatus



from trust_management.data_models.relationship.relationship_controller import RelationshipController
from trust_management.data_models.reputation.reputation_controller import ReputationController
from trust_management.data_models.transaction.transaction_controller import  TransactionController
from trust_management.data_models.trust_manager import TrustManager
from trust_management.settings import TrustManagementSettings
from data_models.iot_devices.common import DeviceType


if TYPE_CHECKING:
    from data_models.properties.properties import GenericProperty
    from data_models.services.service import GenericService
    from data_models.services.service import Service

    from data_models.iot_devices.smart_phone import SmartPhone
    from data_models.iot_devices.vehicle import Vehicle
    from data_models.report_management.report.report import SendingPacket


from data.simulation.scenario_constants import Constants as sc

class GenericDevice:

    def __init__(self, device_id: str, position: List[float], device_type: DeviceType = None, color: List[Tuple] = None, manufacturer: str = None, model: str = None, firmware_version: str = None, hardware_version: str = None, serial_number: str = None, date_of_manufacture: str = None, last_maintenance_date: str = None, next_maintenance_date: str = None, device_behaviour : DeviceBehaviour = DeviceBehaviour.TRUSTWORTHY):
        
        self._id : str = device_id
        
        if device_type != None:
            self._device_map_id : int = copy(sc.DEVICE_ID)
            sc.DEVICE_ID += 1
         
        self._affiliations : List[str] = []
        self._type : DeviceType = device_type
        if position == None:
            self._position : Tuple[float, float] = None
        elif position != None:
            self._position : Tuple[float, float] = (position[0], position[1])
            
            
        self._color : List[Tuple] = color                                       # Identification Features
        self._speed : float = 0.0
        self._internal_status : DeviceInternalStatus = DeviceInternalStatus.ACTIVE
        self._shape_status : DeviceShapeStatus = DeviceShapeStatus.ORIGINAL_MANUFACTURED
        self._manufacturer : str = manufacturer
        self._model : str = model
        self._firmware_version : str = firmware_version
        self._hardware_version : str = hardware_version
        self._serial_number : str = serial_number
        self._date_of_manufacture : str = date_of_manufacture
        self._last_maintenance_date : str = last_maintenance_date
        self._next_maintenance_date : str = next_maintenance_date
        self._behaviour : DeviceBehaviour = device_behaviour
        self._alteration_type = None
        self._significance_level = None
        self._alternated_device_data : Union[Vehicle,SmartPhone] = None
        self._computation_capability_class : DeviceComputationCapabilityClass = self.define_compute_capability_class()
        
        if DeviceBehaviour.TRUSTWORTHY == device_behaviour:
            self._alteration_type = None
            self._significance_level = None
        elif DeviceBehaviour.MALICIOUS == device_behaviour:
            self._alteration_type = AlterationType.DYNAMIC
            self._significance_level = SignificanceLevel.SIGNIFICANT
        
        self._static_values = {}
        
        self._properties : Dict[str, GenericProperty] = {}
        self._services : Dict[Service, GenericService] = {}
        
        
        
        transaction_controller : TransactionController = TransactionController()
        relationship_controller : RelationshipController = RelationshipController()
        reputation_controller : ReputationController = ReputationController(transaction_controller, TrustManagementSettings.REPUTATION_CONTEXT ,TrustManagementSettings.REPUTATION_SCOPE, TrustManagementSettings.REPUTATION_COMPUTATION_STRATEGY)
        
        self.trust_manager : TrustManager = TrustManager(relationship_controller, transaction_controller, reputation_controller)
        
        
        

    def update_request_status(self, request : SendingPacket):
        self.trust_manager.update_request_status(request)
        
    
    def update_status(self, status : DeviceInternalStatus):
        self._internal_status = status
    
    def get_status(self) -> DeviceInternalStatus:  
        return self._internal_status

    def add_service(self, service: GenericService):
        self._services[service.service_type] = service
    
    def define_compute_capability_class(self):
    
        device_type = self._type
        
        
        if device_type == DeviceType.INDUCTION_LOOP or device_type == DeviceType.TRAFFIC_LIGHT:
            return DeviceComputationCapabilityClass.LOW
        
        if device_type == DeviceType.SMART_PHONE or device_type == DeviceType.TRAFFIC_CAMERA:
            return DeviceComputationCapabilityClass.MEDIUM
        
        if device_type == DeviceType.VEHICLE or device_type == DeviceType.EMERGENCY_CENTER:
            return DeviceComputationCapabilityClass.HIGH
        
        return DeviceComputationCapabilityClass.UNDEFINED    
    
    def to_dict(self):
        
        try:
        
            device_dict = {
                'device_id': self._id,
                'affiliations': self._affiliations,
                'type': self._type.name if self._type else None,
                'position': self._position,
                'color': self._color,
                'speed': self._speed,
                'status': self._internal_status.name if self._internal_status else None,
                'shape_status': self._shape_status.name if self._shape_status else None, 
                'manufacturer': self._manufacturer,
                'model': self._model,
                # 'firmware_version': self._firmware_version,
                # 'hardware_version': self._hardware_version,
                # 'serial_number': self._serial_number,
                # 'date_of_manufacture': self._date_of_manufacture,
                # 'last_maintenance_date': self._last_maintenance_date,
                # 'next_maintenance_date': self._next_maintenance_date,
                # 'properties': [property_name for property_name in self._properties.keys()],
                # 'services': [service.name for service in self._services.keys()],
                'trustworthy_devices': self.trust_manager.relationship_controller.relationship_manager.get_trustworthy_devices(),
                'untrustworthy_devices': self.trust_manager.relationship_controller.relationship_manager.get_untrustworthy_devices(),
                'num_untrustworthy_relationships': self.trust_manager.relationship_controller.relationship_manager.get_num_untrustworthy_relationships(),
                'num_trustworthy_relationships': self.trust_manager.relationship_controller.relationship_manager.get_num_trustworthy_relationships(),
                'num_related_devices': self.trust_manager.relationship_controller.relationship_manager.get_num_relationships(),
                'num_trust_transactions' : self.trust_manager.trust_transaction_controller.transaction_manager.get_num_transactions(),
                # 'num_trustor_transactions' : self.trust_manager.trust_transaction_controller.transaction_manager.get_num_transactions(),
                # 'num_trustee_transactions' : self.trust_manager.trust_transaction_controller.transaction_manager.get_num_trustee_transactions(self._id),
                'computation_capability' : self._computation_capability_class.name,
                'device_behaviour' : self._behaviour.name,
            }
            
            json_device_dict = json.dumps(device_dict)
            
            return device_dict
            
        except Exception as e:
            print(e)
    


       