
from __future__ import annotations
from typing import TYPE_CHECKING

import random
from typing import Union
from data_alterantion_model.common import AlterationType, SignificanceLevel
from data_models.iot_devices.common import DeviceType

if TYPE_CHECKING:
    from data_models.iot_devices.smart_phone import SmartPhone
    from data_models.iot_devices.vehicle import Vehicle
    
from data.simulation.network_constants import NetworkConstants
import traci
import random
import copy
# Traci constants
ROUTING_MODE_DEFAULT = 0
ROUTING_MODE_AGGREGATED = 1

vType = ["truck_truck", "veh_passenger", "emergency_vehicle", "moto_motorcycle", "bus_bus", "bicycle_bicycle"]

def get_alternated_data(device : Union[Vehicle, SmartPhone]):
    
    
    # if device._alternated_device_data is  None:
    #     device._alternated_device_data = copy.deepcopy(device)
        
    
    if device._type == DeviceType.VEHICLE:
        device._alternated_device_data = alternate_vehicle_data(device._alternated_device_data)
    
    elif device._type == DeviceType.SMART_PHONE:
        device._alternated_device_data = alternate_smart_phone_data(device._alternated_device_data)
    
    return device._alternated_device_data
    
    
def major_edge_id_manipulation(device):
    
    current_edge = device._edge_id
    is_far_edge_found = False
    
    while not is_far_edge_found:
    
        potential_far_edge = random.choice(NetworkConstants.EDGES)
        distance = traci.simulation.getDistanceRoad(current_edge, 0, potential_far_edge, 0)
    
        if distance > 200:
            device._edge_id = potential_far_edge
            is_far_edge_found = True
    
    potential_lane_id = device._edge_id + "_0"
    
    if potential_lane_id in NetworkConstants.LANES:
        device._lane_id = potential_lane_id
        return
    elif potential_lane_id not in NetworkConstants.LANES:
        raise Exception("Lane id not found")

import random

def edge_id_manipulation(device, min_distance, max_distance):
    current_edge = device._edge_id
    is_far_edge_found = False
    
    while not is_far_edge_found:
        potential_far_edge = random.choice(NetworkConstants.EDGES)
        distance = traci.simulation.getDistanceRoad(current_edge, 0, potential_far_edge, 0)

        if min_distance < distance < max_distance:
            device._edge_id = potential_far_edge
            is_far_edge_found = True


def lane_position_manipulation(device, offset, interval_length):
    device._lane_position += random.uniform(offset - interval_length, offset + interval_length)

def position_manipulation(device, offset, interval_length):
    deviation_x = random.uniform(offset - interval_length, offset + interval_length)
    deviation_y = random.uniform(offset - interval_length, offset + interval_length)
    device._position = (device._position[0] + deviation_x, device._position[1] + deviation_y)

def speed_manipulation(device, offset, interval_length):
    
    min_speed1 = device._speed - offset - interval_length
    max_speed1 = device._speed - offset
    min_speed2 = device._speed + offset
    max_speed2 = device._speed + offset + interval_length
    
    min_speed = random.uniform(min_speed1, max_speed1)
    max_speed = random.uniform(min_speed2, max_speed2)
    
    return random.choice([min_speed, max_speed])

def signal_manipulation(device, major=False):
    if major:
        device._signal ^= 1  # flipping all bits for major manipulation
    else:
        device._signal ^= random.randint(0, 1)  # minor manipulation

def vehicle_type_manipulation(device, vType):
    vehicle_type = random.choice(vType)
    device._vehicle_type = vehicle_type 

def dimension_manipulation(device, attribute, offset, interval_length):
    setattr(device, attribute, getattr(device, attribute) * random.uniform(1 - interval_length, 1 + interval_length))

def alternate_vehicle_data(vehicle):
    if vehicle._alteration_type == AlterationType.STATIC:
        return

    elif vehicle._alteration_type == AlterationType.DYNAMIC:
        if vehicle._significance_level == SignificanceLevel.SLIGHT:
            edge_id_manipulation(vehicle, 60, 150)
            lane_position_manipulation(vehicle, -5, 5)
            speed_manipulation(vehicle, 0.95, 0.05)
            signal_manipulation(vehicle)
            vehicle_type_manipulation(vehicle, vType)
            dimension_manipulation(vehicle, '_width', 0.95, 0.05)
            dimension_manipulation(vehicle, '_length', 0.95, 0.05)
        elif vehicle._significance_level == SignificanceLevel.SIGNIFICANT:
            edge_id_manipulation(vehicle, 200, float('inf'))
            lane_position_manipulation(vehicle, -30, 30)
            speed_manipulation(vehicle, 0.5, 0.5)
            signal_manipulation(vehicle, major=True)
            vehicle_type_manipulation(vehicle, vType)
            dimension_manipulation(vehicle, '_width', 0.8, 0.2)
            dimension_manipulation(vehicle, '_length', 0.8, 0.2)
            
    return vehicle

def alternate_smart_phone_data(smart_phone):
    if smart_phone._alteration_type == AlterationType.STATIC:
        return

    elif smart_phone._alteration_type == AlterationType.DYNAMIC:
        if smart_phone._significance_level == SignificanceLevel.SLIGHT:
            # Minor manipulations
            position_manipulation(smart_phone, -5, 5)
            speed_manipulation(smart_phone, 0.95, 0.05)
            edge_id_manipulation(smart_phone, 60, 150)
        elif smart_phone._significance_level == SignificanceLevel.SIGNIFICANT:
            # Major manipulations
            position_manipulation(smart_phone, -30, 30)
            speed_manipulation(smart_phone, 0.5, 0.5)
            edge_id_manipulation(smart_phone, 200, float('inf'))

    return smart_phone
