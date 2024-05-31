from typing import Callable, Dict

from data_models.functions.functionalities import get_detected_vehicles, get_inductive_object_count, get_position, get_surrounding_objects, get_vehicle_status_update
from data_models.iot_devices.common import Function, Service




class GenericService:
    def __init__(self, service: Service, function: Dict[str, Callable]):
        self.service_type : Service = service
        self.name = service.name
        self.version = '1.0.0'
        self._function : Dict[str, Callable] = function
        
        
    def add_function(self, name: Function, function: Callable):
        self._function[name] = function
        

class ServiceRegistry:
    services : Dict[Service, GenericService]= {}

    @classmethod
    def register_service(cls, service: GenericService):
        cls.services[service.service_type] = service
        
    @classmethod
    def add_service(cls, service: GenericService):
        cls.services[service.service_type] = service



inductive_vehicle_detection_service : GenericService = GenericService(Service.Inductive_Vehicle_Detection_Service, {Function.GET_INDUCTIVE_OBJECT_COUNT: get_inductive_object_count})
vehicle_detection_service : GenericService = GenericService(Service.Vehicle_Detection_Service, {Function.GET_DETECTED_VEHICLES: get_detected_vehicles})
vehicle_service : GenericService = GenericService(Service.Vehicle_Status_Service, {Function.GET_STATUS: get_vehicle_status_update})

object_sensing_service : GenericService = GenericService(Service.Object_Sensing_Service, {Function.GET_SENSED_OBJECTS: get_surrounding_objects})
object_position_service : GenericService = GenericService(Service.Object_Position_Service, {Function.GET_OBJECT_POSITION: get_position})






ServiceRegistry.register_service(inductive_vehicle_detection_service)
ServiceRegistry.register_service(vehicle_detection_service)
ServiceRegistry.register_service(object_sensing_service)


# Smart Phone
ServiceRegistry.register_service(object_position_service)
ServiceRegistry.register_service(vehicle_service)

# service2 = GenericService("service2", function2)
# service3 = GenericService("service3", function3)