from __future__ import annotations
from typing import Any, Dict, Generic, Union, TYPE_CHECKING


from core.models.devices.factories.device_factory import DeviceFactory
from core.models.devices.factories.logging_strategy import LoggingManager
from core.models.devices.factories.subscriptionStrategy import SubscriptionManager
from core.models.devices.factories.update_manager import UpdateManager
from core.models.services import vehicle
from core.simulation.adapter.subscription_adapter import SubscriptionAdapter

from core.simulation.event_bus.base_event import DeviceCreatedEvent, TimeStepEvent
from core.simulation.simulation_context import SimulationContext
from core.utils.debug.typing import TSmartDevices
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
import utils.logging as logger
from core.models.devices.genric_iot_device import DeviceType

if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.vehicle import Vehicle
    from core.models.devices.induction_loop import InductionLoop
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter

class DevicesGroupHandler:


    def __init__(self, context : SimulationContext) -> None:
        self._device_group: Dict[DeviceType, Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem, EmergencyVehicle]]] = {}
        self._devices: Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem, EmergencyVehicle]] = {}
        self.context : SimulationContext = context
        self._device_factory = DeviceFactory(simulation_context=context)
        
        self._subscription_manager = SubscriptionManager(traci_adapter=SubscriptionAdapter())
        self._logging_manager = LoggingManager()
        self._update_manager = UpdateManager()
        
        
        self.context.register_device_registry(registry=self)
        
        
        context.get_event_bus().subscribe(TimeStepEvent, self._handle_time_step)

        
        
    
    def add_group(self, device_type: DeviceType) -> None:
        """Add a group of devices for the given device type."""
        assert self._device_factory is not None, "Device factory is not initialized."
        assert device_type not in self._device_group, f"Device group for {device_type} already exists."
        
        devices = self._device_factory.create_device_group(device_type)
        
        assert devices is not None, f"Device group for {device_type} returned None from factory."
        assert device_type not in self._device_group, f"Device group for {device_type} already exists."
        
        
        
        
        self._device_group[device_type] = devices
        
        self._devices.update(devices)
    
    
    def _handle_time_step(self, event: TimeStepEvent) -> None:
        """Handle time step updates for all devices"""
        # for device_id, device in self._devices.items():
        #     if hasattr(device, '_services'):
        #         for service in device._services.values():
        #             if hasattr(service, '_handle_time_step'):
        #                 service._handle_time_step(event)
        
        # TODO: Handler Update events of the services
    

    
    def subscribe(self, device_type: DeviceType) -> None:
        """Subscribe to updates for the given device type."""
        assert device_type in self._device_group, f"Device group for {device_type} not found."
        self._subscription_manager.subscribe(device_type=device_type)
        
    def add_device(self, key: str, device: Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]) -> None:
        """Add a single device to the group and global devices dictionary."""
        assert key not in self._devices, f"Device with key '{key}' already exists."
        assert hasattr(device, '_type'), f"Device must have a '_type' attribute."
        assert isinstance(device._type, DeviceType), f"Device '_type' must be a DeviceType, got {type(device._type)}."
        
        if device._type not in self._device_group:
            self._device_group[device._type] = {}
        self._devices[key] = device
        self._device_group[device._type][key] = device

    def create_device(self, device_type: DeviceType, config: dict, _id: str) -> Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]:
        """Create a new device of the given type."""
        device =  self._device_factory.create(device_type=device_type, config=config, _id=_id)
        self._devices[_id] = device
        self._device_group[device_type][_id] = device
        return device
        
    def remove_group(self, device_type: DeviceType) -> None:
        """Remove a device group by device type."""
        assert device_type in self._device_group, f"Device group for {device_type} not found."
        # Remove devices from the global _devices dictionary
        for key in self._device_group[device_type]:
            self._devices.pop(key, None)
        del self._device_group[device_type]
        
    def get_status(self) -> Dict[DeviceType, Any]:
        """Get the status of all device groups."""
        status = {}
        for device_type, devices in self._device_group.items():
            assert devices is not None, f"Device group for {device_type} is None."
            status[device_type] = {key: device.get_status() for key, device in devices.items()}
        return status

    def get_devices_by_group(self, device_type: DeviceType) -> Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, EmergencyVehicle, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]]:
        """Get all devices for a specific device type."""
        assert device_type in self._device_group, f"Device group for {device_type} not found."
        devices = self._device_group[device_type]
        assert devices is not None, f"Device group for {device_type} is None."
        return devices
    
    def get_all_groups(self) -> list[DeviceType]:
        """Get all device group types."""
        return list(self._device_group.keys())
    
    def get_device(self, key: str) -> Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, EmergencyVehicle, TrafficLightSystem]:
        """Get a device by its key."""
        assert isinstance(key, str), f"Device key must be a string, got {type(key)}."
        return self._devices[key]

    def get_devices(self) -> Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, EmergencyVehicle, TrafficLightSystem]]:
        """Get all devices across all groups."""
        return self._devices
    
    def update_by_group(self, device_type: DeviceType) -> None:
        """Update devices for the given device type."""
        assert device_type in self._device_group, f"Device group for {device_type} not found."
        self._update_manager.update(device_type)

    def update_device(self, key: str, device: TSmartDevices) -> None:
        """Update a device by its key."""
        assert key in self._devices, f"Device with key '{key}' not found."
        self._devices[key] = device

    def log_by_group(self, device_type: DeviceType) -> None:
        """Log the status of devices for the given device type."""
        assert device_type in self._device_group, f"Device group for {device_type} not found."
        selected_device_group = self._device_group[device_type]
        assert selected_device_group is not None, f"Device group for {device_type} is None."
        assert all(device._type == device_type for device in selected_device_group.values()), f"Not all devices are of type {device_type}"
        
        self._logging_manager.log(device_type, selected_device_group)
    
    
    
        
        

