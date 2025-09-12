from __future__ import annotations
import itertools
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import random



from abc import ABC, abstractmethod
from typing import Dict, Union



from core.data_alteration.behaviour.device_behaviour_determinator import determine_device_behavior
from core.data_alteration.profiles.device_profile_generator import generate_device_profiles
from core.models.devices.induction_loop import InductionLoop
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.traffic_camera import TrafficCamera
from core.models.devices.traffic_light import TrafficLightSystem
from core.models.devices.vehicle import Vehicle
from core.simulation.simulation_context import SimulationContext
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings


import traci



from core.models.devices.common import DeviceBehaviour, DeviceType


from traci import constants as tc


from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
from scenarios.canberra_case_study.core.devices import INDUCTION_SENSOR_SPECIFICATION, TRAFFIC_CAMERA_SPECIFICATION

if TYPE_CHECKING:
    from core.models.devices.vehicle import Vehicle
    from core.models.devices.device_handler import DevicesGroupHandler
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter

class IDeviceCreator(ABC):
    
    @abstractmethod
    def create(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Union[SmartPhone, TrafficCamera, TrafficLightSystem, InductionLoop, Vehicle, EmergencyResponseCenter]:
        pass
    
    @abstractmethod
    def create_group(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Dict[str,Union[TrafficCamera, TrafficLightSystem, InductionLoop, EmergencyResponseCenter, EmergencyVehicle, Vehicle, SmartPhone]]:
        pass
    
    

    


    
    
class DeviceCreationFactory:
    
    def __init__(self, context : SimulationContext) -> None:
        
        self.context = context
        
        self._creators : Dict[DeviceType, IDeviceCreator] = {}        
        self._creators[DeviceType.SMART_PHONE] = SmartPhoneFactory()
        self._creators[DeviceType.TRAFFIC_CAMERA] = TrafficCameraFactory()
        self._creators[DeviceType.TRAFFIC_LIGHT] = TrafficLightFactory()
        self._creators[DeviceType.INDUCTION_LOOP] = InductionLoopFactory()
        self._creators[DeviceType.VEHICLE] = VehicleFactory()
        self._creators[DeviceType.EMERGENCY_VEHICLE] = EmergencyVehicleFactory()
        self._creators[DeviceType.EMERGENCY_CENTER] = EmergencyResponseCenterFactory()
    
    
    def get_device_creator(self, device_type: DeviceType) -> IDeviceCreator:
        creator = self._creators.get(device_type)
        if not creator:
            raise ValueError(f"Device creator for type {device_type} not found.")
        return creator
    
    
    def create_group(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Dict[str,Union[TrafficCamera, TrafficLightSystem, InductionLoop, EmergencyResponseCenter, EmergencyVehicle, Vehicle, SmartPhone]]:
        
        creator = self._creators.get(device_type)
        if not creator:
            raise ValueError(f"Device creator for type {device_type} not found.")
        
        device_group =  creator.create_group(device_type=device_type, config=config, _id=_id)
        assert isinstance(device_group, dict), f"Device group for {device_type} is not a dictionary."
        # assert len(device_group) > 0 or device_type == DeviceType.SMART_PHONE, f"Device group for {device_type} is empty."

        return device_group
        
    def create(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Union[SmartPhone, TrafficCamera, TrafficLightSystem, InductionLoop, Vehicle, EmergencyResponseCenter, EmergencyVehicle]:
        creator = self._creators.get(device_type)
        if not creator:
            raise ValueError(f"Device creator for type {device_type} not found.")
        
        return creator.create(device_type=device_type, config=config, _id=_id)


class EmergencyResponseCenterFactory(IDeviceCreator):

    _id_counter = itertools.count(0)

    def create(self, device_type: DeviceType = DeviceType.EMERGENCY_CENTER, config : Dict[Any,Any]={}, _id : str ="") -> EmergencyResponseCenter:
        
        config = {"device_id": "Emergency Response",
              "manufacturer": 'Motorola Solutions',
              "model": 'Motorola Center 1',
              "firmware_version": '1.0.0',
              "hardware_version": '1.0.0',
              "serial_number": '123456789',
              "date_of_manufacture": '2020-01-01',
              "last_maintenance_date": '2020-01-01',
              "next_maintenance_date": '2020-01-01',
              "color": (0, 0, 0)
        }

        assert all(isinstance(key, str) and isinstance(value, str) or isinstance(value, tuple)for key, value in config.items()), "All keys and values in config must be strings."
        


        return EmergencyResponseCenter(device_id=config['device_id'],
                                       device_type=DeviceType.EMERGENCY_CENTER,
                                       color=config['color'],
                                       config=config)

    def create_group(self, device_type = None, config = {}, _id = ""):
        return self.create()
        

class TrafficCameraFactory(IDeviceCreator):
    
    _id_counter = itertools.count(0)
    
    def create(self, device_type: DeviceType = DeviceType.TRAFFIC_CAMERA, config : Dict[Any,Any]={}, _id : str ="") -> TrafficCamera:
 
        camera_conf = config

        # # Generate random values for static fields
        # manufacturer = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        # model = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        # firmware_version = 'v' + '.'.join(str(random.randint(1, 9)) for _ in range(3))
        # hardware_version = 'HW' + ''.join(str(random.randint(0, 9)) for _ in range(3))
        # serial_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

        # time = datetime.now()
        
        # date_of_manufacture = (time - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d')
        # last_maintenance_date = (time - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')
        # next_maintenance_date = (time + timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')

        traffic_camera_id = f"traffic_camera_{_id if _id else next(self._id_counter)}"

        camera = TrafficCamera(                                    
                               camera_id=traffic_camera_id,
                               observedStreets=camera_conf['edgeID'],
                               position=camera_conf['position'],
                               color=camera_conf['color'],
                                
                                # manufacturer=manufacturer,
                                # model=model,
                                # firmware_version=firmware_version,
                                # hardware_version=hardware_version,
                                # serial_number=serial_number,
                                # date_of_manufacture=date_of_manufacture,
                                # last_maintenance_date=last_maintenance_date,
                                # next_maintenance_date=next_maintenance_date
                                )

        return camera
            
            

    def create_group(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str =""):
        _traffic_cameras : Dict[str,TrafficCamera] = {}
        
        for camera_conf in TRAFFIC_CAMERA_SPECIFICATION:

            # id_count = itertools.count()
            traffic_camera = self.create(config=camera_conf)
            _traffic_cameras[traffic_camera._id] = traffic_camera
            
        return _traffic_cameras
            

class InductionLoopFactory(IDeviceCreator):
    
    _id_counter = itertools.count(0)
    
    def create(self, device_type: DeviceType = DeviceType.INDUCTION_LOOP, config : Dict[Any,Any]={}, _id : str ="") -> InductionLoop:

        induction_conf = config
        induction_loop_id = f"induction_loop_{_id if _id else next(self._id_counter)}"
        induction = InductionLoop(
            induction_loop_id=induction_loop_id,
            observedStreet=induction_conf['edgeID'],
            position=induction_conf['position'],
            color=induction_conf['color'], 
            profile_config=induction_conf)
        
        return induction
    
    
    def create_group(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Dict[str,InductionLoop]:
        _induction_loops: Dict[str, InductionLoop] = {}
        
        for induction_conf in INDUCTION_SENSOR_SPECIFICATION:
            induction_loop = self.create(config=induction_conf)
            _induction_loops[induction_loop._id] = induction_loop

        return _induction_loops


class SmartPhoneFactory(IDeviceCreator):

    _id_counter = itertools.count(0)

    def __init__(self):
        trustworthy_smartphone_profiles, untrustworthy_smartphone_profiles = generate_device_profiles('smartphone', 20, 20)
        
        self.trustworthy_smartphone_profiles = trustworthy_smartphone_profiles
        self.untrustworthy_smartphone_profiles = untrustworthy_smartphone_profiles
        
        self.profile_counter = 0



    def create(self, device_type: DeviceType, config : Dict[int,Any]={}, _id : str =""):
        smart_phone = config
        speed = smart_phone[tc.VAR_SPEED]
        position = smart_phone[tc.VAR_POSITION]
        edge_id = smart_phone[tc.VAR_ROAD_ID]
        lane_id = smart_phone[tc.VAR_LANE_ID]
        lane_position = smart_phone[tc.VAR_LANEPOSITION]
        
        device_behaviour = determine_device_behavior()
        
        # if device_behaviour == DeviceBehaviour.TRUSTWORTHY:            
        #     profile = random.choice(self.trustworthy_smartphone_profiles)
        # elif device_behaviour == DeviceBehaviour.MALICIOUS:
        #     profile = random.choice(self.untrustworthy_smartphone_profiles)
        #     self.profile_counter = (self.profile_counter + 1) % len(self.untrustworthy_smartphone_profiles)

        smart_phone_id = str(_id) if _id else f"smart_phone_{next(self._id_counter)}"
        smart_phone = SmartPhone(
            smart_phone_id=smart_phone_id,
            position=position, 
            speed=speed, 
            lane_position=lane_position, 
            edge_id=edge_id, 
            lane_id=lane_id,
            device_behaviour=device_behaviour
        )
        
        return smart_phone
    
    
    
    def create_group(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Dict[str,Optional[SmartPhone]]:
        return {}
    
    
class VehicleFactory(IDeviceCreator):
    
    def __init__(self) -> None:
        self.vehicles: Dict[str, Vehicle] = {}
        
        trustworthy_vehicle_profiles, untrustworthy_vehicle_profiles = generate_device_profiles('vehicle', 20, 20)
        
        self.trustworthy_vehicle_profiles = trustworthy_vehicle_profiles
        self.untrustworthy_vehicle_profiles = untrustworthy_vehicle_profiles
        self.profile_counter = 0
        
    
    def create(self, device_type: DeviceType, config : Dict[int,Any], _id : str ="") -> Vehicle:
        veh_object= config
        speed : float =  veh_object[tc.VAR_SPEED]
        position : List[float] = veh_object[tc.VAR_POSITION]
        edge_id : str = veh_object[tc.VAR_ROAD_ID]
        lane_id : str = veh_object[tc.VAR_LANE_ID]
        lane_position : float = veh_object[tc.VAR_LANEPOSITION]
        lane_index : int = veh_object[tc.VAR_LANE_INDEX]
                
        color : List[float] = veh_object[tc.VAR_COLOR]
                
        signal : int = veh_object[tc.VAR_SIGNALS]
                
        type : str = veh_object[tc.VAR_TYPE]
        length : float  = veh_object[tc.VAR_LENGTH]
        width : float = veh_object[tc.VAR_WIDTH]
        height : float = veh_object[tc.VAR_HEIGHT]
        vehicle_class : str = veh_object[tc.VAR_VEHICLECLASS]
                    
        # veh_id = veh_object[tc.ID_COUNT]
        device_behaviour = DeviceBehaviour.TRUSTWORTHY
        
        veh_id : str = veh_object[tc.ID_COUNT]
        
        if not veh_id.startswith("emergency_veh"):
            device_behaviour = determine_device_behavior()
        
        
        if device_behaviour == DeviceBehaviour.TRUSTWORTHY:
            profile = random.choice(self.trustworthy_vehicle_profiles)
        elif device_behaviour == DeviceBehaviour.MALICIOUS:
            profile = random.choice(self.untrustworthy_vehicle_profiles)
        
        
        vehicle = Vehicle(
            veh_id=veh_id,
            speed=speed,
            position=position,
            signal=signal,
            edge_id=edge_id,
            lane_id=lane_id,
            color=color,
            lane_position=lane_position,
            vehicle_type=type,
            width=width,
            height=height,
            length=length,
            lane_index=lane_index,
            vehicle_class=vehicle_class,
            device_behaviour=device_behaviour  
        )
                                        
        return vehicle
        

    def create_group(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Dict[str, Optional[Vehicle]]:
        return {}


class TrafficLightFactory(IDeviceCreator):
    
    
    def __init__(self):
        super().__init__()
        
        trustworthy_traffic_light_profile, _ = generate_device_profiles('traffic_lights', 4, 0)
        self.trustworthy_traffic_light_profile = trustworthy_traffic_light_profile

            
    def create_group(self, device_type: DeviceType = DeviceType.TRAFFIC_LIGHT, config : Dict[Any,Any]={}, _id : str ="") -> Dict[str, TrafficLightSystem]:

        traffic_lights: Dict[str, TrafficLightSystem] = {}
        for traffic_light_id in traci.trafficlight.getIDList():
            traffic_lights[traffic_light_id] = self.create(device_type=device_type, _id=traffic_light_id)  
            
        return traffic_lights

    
    def create(self, device_type: DeviceType = DeviceType.TRAFFIC_LIGHT, config : Dict[Any,Any]={}, _id : str ="") -> TrafficLightSystem:
        
        position = traci.junction.getPosition(_id)
        profile = random.choice(self.trustworthy_traffic_light_profile)
        
        return TrafficLightSystem(traffic_light_id=_id,
                                position=position,
                                profile=profile)

    
class EmergencyVehicleFactory(IDeviceCreator):
    
    EMERGENCY_BLUE_LIGHT = 0b100000000000
    

    def create(self, device_type: DeviceType = DeviceType.EMERGENCY_VEHICLE, config : Dict[Any,Any]={}, _id : str ="") -> EmergencyVehicle:
        emergeemergency_vehicle_configuration = config
        vehicle = EmergencyVehicle(emergency_id=_id,
                                   emergency_vehicle_configuration=config
                                   )
        traci.vehicle.setParameter(_id,"has.rerouting.device","true")
        traci.vehicle.setSignals(_id, self.EMERGENCY_BLUE_LIGHT)
        
        return vehicle
        
    def create_group(self, device_type: DeviceType, config : Dict[Any,Any]={}, _id : str ="") -> Dict[str,EmergencyVehicle]:
        
        emergency_vehicles = {}
        for emergency_id, emergency_vehicle_configuration in AccidentSettings.EMERGENCY_VEHS.items():
            emergency_vehicles[emergency_id] = self.create(config=emergency_vehicle_configuration, _id=emergency_id)
        
        return emergency_vehicles
            
