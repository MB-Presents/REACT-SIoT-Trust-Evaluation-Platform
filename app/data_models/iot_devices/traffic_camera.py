from __future__ import annotations

import random
import string
from typing import Dict, List, Tuple, TYPE_CHECKING

import itertools
import traci

from datetime import datetime, timedelta

import data.simulation.device_descriptions as config
from data.simulation.device_descriptions import ColorCode

from data_models.iot_devices.common import DeviceRecordType, DeviceType, Function, Service
from data_models.iot_devices.genric_iot_device import GenericDevice
from data_models.properties.properties import GenericProperty
from data_models.services.service import ServiceRegistry

from data_models.simulation.logging import ObjectType



import utils.logging as logger

if TYPE_CHECKING:
    from data_models.iot_devices.vehicle import Vehicle

class TrafficCamera(GenericDevice):

    def __init__(self, observedStreets:List[str], position:List[float], color:List[Tuple], camera_id: str, manufacturer: str, model: str, firmware_version: str, hardware_version: str, serial_number: str, date_of_manufacture: str, last_maintenance_date: str, next_maintenance_date: str):
        
        super().__init__(device_id=camera_id, position=position, device_type=DeviceType.TRAFFIC_CAMERA, color=color, manufacturer=manufacturer, model=model, firmware_version=firmware_version, hardware_version=hardware_version, serial_number=serial_number, date_of_manufacture=date_of_manufacture, last_maintenance_date=last_maintenance_date, next_maintenance_date=next_maintenance_date)
        
        self.x : float = position[0]
        self.y : float = position[1]

        self._captured_vehicles : Dict[str,Vehicle]= {}
        self._observed_streets = observedStreets
        self._device_description = ['license_plate', 'color', 'position','type','dimension','speed','signals','shape','lanePosition']


        self._properties['captured_vehicles'] = GenericProperty('captured vehicles', [])
        self._properties['observedStreets'] = GenericProperty('observed streets', observedStreets)
        
        
        self.add_service(ServiceRegistry.services[Service.Vehicle_Detection_Service])
        
        

        traci.poi.add(camera_id,self.x,self.y,self._color,poiType=self._type,width=50000,height=50000)
        
    
    def to_dict(self):
        # self._properties['captured_vehicles'].value = list(self._captured_vehicles.keys())
        
        device_dict = super().to_dict()
        device_dict['record_type'] = DeviceRecordType.STATUS.name
        
        
        return device_dict
    
    def sensed_objects_to_dict(self, captured_vehicle_id : str, captured_vehicle: Vehicle):
        
        
        # device_dict = super().to_dict()
        # device_dict = super().to_dict()
        
        device_dict = {}
        device_dict['sensor_id'] = self._id
        device_dict['record_type'] = DeviceRecordType.SENSED.name
        sensed_vehicle_dict = captured_vehicle.to_dict()
        device_dict.update(sensed_vehicle_dict)
        
        return device_dict
        
        
class Traffic_Camera_Manager:
    
    id_iter: int = itertools.count()
    
    def __init__(self, device_handler ) -> None:
        
        self._traffic_cameras : Dict[str,TrafficCamera] = {}
        self._devices = device_handler
        
        

        for camera_conf in config.traffic_cameras:
            camera_id = str(next(Traffic_Camera_Manager.id_iter)) + '_traffic_camera'

            # Generate random values for static fields
            manufacturer = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            model = ''.join(random.choice(string.ascii_letters) for _ in range(8))
            firmware_version = 'v' + '.'.join(str(random.randint(1, 9)) for _ in range(3))
            hardware_version = 'HW' + ''.join(str(random.randint(0, 9)) for _ in range(3))
            serial_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

            time = datetime.now()
            
            date_of_manufacture = (time - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d')
            last_maintenance_date = (time - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')
            next_maintenance_date = (time + timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')

            camera = TrafficCamera(observedStreets=camera_conf['edgeID'],
                                   position=camera_conf['position'],
                                   color=ColorCode.TRAFFIC_CAMERA.value,
                                   camera_id=camera_id,
                                   manufacturer=manufacturer,
                                   model=model,
                                   firmware_version=firmware_version,
                                   hardware_version=hardware_version,
                                   serial_number=serial_number,
                                   date_of_manufacture=date_of_manufacture,
                                   last_maintenance_date=last_maintenance_date,
                                   next_maintenance_date=next_maintenance_date)

            self._traffic_cameras[camera_id] = camera
            print(f'Device created: {camera_id} with device mapping id: {self._traffic_cameras[camera_id]._device_map_id}')  
        
            
            
    def update(self):        
        for traffic_camera_id, traffic_camera in self._traffic_cameras.items():
            traffic_camera._services[Service.Vehicle_Detection_Service]._function[Function.GET_DETECTED_VEHICLES](traffic_camera)


    def all(self) -> Dict[str,TrafficCamera]:
        return self._traffic_cameras

    
    def get_status(self, traffic_camera_id : str) -> TrafficCamera:
        return self._traffic_cameras[traffic_camera_id]


    def log(self):
        
        
        for traffic_camera_id, traffic_camera in self._traffic_cameras.items():
            
            try:
                message = traffic_camera.to_dict()
                logger.info(ObjectType.TRAFFIC_CAMERA, message, logger.LoggingBehaviour.STATUS)
                
                for captured_vehicle_id, captured_vehicle in traffic_camera._captured_vehicles.items():
                    message = traffic_camera.sensed_objects_to_dict(captured_vehicle_id, captured_vehicle)
                    logger.info(ObjectType.TRAFFIC_CAMERA, message, logger.LoggingBehaviour.SENSING)
                
                

            except Exception as e:
                print(e)
                logger.error(ObjectType.TRAFFIC_CAMERA,e.__dict__)
    