from __future__ import annotations
from typing import TYPE_CHECKING, Dict







from typing import List, Union
from traci import constants as tc
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters
from core.models.devices import device_handler
from core.models.devices.common import DeviceShapeStatus, DeviceType

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.devices.vehicle import Vehicle
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.induction_loop import InductionLoop



class SensedDeviceRecord:
    
    
    
    def __init__(self, 
                 service_provider : Union[InductionLoop, Vehicle, TrafficCamera,SmartPhone ],
                 observed_device : Union[InductionLoop, Vehicle, TrafficCamera,SmartPhone]) -> None:
        
        devices : device_handler.DevicesGroupHandler  = device_handler.get_device_handler().get_devices_group_handler() 
        vehicles : Dict[str,Vehicle] = devices.get_devices_by_group(DeviceType.VEHICLE)
        smart_phones : Dict[str,SmartPhone] = devices.get_devices_by_group(DeviceType.SMART_PHONE)
        traffic_cameras : Dict[str,TrafficCamera] = devices.get_devices_by_group(DeviceType.TRAFFIC_CAMERA)
        induction_loops : Dict[str,InductionLoop] = devices.get_devices_by_group(DeviceType.INDUCTION_LOOP)

        self.service_provider_id = service_provider._id
        self.service_provider_location = service_provider._position
        self.service_provider_speed = service_provider._speed
        
        self.time : int = ScenarioParameters.TIME
        self.sensed_device_id = observed_device._id
        self.sensed_device_type : DeviceType = None
        
        self.sensed_vehicle_type : str = 'Unknown'
        self.sensed_device_functional_status : DeviceShapeStatus = None
        self.sensed_device_signal : List[float] = None
        self.sensed_device_speed : float = None
        self.sensed_device_position : List[float] = None    
        self.sensed_device_lane: str = 'Unknown'
        self.service_provider : Union[InductionLoop, Vehicle, TrafficCamera,SmartPhone ] = service_provider
        
        # if isinstance(observed_device, Vehicle):
        if observed_device._id in vehicles.keys():
            self.normalize_vehicle_object(observed_device)
            
        # if isinstance(observed_device, TrafficCamera):
        elif observed_device._id in traffic_cameras.keys():
            self.normalize_traffic_camera(observed_device)
            
        # if isinstance(observed_device, InductionLoop):
        elif observed_device._id in induction_loops.keys():
            self.normalize_induction_loop_object(observed_device)
        
        elif observed_device._id == "No Device":
            self.normalize_no_dummy_device(observed_device)
        
    
    def normalize_no_dummy_device(self, observed_device : GenericDevice):
            
        self.sensed_device_type = observed_device._type
        self.sensed_vehicle_type = None
        self.sensed_device_functional_status = observed_device._shape_status
            
        self.sensed_device_signal = None
        self.sensed_device_speed = observed_device._speed
        self.sensed_device_position = observed_device._position
        
        self.sensed_device_lane = None
        self.sensed_device_lane_position = None
        self.sensed_device_width = None
        self.sensed_device_height = None
        self.sensed_device_length = None
        self.sensed_device_edge_id = None
        
        
    def normalize_vehicle_object(self, vehicle : Vehicle):
        
        self.sensed_device_type = vehicle._type
        self.sensed_vehicle_type = vehicle._vehicle_type
        self.sensed_device_functional_status = vehicle._shape_status
            
        self.sensed_device_signal = vehicle._signal
        self.sensed_device_speed = vehicle._speed
        self.sensed_device_position = vehicle._position
        
        self.sensed_device_lane = vehicle._lane_id
        self.sensed_device_lane_position = vehicle._lane_position
        self.sensed_device_width = vehicle._width
        self.sensed_device_height = vehicle._height
        self.sensed_device_length = vehicle._length
        self.sensed_device_edge_id = vehicle._edge_id
    
    
    def normalize_traffic_camera(self, captured_vehicle : Vehicle):
                
        self.sensed_device_type = captured_vehicle._type
        self.sensed_vehicle_type = captured_vehicle._vehicle_type
        self.sensed_device_functional_status = captured_vehicle._color
                    
        self.sensed_device_signal = captured_vehicle._signal
        self.sensed_device_speed = captured_vehicle._speed
        self.sensed_device_position = captured_vehicle._position
                
        self.sensed_device_lane = captured_vehicle._lane_id
        self.sensed_device_lane_position = captured_vehicle._lane_position
        self.sensed_device_width = captured_vehicle._width
        self.sensed_device_height = captured_vehicle._height
        self.sensed_device_length = captured_vehicle._length
        self.sensed_device_edge_id = captured_vehicle._edge_id
    
    def normalize_induction_loop_object(self, detected_vehicle : Vehicle):
        
        self.sensed_device_type = detected_vehicle._type
        self.sensed_device_height = detected_vehicle._height
        self.sensed_device_length = detected_vehicle._length
        self.sensed_device_width = detected_vehicle._width
        
        self.sensed_device_lane = detected_vehicle._lane_id
        self.sensed_device_position = detected_vehicle._position
        self.sensed_device_lane_position = detected_vehicle._lane_position
        self.sensed_vehicle_type = detected_vehicle._vehicle_type
        self.sensed_device_speed = detected_vehicle._speed
        