

from abc import abstractmethod
from typing import Any, Callable, Dict
from core.models.devices.common import Function, Service
from core.models.devices.genric_iot_device import GenericDevice
from core.models.interfaces.service import IService
from core.simulation.event_bus.base_event import DeviceStateChangedEvent, TimeStepEvent
from core.simulation.simulation_context import SimulationContext


class BaseService(IService):
    """Base service class with context injection"""
    
    def __init__(self, simulation_context: SimulationContext, device: GenericDevice):
        self.simulation_context = simulation_context
        self.device = device
        self.logger = None  # Replace with your LoggingUtil()
        
        # Subscribe to relevant events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to events - override in subclasses"""
        self.simulation_context.get_event_bus().subscribe(TimeStepEvent, self._handle_time_step)
        self.simulation_context.get_event_bus().subscribe(DeviceStateChangedEvent, self._handle_device_state_change)
    
    def _handle_time_step(self, event: TimeStepEvent):
        """Handle time step events"""
        self.update(step=event.step, dt=event.dt)
    
    def _handle_device_state_change(self, event: DeviceStateChangedEvent):
        """Handle device state changes - override in subclasses"""
        pass
    
    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> None:
        pass
        



# inductive_vehicle_detection_service : GenericService = GenericService(Service.Inductive_Vehicle_Detection_Service, {Function.GET_INDUCTIVE_OBJECT_COUNT: get_inductive_object_count})
# vehicle_detection_service : GenericService = GenericService(Service.Vehicle_Detection_Service, {Function.GET_DETECTED_VEHICLES: get_detected_vehicles})
# vehicle_service : GenericService = GenericService(Service.Vehicle_Status_Service, {Function.GET_STATUS: get_vehicle_status_update})

# object_sensing_service : GenericService = GenericService(Service.Object_Sensing_Service, {Function.GET_SENSED_OBJECTS: get_surrounding_objects})
# object_position_service : GenericService = GenericService(Service.Object_Position_Service, {Function.GET_OBJECT_POSITION: get_position})






# ServiceRegistry.register_service(inductive_vehicle_detection_service)
# ServiceRegistry.register_service(vehicle_detection_service)
# ServiceRegistry.register_service(object_sensing_service)


# # Smart Phone
# ServiceRegistry.register_service(object_position_service)
# ServiceRegistry.register_service(vehicle_service)