
from __future__ import annotations
import copy
import random
from typing import Dict, List, TYPE_CHECKING

from enum import Enum, auto
import traci
from traci import constants as tc
from data.simulation.scenario_constants import Constants as sc
import traci
from data_alterantion_model.generate_device_profiles import generate_profiles
from data_alterantion_model.intial_device_behaviour import get_device_behaviour
from data_models.events.simulation_events import EventState, EventType, SimulationEvent, SimulationEventManager
from data_models.iot_devices.common import DeviceBehaviour, DeviceRecordType, DeviceType, Function, Service
from data_models.iot_devices.genric_iot_device import GenericDevice
from data_models.report_management.report.report_models import AuthenticityRole, ReportType
from data_models.report_management.report.reporter import SendersEntity


from data_models.services.service import ServiceRegistry
from data_models.simulation.logging import ObjectType

import utils.logging as logger

if TYPE_CHECKING:
    from data_models.iot_devices.traffic_light import TrafficLightManager, TrafficLightSystem
    from data_models.report_management.report_manager import ReportManager

class VehicleState(Enum):
    START_STOP = auto()
    END_STOP = auto()
    CREATED = auto()
    START_TRIP = auto()
    ARRIVED = auto()
    STOPPED = auto()
    DRIVING = auto()
    COLLIDING = auto()


class Vehicle(GenericDevice):
    
    def __init__(self, veh_id : str, speed : float, position : List[float], signal , edge_id : str, lane_id : str, color : List[float], lane_position : float, vehicle_type : str, width : float, height : float, length : float, lane_index : int, vehicle_class : str, manufacturer: str, model: str, firmware_version: str, hardware_version: str, serial_number: str, date_of_manufacture: str, last_maintenance_date: str, next_maintenance_date: str, device_behaviour : DeviceBehaviour) -> None:
        
        super().__init__(device_id=veh_id, position=position, device_type=DeviceType.VEHICLE, color=color, manufacturer=manufacturer, model=model, firmware_version=firmware_version, hardware_version=hardware_version, serial_number=serial_number, date_of_manufacture=date_of_manufacture, last_maintenance_date=last_maintenance_date, next_maintenance_date=next_maintenance_date, device_behaviour=device_behaviour)
        
        self._speed = speed
        self._signal = signal
        self._edge_id = edge_id
        self._lane_id = lane_id
        self._lane_position = lane_position
        self._vehicle_type = vehicle_type
        self._width = width
        self._height = height
        self._length = length
        self._lane_index = lane_index
        self._vehicle_class = vehicle_class
        self._sensed_devices = {}
        
        # if self._behaviour == DeviceBehaviour.MALICIOUS:
        self._alternated_device_data = copy.deepcopy(self) 
        
        traci.vehicle.setParameter(veh_id,"has.rerouting.device","true")
          
                  
        self.add_service(ServiceRegistry.services[Service.Vehicle_Status_Service])
        self.add_service(ServiceRegistry.services[Service.Object_Sensing_Service])
            
    def update(self,vehicle : dict):
        
        self._services[Service.Vehicle_Status_Service]._function[Function.GET_STATUS](self, vehicle)
        self._services[Service.Object_Sensing_Service]._function[Function.GET_SENSED_OBJECTS](self, vehicle)
        
        
    def request_traffic_lights_on_route(self, traffic_lights_manager : TrafficLightManager, report_manager : ReportManager, vehicles_simulation, simulation_event_manager : SimulationEventManager, authenticity=True):
        
        traffic_lights = traci.vehicle.getNextTLS(self._id)
        
        for traffic_light in traffic_lights:
            traffic_light_id = traffic_light[0]
            
            traffic_light: TrafficLightSystem = traffic_lights_manager.traffic_lights[traffic_light_id]
            
            if self._id not in traffic_light._requesting_vehicles and not report_manager.exists(self._id, traffic_light._id):        
                
                traffic_request_event : SimulationEvent = simulation_event_manager.create_event(reporter_id=self._id,
                                                      vehicle=vehicles_simulation[self._id],
                                                      event_type=EventType.TRAFFIC_LIGHT_PRIORITY_REQUEST,
                                                      authenticity=authenticity,
                                                      event_state=EventState.TRIGGERED)
                
                simulation_event_manager.add(traffic_request_event)
            
                vehicle: Vehicle = vehicles_simulation[self._id]
                authenticity_role = AuthenticityRole.AUTHENTIC if authenticity else AuthenticityRole.UNAUTHENTIC
                
                requestor : Dict[str,SendersEntity]= {}
                requestor[vehicle._id] = SendersEntity(vehicle,authenticity_role,sc.TIME)
                
                
                
                report = report_manager.create_report(requestor ,traffic_request_event, vehicle, traffic_light, ReportType.TraffiCPriorityRequest)
                report_manager.add(report)
                
                traffic_light.request_priority(self._id)    
    
    def to_dict(self):
        
        device_dict = super().to_dict()
        vehicle_dict = {
            'speed': self._speed,
            'signal': self._signal,
            'edge_id': self._edge_id,
            'lane_id': self._lane_id,
            'lane_position': self._lane_position,
            'vehicle_type': self._vehicle_type,
            'width': self._width,
            'height': self._height,
            'length': self._length,
            'lane_index': self._lane_index,
            'vehicle_class': self._vehicle_class,
        }

        device_dict['record_type'] = DeviceRecordType.STATUS.name
        device_dict.update(vehicle_dict)

        return device_dict
    

