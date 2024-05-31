from __future__ import annotations
import itertools
from typing import TYPE_CHECKING, Tuple, Union

from typing import Dict, List
import numpy as np
import traci
from traci import exceptions
from traci import constants as tc
from traci import vehicle, person
from data_alterantion_model.data_alternation_model import get_alternated_data

from data_models.iot_devices.genric_iot_device import DeviceBehaviour
from data_models.iot_devices import device_handler
from data_models.iot_devices.common import DeviceType
from data_models.report_management.sensed_device_record import SensedDeviceRecord
from scenario.intelligent_traffic_light.constants import TrafficLightApplicationSettings

from data.simulation.scenario_constants import Constants as sc




if TYPE_CHECKING:
    from data_models.iot_devices.device_handler import Devices_Group_Handler
    from data_models.iot_devices.induction_loop import InductionLoop
    from data_models.iot_devices.traffic_camera import TrafficCamera
    from data_models.iot_devices.vehicle import Vehicle_Manager
    from data_models.iot_devices.vehicle import Vehicle
    from data_models.iot_devices.smart_phone import SmartPhone



def get_inductive_object_count(induction_loop : InductionLoop) -> Dict[str,dict]: 
    
    captured_vehicles = {}

    objects_on_edge = traci.edge.getLastStepVehicleIDs(induction_loop._observed_street)
    
    devices   = device_handler.get_devices_group_handler() 
    vehicles : Dict[str,Vehicle] = devices.get(DeviceType.VEHICLE).all()
    
    vehicles_on_edge = { veh_id: vehicles[veh_id] for veh_id in objects_on_edge if veh_id in vehicles.keys()}
    
    

    for veh_id, vehicle in vehicles_on_edge.items():
    
        vehicle = {}
        
        vehicle['device_id'] = veh_id
        vehicle['dimension'] = getVehicleDimensions(veh_id)
        vehicle['speed'] = vehicles[veh_id]._speed             
        vehicle['lanePosition'] = vehicles[veh_id]._lane_position
        vehicle['laneIndex'] = vehicles[veh_id]._lane_index
        vehicle['laneID'] = vehicles[veh_id]._lane_id
        vehicle['edgeID'] = vehicles[veh_id]._edge_id
        
        captured_vehicles[veh_id] = vehicle
    
    induction_loop._captured_vehicles_features = captured_vehicles
    
    return captured_vehicles

def get_detected_vehicles(sensing_device : TrafficCamera) -> Dict[str,Vehicle]:
    
    sensing_device._captured_vehicles = {}
    
    devices  = device_handler.get_devices_group_handler()    
    vehicles : Vehicle_Manager = devices.get(DeviceType.VEHICLE)
    
    for observed_edge in sensing_device._observed_streets:    
        for veh_id in traci.edge.getLastStepVehicleIDs(observed_edge):
                
            if veh_id.startswith("ped") or veh_id.startswith("bike"):
                continue
            
            vehicle : Vehicle = vehicles.get_vehicle(veh_id)            
            sensing_device._captured_vehicles[veh_id] = vehicle

def get_vehicle_status_update(self : Vehicle, veh_object : dict):
    
    self._speed : float =  veh_object[tc.VAR_SPEED]
    self._position : List[float] = veh_object[tc.VAR_POSITION]
    self._edge_id : str = veh_object[tc.VAR_ROAD_ID]
    self._lane_id : str = veh_object[tc.VAR_LANE_ID]
    self._lane_position : float = veh_object[tc.VAR_LANEPOSITION]
    self._lane_index : int = veh_object[tc.VAR_LANE_INDEX]
    
    self._color : List[float] = veh_object[tc.VAR_COLOR]
    self._signal : int = veh_object[tc.VAR_SIGNALS]

    if self._signal is None:
        self._signal = 0 



def get_surrounding_objects(self : Union[SmartPhone,Vehicle], mobile_device : dict):
    
    id: int = itertools.count()
    
    service_provider_table = {}
    
    devices : Devices_Group_Handler  = device_handler.get_devices_group_handler()
    vehicles = devices.get(DeviceType.VEHICLE).all()
    
    observed_surrounding_vehicles = get_surrounding_vehicles_of(self)




        
    for observed_vehicle_key, vehicle_object in observed_surrounding_vehicles.items():
        
        if observed_vehicle_key not in vehicles:
            continue
            
        if self._behaviour == DeviceBehaviour.TRUSTWORTHY: 
            sensed_device = vehicles[observed_vehicle_key]
            
        elif DeviceBehaviour.MALICIOUS == self._behaviour:
            sensed_device = get_alternated_data(vehicles[observed_vehicle_key])
            
        add_sensed_device(service_provider_table, id, self, sensed_device)
        
    self._sensed_devices = service_provider_table

