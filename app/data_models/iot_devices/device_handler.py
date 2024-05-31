from __future__ import annotations
from typing import Any, Dict, Union, TYPE_CHECKING



from data_models.iot_devices.smart_phone import Smart_Phone_Manager
from data_models.iot_devices.traffic_camera import Traffic_Camera_Manager
from data_models.iot_devices.traffic_light import TrafficLightManager
from data_models.iot_devices.vehicle import Vehicle_Manager
from scenario.emergency_response.emergency_response import EmergencyResponseCenter
from data_models.iot_devices.induction_loop import Induction_Loop_Manager



if TYPE_CHECKING:
    from data_models.iot_devices.genric_iot_device import DeviceType
    

class Devices_Group_Handler:
    
    def __init__(self) -> None:
        self._device_group : Dict[DeviceType,Union[Traffic_Camera_Manager, Vehicle_Manager, Induction_Loop_Manager, Smart_Phone_Manager, EmergencyResponseCenter,TrafficLightManager]] = {}
    
    def add(self, device_type: DeviceType, device_group: Traffic_Camera_Manager | Smart_Phone_Manager | Vehicle_Manager | Induction_Loop_Manager | TrafficLightManager | TrafficLightManager):
        self._device_group[device_type] = device_group
        
    def remove(self,device_type: DeviceType):
        del self._device_group[device_type]
        
    def get_status(self):
        for device in self._device_group.items():
            return device.get_status()
        
    def get(self, device_type: DeviceType) -> Union[Traffic_Camera_Manager, Vehicle_Manager, Induction_Loop_Manager, Smart_Phone_Manager, EmergencyResponseCenter,TrafficLightManager]:
       return self._device_group[device_type]
    
    def get_all_groups(self):
        return self._device_group.keys()
    
    def check_key_exists(self, key: str) -> bool:
        for device_manager in self._device_group.values():
        
            if isinstance(device_manager, Traffic_Camera_Manager):
                if key in device_manager._traffic_cameras.keys():
                    return True
            
            elif isinstance(device_manager, Vehicle_Manager):
                if key in device_manager.vehicles.keys():
                    return True
            
            elif isinstance(device_manager, Smart_Phone_Manager):
                if key in device_manager._smart_phones.keys():
                    return True
        
            elif isinstance(device_manager, Induction_Loop_Manager):
                if key in device_manager._induction_loops.keys():
                    return True
            
            elif isinstance(device_manager, EmergencyResponseCenter):
                if key == device_manager._id:
                    return True
            elif isinstance(device_manager, TrafficLightManager):
                if key in device_manager.traffic_lights.keys():
                    return True
        
        return False
    
    def get_device_by_key(self, key: str) -> Any:
        for device_manager in self._device_group.values():
            
            if isinstance(device_manager, Traffic_Camera_Manager):
                if key in device_manager._traffic_cameras:
                    return device_manager._traffic_cameras[key]
                
            elif isinstance(device_manager, Vehicle_Manager):
                if key in device_manager.vehicles:
                    return device_manager.vehicles[key]
                
            elif isinstance(device_manager, Smart_Phone_Manager):
                if key in device_manager._smart_phones:
                    return device_manager._smart_phones[key]
            
            elif isinstance(device_manager, Induction_Loop_Manager):
                if key in device_manager._induction_loops:
                    return device_manager._induction_loops[key]
                
            elif isinstance(device_manager, EmergencyResponseCenter):
                if key in device_manager:
                    return device_manager[key]
            
            elif isinstance(device_manager, TrafficLightManager):
                if key in device_manager.traffic_lights:
                    return device_manager.traffic_lights[key]
            
        return None
    
    
    
    def get_devices(self) -> Dict[str,Any]:
        
        devices = {}
        
        for device_manager in self._device_group.values():
            
            if isinstance(device_manager, Traffic_Camera_Manager):
                for key, value in device_manager.all().items():
                    devices[key] = value

            elif isinstance(device_manager, Vehicle_Manager):
                for key, value in device_manager.all().items():
                    devices[key] = value
                
            elif isinstance(device_manager, Smart_Phone_Manager):
                for key, value in device_manager.all().items():
                    devices[key] = value
                
            elif isinstance(device_manager, Induction_Loop_Manager):
                for key, value in device_manager.all().items():
                    devices[key] = value
                
            elif isinstance(device_manager, EmergencyResponseCenter):
                devices[device_manager._id] = device_manager
                    
            elif isinstance(device_manager, TrafficLightManager):
                for key, value in device_manager.all().items():
                    devices[key] = value
                

                    
        return devices
    
    
def get_devices_group_handler() -> Devices_Group_Handler:
    return device_group_handler

device_group_handler : Devices_Group_Handler = Devices_Group_Handler()