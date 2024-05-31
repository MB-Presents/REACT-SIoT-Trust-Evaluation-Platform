from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING



import itertools

import traci
from typing import Any, Dict, List, Tuple


import data.simulation.device_descriptions as config
from data_models.iot_devices.common import DeviceRecordType, DeviceType, Function, Service

from data_models.iot_devices.genric_iot_device import GenericDevice
from data_models.properties.properties import GenericProperty
from data_models.services.service import ServiceRegistry



from data_models.simulation.logging import ObjectType
import utils.logging as logger

class InductionLoop(GenericDevice):

    def __init__(self, induction_loop_id: str, observedStreet : str, position: List[float], color: List[Tuple], manufacturer: str, model: str, firmware_version: str, hardware_version: str, serial_number: str, date_of_manufacture: str, last_maintenance_date: str, next_maintenance_date: str):
   
        super().__init__(induction_loop_id,
                         position, 
                         DeviceType.INDUCTION_LOOP, 
                         color, 
                         manufacturer, 
                         model, 
                         firmware_version, 
                         hardware_version, 
                         serial_number, 
                         date_of_manufacture, 
                         last_maintenance_date, 
                         next_maintenance_date)
        
        self._observed_street : str = observedStreet
        self._captured_vehicles_features : Dict[str,Any] = {}
        
        traci.poi.add(self._id, self._position[0], self._position[1], self._color, poiType=self._type, width=50000, height=50000)
        
        self._properties['captured_vehicles'] = GenericProperty('captured vehicles', [])
        self._properties['observedStreet'] = GenericProperty('observed street', observedStreet)

        self.add_service(ServiceRegistry.services[Service.Inductive_Vehicle_Detection_Service])
    
    def to_dict(self):
        
        # self._properties['captured_vehicles'].value = list(self._captured_vehicles_features.keys())
        
        device_dict = super().to_dict()
        induction_loop_dict = {
            'observed_street': self._observed_street,
            'record_type' : DeviceRecordType.STATUS.name
        }
        
        
        device_dict.update(induction_loop_dict)
        
        
        return device_dict
        
    def sensed_objects_to_dict(self, captured_vehicle_id : str, captured_vehicle: dict):
        
        device_dict = {}
        device_dict['sensor_id'] = self._id
        device_dict['record_type'] = DeviceRecordType.SENSED.name
        device_dict.update(captured_vehicle)
        
        return device_dict

class Induction_Loop_Manager:
    
    id_iter: int = itertools.count()
    
    def __init__(self, device_handler) -> None:
        self._induction_loops: Dict[str, InductionLoop] = {}
        self._devices = device_handler
        
        for induction_conf in config.induction_sensors:
        
            induction_id: int =  str(next(Induction_Loop_Manager.id_iter)) + '_induction_loop'
            
                                       
            induction = InductionLoop(induction_loop_id=induction_id,
                                      observedStreet=induction_conf['edgeID'],
                                      position=induction_conf['position'],
                                      color=config.ColorCode.INDUCTION_LOOP.value, 
                                      manufacturer=induction_conf['manufacturer'], 
                                      model=induction_conf['model'], 
                                      firmware_version=induction_conf['firmware_version'], 
                                      hardware_version=induction_conf['hardware_version'], 
                                      serial_number=induction_conf['serial_number'], 
                                      date_of_manufacture=induction_conf['date_of_manufacture'], last_maintenance_date=induction_conf['last_maintenance_date'], next_maintenance_date=induction_conf['next_maintenance_date'])
            
            self._induction_loops[induction_id] = induction
            print(f'Device created: {induction_id} with device mapping id: {self._induction_loops[induction_id]._device_map_id}')  
            
        
    def update(self):
        for induction_id, induction_loop in self._induction_loops.items():            
            induction_loop._services[Service.Inductive_Vehicle_Detection_Service]._function[Function.GET_INDUCTIVE_OBJECT_COUNT](induction_loop)

    
    def get_status(self, induction_id: str) -> InductionLoop:
        return self._induction_loops[induction_id] 
    
    
    def all(self) -> Dict[str, InductionLoop]:
        return self._induction_loops
    
    

    def log(self):
    
        for index, induction_loop in self._induction_loops.items():    
            
            try:                    
                message = induction_loop.to_dict()
                
                
                
                
                logger.info(ObjectType.INDUCTION_LOOP, message, logger.LoggingBehaviour.STATUS)
                
                for captured_vehicle_id, captured_vehicle in induction_loop._captured_vehicles_features.items():
                    
                    message = induction_loop.sensed_objects_to_dict(captured_vehicle_id, captured_vehicle)
                    logger.info(ObjectType.INDUCTION_LOOP, message, logger.LoggingBehaviour.SENSING)
                
            except Exception as e:
                logger.get_logger()
                
                logger.error(ObjectType.INDUCTION_LOOP,e)