def get_surrounding_vehicles_of(self : Union[SmartPhone,Vehicle]):
    
    devices : Devices_Group_Handler  = device_handler.get_devices_group_handler()
    vehicles = devices.get(DeviceType.VEHICLE).all()
    
    observed_surrounding_vehicles = {}
    
    vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
    if vehicle_positions.shape[0] == 0:
        observed_surrounding_vehicles = {}
    
    else:
        vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
        
        self_position = np.array(self._position)
        distances = np.linalg.norm(vehicle_positions - self_position, axis=1)
        distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
        observed_surrounding_vehicles = {veh_id: vehicles[veh_id] for veh_id, dist in zip(vehicles.keys(), distances) if dist <= distance_threshold}
    
    return observed_surrounding_vehicles
    
    # # if isinstance(self,Vehicle):

    # if self._id in vehicles.keys():
    #     # vehicle.subscribeContext(service_provider_key, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING, sc.VEHICLE_FEATURES)
    #     # observed_surrounding_vehicles : dict = vehicle.getContextSubscriptionResults(service_provider_key)
    #     # vehicle.unsubscribeContext(service_provider_key, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING)
    #     # vehicles : Dict[str, Vehicle] = devices.get(DeviceType.VEHICLE).all()
    #     # for veh_id, vehicle_obj in vehicles.items():
    #     #     # Eucilidean distance
    #     #     distance = np.linalg.norm(np.array(self._position) - np.array(vehicle_obj._position))
    #     #     if distance <= TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING:
    #     #         observed_surrounding_vehicles[veh_id] = vehicle_obj
    #     # Assuming vehicles is a dictionary with vehicle_id as key and vehicle object as value
    #     vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
    #     if vehicle_positions.shape[0] == 0:
    #         observed_surrounding_vehicles = {}
        
    #     else:
    #         vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
            
    #         self_position = np.array(self._position)
    #         distances = np.linalg.norm(vehicle_positions - self_position, axis=1)
    #         distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
    #         observed_surrounding_vehicles = {veh_id: vehicles[veh_id] for veh_id, dist in zip(vehicles.keys(), distances) if dist <= distance_threshold}

                        
    
    
    # if self._id in smart_phones.keys():
    #     if service_provider_key.startswith("ped"):
    #         # person.subscribeContext(service_provider_key, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING, sc.VEHICLE_FEATURES)
    #         # observed_surrounding_vehicles = person.getContextSubscriptionResults(service_provider_key)
    #         # person.unsubscribeContext(service_provider_key, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING)
    #         vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
            
    #         if vehicle_positions.shape[0] == 0:
    #             observed_surrounding_vehicles = {}
            
    #         else:
    #             self_position = np.array(self._position)
    #             distances = np.linalg.norm(vehicle_positions - self_position, axis=1)
    #             distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
    #             observed_surrounding_vehicles = {veh_id: vehicles[veh_id] for veh_id, dist in zip(vehicles.keys(), distances) if dist <= distance_threshold}


            
            
    #     elif service_provider_key.startswith("bike"):
    #         # vehicle.subscribeContext(service_provider_key, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING, sc.VEHICLE_FEATURES)
    #         # observed_surrounding_vehicles = vehicle.getContextSubscriptionResults(service_provider_key)
    #         # vehicle.unsubscribeContext(service_provider_key, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING)
    #         vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
    #         if vehicle_positions.shape[0] == 0:
    #             observed_surrounding_vehicles = {}
            
    #         else:
    #             vehicle_positions = np.array([vehicle_obj._position for vehicle_obj in vehicles.values()])
                
    #             self_position = np.array(self._position)
    #             distances = np.linalg.norm(vehicle_positions - self_position, axis=1)
    #             distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
    #             observed_surrounding_vehicles = {veh_id: vehicles[veh_id] for veh_id, dist in zip(vehicles.keys(), distances) if dist <= distance_threshold}
    


def add_sensed_device(service_provider_table, id, service_provider, sensed_device):
    record = SensedDeviceRecord(service_provider, sensed_device)
    key = (sc.TIME, service_provider._id, sensed_device._id)
    service_provider_table[key] = record.__dict__





def get_position(self : Union[SmartPhone,Vehicle], mobile_device : dict):
        self._speed : float =  mobile_device[tc.VAR_SPEED]
        self._position : List[float] = mobile_device[tc.VAR_POSITION]
        
        self._edge_id : str = mobile_device[tc.VAR_ROAD_ID]
        self._lane_id : str = mobile_device[tc.VAR_LANE_ID]
        self._lane_position : float = mobile_device[tc.VAR_LANEPOSITION]
                
        if self._type == DeviceType.VEHICLE:
            self._lane_index : int = mobile_device[tc.VAR_LANE_INDEX]
            
        
def getNumberOfObjects(edgeID):
    vehiclesNumber = traci.edge.getLastStepVehicleNumber(edgeID)
    return vehiclesNumber

def getNumberOfObjects(laneID):
    vehiclesNumber = traci.lane.getLastStepVehicleNumber(laneID)
    return vehiclesNumber

def getObjects(edgeID):        
    vehicles = traci.edge.getLastStepVehicleIDs(edgeID)
    return vehicles

def getObjects(laneID):
    vehicles = traci.lane.getLastStepVehicleIDs(laneID)        
    return vehicles

def getVehicleDimensions(veh_id : str) -> dict:
    
    devices   = device_handler.get_devices_group_handler() 
    vehicles : Dict[str,Vehicle] = devices.get(DeviceType.VEHICLE).all()
    smart_phones : Dict[str,SmartPhone] = devices.get(DeviceType.SMART_PHONE).all()
    sensed_object = {}
    
    if veh_id not in vehicles.keys():
        dimensions = {
            'width':np.nan,
            'length':np.nan,
            'height':np.nan
        }
        return dimensions
    
    sensed_object = vehicles[veh_id]
    
    dimension = {
        'width':sensed_object._width,
        'length':sensed_object._length,
        'height':sensed_object._height
    }     
    return dimension

def getObjectColor(obj_id):
    vehicleType = traci.vehicle.getTypeID(obj_id)
    vehicleColor = traci.vehicletype.getColor(vehicleType)
    
    return vehicleColor
    
def getPosition(veh_id):
    return traci.vehicle.getPosition3D(veh_id)
    

def getType(veh_id):
    
    try:    
        vehicle_type = traci.vehicle.getTypeID(veh_id)
        if vehicle_type == 'veh_passenger':
            classVehicle = traci.vehicletype.getVehicleClass(vehicle_type)
            return classVehicle

    except exceptions.TraCIException as e:
        e.with_traceback()
        
    return veh_id 
   

def getLicensePlate(veh_id):
    license_plate = str(veh_id)
    return license_plate