class Vehicle_Manager:
    
    def __init__(self,device_handler) -> None:
        self.vehicles: Dict[str, Vehicle] = {}
        self._devices = device_handler
        
        # Example usage
        trustworthy_vehicle_profiles, untrustworthy_vehicle_profiles = generate_profiles('vehicle', 20, 20)
        
        self.trustworthy_vehicle_profiles = trustworthy_vehicle_profiles
        self.untrustworthy_vehicle_profiles = untrustworthy_vehicle_profiles
        self.profile_counter = 0
    
    def subscribe(self):
        
        for veh_id in traci.simulation.getDepartedIDList():
            if veh_id.startswith("ped") or veh_id.startswith("bike"):
                continue
            
            traci.vehicle.subscribe(veh_id, sc.VEHICLE_FEATURES)
            
            
            
    def update(self) -> Dict[str,Vehicle]:
        
        vehicle_in_simulation : dict = traci.vehicle.getAllSubscriptionResults()
        vehicle_in_simulation = self.remove_non_present_vehicles(vehicle_in_simulation)

        for veh_id, vehicle in vehicle_in_simulation.items():            
            if veh_id not in self.vehicles.keys():
                self.create_vehicle(veh_id, vehicle)
                # print(f'Device created: {veh_id} with device mapping id: {self.vehicles[veh_id]._device_map_id}')  
            
            self.vehicles[veh_id].update(vehicle)
            
        return self.vehicles

    def create_vehicle(self, veh_id, veh_object):
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
                    
        device_behaviour = DeviceBehaviour.TRUSTWORTHY
        
        if not veh_id.startswith("emergency_veh"):
            device_behaviour = get_device_behaviour(self._devices)
        
        
        if device_behaviour == DeviceBehaviour.TRUSTWORTHY:
            profile = random.choice(self.trustworthy_vehicle_profiles)
        elif device_behaviour == DeviceBehaviour.MALICIOUS:
            profile = random.choice(self.untrustworthy_vehicle_profiles)
        
        
        self.vehicles[veh_id] = Vehicle(
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
            manufacturer=profile['manufacturer'],
            model=profile['model'],
            firmware_version=profile['firmware_version'],
            hardware_version=profile['hardware_version'],
            serial_number=profile['serial_number'],
            date_of_manufacture=profile['manufacture_date'],
            last_maintenance_date=profile['last_maintenance_date'],
            next_maintenance_date=profile['next_maintenance_date'],
            device_behaviour=device_behaviour  
        )
                                        
        return speed,position,edge_id,lane_id,lane_position,lane_index,color,signal,type,length,width,height,vehicle_class


    def remove_non_present_vehicles(self, vehicle_in_simulation):
        vehicle_ids_in_simulation = list(vehicle_in_simulation.keys())

        current_vehicle_ids = list(self.vehicles.keys())

        
        nonexistent_vehicle_ids = [veh_id for veh_id in current_vehicle_ids if veh_id not in vehicle_ids_in_simulation or self.vehicles[veh_id]._vehicle_type in ['bike_bicycle','ped_pedestrian']]
        
        for veh_id in nonexistent_vehicle_ids:
            del self.vehicles[veh_id]
            
            
        vehicle_in_simulation = {veh_id: vehicle for veh_id, vehicle in vehicle_in_simulation.items() if vehicle[tc.VAR_VEHICLECLASS] not in ['bicycle','ped_pedestrian']}  
        
        return vehicle_in_simulation    
    
    def get_status(self):
        return self.vehicles.__dict__
    
    def all(self) -> Dict[str,Vehicle]:
        return self.vehicles
    

    def log(self):
        
        for veh_id, vehicle in self.vehicles.items():
    
            try:
                
                message = vehicle.to_dict()
                
                logger.info(ObjectType.VEHICLE, message, logger.LoggingBehaviour.STATUS)      
            
            except Exception as e:
                str(e)


    def get_vehicle(self,index : str) -> Vehicle:
        
        if index not in self.vehicles.keys():
            return None
        
    
        return self.vehicles[index]