# from __future__ import annotations
# from typing import Any, Dict, Union, TYPE_CHECKING

# from git import Optional




# from core.models.devices.configuration.device_factory import DeviceCreationFactory
# from core.models.devices.configuration.logging_strategy import LoggingManager
# from core.models.devices.configuration.subscriptionStrategy import SubscriptionManager
# from core.models.devices.configuration.update_manager import UpdateManager
# from core.utils.traci_adapter import TraCIAdapter
# import utils.logging as logger
# from core.models.devices.genric_iot_device import DeviceType

# if TYPE_CHECKING:
#     from core.models.devices.genric_iot_device import GenericDevice
#     from core.models.devices.smart_phone import SmartPhone
#     from core.models.devices.traffic_camera import TrafficCamera
#     from core.models.devices.traffic_light import TrafficLightSystem
#     from core.models.devices.vehicle import Vehicle

#     from core.models.devices.induction_loop import InductionLoop
#     from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    

# class DevicesGroupHandler:
#     _instance = None
#     _initialized = False
    
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(DevicesGroupHandler, cls).__new__(cls)
#         return cls._instance
    
#     def __init__(self) -> None:
#         if not self._initialized:
#             self._device_group : Dict[DeviceType, Optional[Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]]]] = {}
#             self._devices : Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]] = {}
#             self._device_factory = DeviceCreationFactory()
#             self._subscription_manager = SubscriptionManager(traci_adapter=TraCIAdapter())
#             self._logging_manager = LoggingManager()
#             self._update_manager = UpdateManager()

#             self._initialized = True
    
#     def add_group(self, device_type: DeviceType) -> None:
        
#         # device_group = self._device_factory.create_group(device_type)
#         assert device_type in self._device_group.keys(), f"Device group for {device_type} not found."
#         assert self._device_group[device_type] is not None, f"Device group for {device_type} is empty."
        
#         devices = self._device_factory.create_group(device_type)
        
#         assert devices is not None, f"Device group for {device_type} is empty."
#         assert len(devices) > 0, f"Device group for {device_type} is empty."
        

#         self._device_group[device_type] = devices
#         self._devices.update(self._device_group[device_type])
        
    
#     def subscribe(self, device_type: DeviceType) -> None:
#         self._subscription_manager.subscribe(device_type=device_type)
        

#     def add_device(self, key: str, device: Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]) -> None:
#         self._devices[key] = device
#         self._device_group[device._type][key] = device

#     def remove_group(self,device_type: DeviceType):
#         del self._device_group[device_type]
        
        
#     def get_status(self):
#         for device_type, device in self._device_group.items():
#             return device.get_status()

#     def get_devices_by_group(self, device_type: DeviceType) -> Dict[str,Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]]:
#         return self._device_group[device_type]
    
#     def get_all_groups(self):
#         return self._device_group.keys()
    
#     def get_device(self, key: str) -> Optional[Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, TrafficLightSystem]]:
#         assert 
#         return self._devices[key] if key in self._devices else None
    
    
#     def get_devices(self) -> Dict[str,Any]:
#         return self._devices

    
#     def update_by_group(self, device_type: DeviceType):
#         self._update_manager.update(device_type)
#         # self._device_group[device_type]._services.update()
    
#     def log_by_group(self, device_type : DeviceType):
#         self._logging_manager.log(device_type, self._device_group[device_type].values())
        



#             # for device_id, device in self._device_group[device_type].items():
            
#             #     try:
#             #         message = device.to_dict()
#             #         logger.info(device_type.value, message, logger.LoggingBehaviour.STATUS)
                    
#             #         for captured_vehicle_id, captured_vehicle in device._captured_vehicles.items():
#             #             message = device.sensed_objects_to_dict(captured_vehicle_id, captured_vehicle)
#             #             logger.info(device_type.value, message, logger.LoggingBehaviour.SENSING)
                    
                    

#             #     except Exception as e:
#             #         print(e)
#             #         logger.error(device_type.value,e.__dict__)
        
            
#             # try:
#             #     message = traffic_camera.to_dict()
#             #     logger.info(ObjectType.TRAFFIC_CAMERA, message, logger.LoggingBehaviour.STATUS)
                
#             #     for captured_vehicle_id, captured_vehicle in traffic_camera._captured_vehicles.items():
#             #         message = traffic_camera.sensed_objects_to_dict(captured_vehicle_id, captured_vehicle)
#             #         logger.info(ObjectType.TRAFFIC_CAMERA, message, logger.LoggingBehaviour.SENSING)
                
                

#             # except Exception as e:
#             #     print(e)
#             #     logger.error(ObjectType.TRAFFIC_CAMERA,e.__dict__)
        
        
        