from __future__ import annotations

from turtle import pos
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import itertools
import traci



from core.models.devices.common import DeviceRecordType, DeviceType, Function, Service
from core.models.devices.genric_iot_device import GenericDevice
from core.models.properties.properties import GenericProperty




from core.simulation.simulation_context import SimulationContext
from scenarios.canberra_case_study.core.devices import TRAFFIC_CAMERA_SPECIFICATION

if TYPE_CHECKING:
    from core.models.devices.vehicle import Vehicle


class TrafficCamera(GenericDevice):

    def __init__(self, 
                 observedStreets:List[str],
                 position: Tuple[float,float],
                 color: Tuple[float,float,float],
                 camera_id: str,
                 simulation_context : Optional[SimulationContext]= None):
        
        super().__init__(
            device_id=camera_id,
            device_type=DeviceType.TRAFFIC_CAMERA,
            color=color,
            simulation_context=simulation_context
        )
        self.with_position(position=position)
        
        self._captured_vehicles : Dict[str,Vehicle]= {}
        self._observed_streets = observedStreets
        self._device_description = ['license_plate', 'color', 'position','type','dimension','speed','signals','shape','lanePosition']


        self._properties['captured_vehicles'] = GenericProperty('captured vehicles', [])
        self._properties['observedStreets'] = GenericProperty('observed streets', observedStreets)
        
        
        # self.add_service(ServiceRegistry.services[Service.Vehicle_Detection_Service])
        
        

        traci.poi.add(camera_id,self.x,self.y,self._color,poiType=self._type.name,width=50000,height=50000)
        
    
    def to_dict(self) -> Dict[str, Any]:
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
        
        
# class Traffic_Camera_Manager:
    
#     id_iter: int = itertools.count()
    
#     def __init__(self, device_handler ) -> None:
        
#         self._traffic_cameras : Dict[str,TrafficCamera] = {}
#         self._devices = device_handler
        
        

#         for camera_conf in TRAFFIC_CAMERA_SPECIFICATION:
#             camera_id = str(next(Traffic_Camera_Manager.id_iter)) + '_traffic_camera'

#             # # Generate random values for static fields
#             # manufacturer = ''.join(random.choice(string.ascii_letters) for _ in range(10))
#             # model = ''.join(random.choice(string.ascii_letters) for _ in range(8))
#             # firmware_version = 'v' + '.'.join(str(random.randint(1, 9)) for _ in range(3))
#             # hardware_version = 'HW' + ''.join(str(random.randint(0, 9)) for _ in range(3))
#             # serial_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

#             # time = datetime.now()
            
#             # date_of_manufacture = (time - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d')
#             # last_maintenance_date = (time - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')
#             # next_maintenance_date = (time + timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')

#             camera = TrafficCamera(observedStreets=camera_conf['edgeID'],
#                                    position=camera_conf['position'],
#                                    color=camera_conf['color'],
#                                    camera_id=camera_id,
#                                 #    manufacturer=manufacturer,
#                                 #    model=model,
#                                 #    firmware_version=firmware_version,
#                                 #    hardware_version=hardware_version,
#                                 #    serial_number=serial_number,
#                                 #    date_of_manufacture=date_of_manufacture,
#                                 #    last_maintenance_date=last_maintenance_date,
#                                 #    next_maintenance_date=next_maintenance_date,
#                                    devices=self._devices)

#             self._traffic_cameras[camera_id] = camera
#             print(f'Device created: {camera_id} with device mapping id: {self._traffic_cameras[camera_id]._device_map_id}')  
        
            
            
#     def update(self):        
#         for traffic_camera_id, traffic_camera in self._traffic_cameras.items():
#             traffic_camera._services[Service.Vehicle_Detection_Service]._function[Function.GET_DETECTED_VEHICLES](traffic_camera, self._devices)


#     # def all(self) -> Dict[str,TrafficCamera]:
#     #     return self._traffic_cameras

    
#     # def get_status(self, traffic_camera_id : str) -> TrafficCamera:
#     #     return self._traffic_cameras[traffic_camera_id]


    # def log(self):
        
        
    #     for traffic_camera_id, traffic_camera in self._traffic_cameras.items():
            
    #         try:
    #             message = traffic_camera.to_dict()
    #             logger.info(ObjectType.TRAFFIC_CAMERA, message, logger.LoggingBehaviour.STATUS)
                
    #             for captured_vehicle_id, captured_vehicle in traffic_camera._captured_vehicles.items():
    #                 message = traffic_camera.sensed_objects_to_dict(captured_vehicle_id, captured_vehicle)
    #                 logger.info(ObjectType.TRAFFIC_CAMERA, message, logger.LoggingBehaviour.SENSING)
                
                

    #         except Exception as e:
    #             print(e)
    #             logger.error(ObjectType.TRAFFIC_CAMERA,e.__dict__)
    