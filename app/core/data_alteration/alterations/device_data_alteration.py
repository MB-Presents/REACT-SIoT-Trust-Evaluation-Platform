from __future__ import annotations
from typing import TYPE_CHECKING, Union
import random
import copy
import traci

from core.data_alteration.common import AlterationType, SignificanceLevel
from core.models.devices.common import DeviceType
from scenarios.canberra_case_study.core.networks import NetworkConstants

if TYPE_CHECKING:
    from models.devices.smart_phone import SmartPhone
    from models.devices.vehicle import Vehicle

# Constants
ROUTING_MODE_DEFAULT = 0
ROUTING_MODE_AGGREGATED = 1
VEHICLE_TYPES = ["truck_truck", "veh_passenger", "emergency_vehicle", "moto_motorcycle", "bus_bus", "bicycle_bicycle"]
MINOR_EDGE_MIN_DISTANCE = 60
MINOR_EDGE_MAX_DISTANCE = 150
MAJOR_EDGE_MIN_DISTANCE = 200
LANE_SUFFIX = "_0"

def modify_device_data(device: Union[Vehicle, SmartPhone]) -> Union[Vehicle, SmartPhone]:
    """Modify device data based on its type and return the modified copy."""

    if device._type == DeviceType.VEHICLE:
        device._alternated_device_data = modify_vehicle_data(device._alternated_device_data)
    elif device._type == DeviceType.SMART_PHONE:
        device._alternated_device_data = modify_smart_phone_data(device._alternated_device_data)
    
    return device._alternated_device_data

def modify_edge_id(device: Union[Vehicle, SmartPhone], min_distance: float, max_distance: float) -> None:
    """Modify the device's edge ID to a new edge within the specified distance range."""
    current_edge = device._edge_id
    while True:
        new_edge = random.choice(NetworkConstants.EDGES)
        distance = traci.simulation.getDistanceRoad(current_edge, 0, new_edge, 0)
        if min_distance < distance < max_distance:
            device._edge_id = new_edge
            new_lane = f"{new_edge}{LANE_SUFFIX}"
            if new_lane in NetworkConstants.LANES:
                device._lane_id = new_lane
                break
            else:
                raise ValueError(f"Lane ID {new_lane} not found in NetworkConstants.LANES")

def modify_lane_position(device: Vehicle, offset: float, interval_length: float) -> None:
    """Adjust the device's lane position by a random deviation."""
    device._lane_position += random.uniform(offset - interval_length, offset + interval_length)

def modify_position(device: SmartPhone, offset: float, interval_length: float) -> None:
    """Adjust the device's 2D position by random deviations in x and y coordinates."""
    deviation_x = random.uniform(offset - interval_length, offset + interval_length)
    deviation_y = random.uniform(offset - interval_length, offset + interval_length)
    device._position = (device._position[0] + deviation_x, device._position[1] + deviation_y)

def modify_speed(device: Union[Vehicle, SmartPhone], offset: float, interval_length: float) -> float:
    """Modify the device's speed by selecting a random value within defined ranges."""
    min_speed_lower = device._speed - offset - interval_length
    max_speed_lower = device._speed - offset
    min_speed_upper = device._speed + offset
    max_speed_upper = device._speed + offset + interval_length
    return random.choice([
        random.uniform(min_speed_lower, max_speed_lower),
        random.uniform(min_speed_upper, max_speed_upper)
    ])

def modify_signal(device: Union[Vehicle, SmartPhone], major: bool = False) -> None:
    """Modify the device's signal by flipping bits (major or minor manipulation)."""
    device._signal ^= 1 if major else random.randint(0, 1)

def modify_vehicle_type(device: Vehicle, vehicle_types: list[str]) -> None:
    """Assign a random vehicle type from the provided list."""
    device._vehicle_type = random.choice(vehicle_types)

def modify_dimension(device: Vehicle, attribute: str, offset: float, interval_length: float) -> None:
    """Modify a specified dimension attribute by a random factor."""
    current_value = getattr(device, attribute)
    setattr(device, attribute, current_value * random.uniform(1 - interval_length, 1 + interval_length))

def modify_vehicle_data(vehicle: Vehicle) -> Vehicle:
    """Apply modifications to vehicle data based on alteration type and significance."""
    if vehicle._alteration_type == AlterationType.STATIC:
        return vehicle

    if vehicle._alteration_type == AlterationType.DYNAMIC:
        if vehicle._significance_level == SignificanceLevel.SLIGHT:
            modify_edge_id(vehicle, MINOR_EDGE_MIN_DISTANCE, MINOR_EDGE_MAX_DISTANCE)
            modify_lane_position(vehicle, -5, 5)
            vehicle._speed = modify_speed(vehicle, 0.95, 0.05)
            modify_signal(vehicle)
            modify_vehicle_type(vehicle, VEHICLE_TYPES)
            modify_dimension(vehicle, '_width', 0.95, 0.05)
            modify_dimension(vehicle, '_length', 0.95, 0.05)
        elif vehicle._significance_level == SignificanceLevel.SIGNIFICANT:
            modify_edge_id(vehicle, MAJOR_EDGE_MIN_DISTANCE, float('inf'))
            modify_lane_position(vehicle, -30, 30)
            vehicle._speed = modify_speed(vehicle, 0.5, 0.5)
            modify_signal(vehicle, major=True)
            modify_vehicle_type(vehicle, VEHICLE_TYPES)
            modify_dimension(vehicle, '_width', 0.8, 0.2)
            modify_dimension(vehicle, '_length', 0.8, 0.2)
    
    return vehicle

def modify_smart_phone_data(smart_phone: SmartPhone) -> SmartPhone:
    """Apply modifications to smartphone data based on alteration type and significance."""
    if smart_phone._alteration_type == AlterationType.STATIC:
        return smart_phone

    if smart_phone._alteration_type == AlterationType.DYNAMIC:
        if smart_phone._significance_level == SignificanceLevel.SLIGHT:
            modify_position(smart_phone, -5, 5)
            smart_phone._speed = modify_speed(smart_phone, 0.95, 0.05)
            modify_edge_id(smart_phone, MINOR_EDGE_MIN_DISTANCE, MINOR_EDGE_MAX_DISTANCE)
        elif smart_phone._significance_level == SignificanceLevel.SIGNIFICANT:
            modify_position(smart_phone, -30, 30)
            smart_phone._speed = modify_speed(smart_phone, 0.5, 0.5)
            modify_edge_id(smart_phone, MAJOR_EDGE_MIN_DISTANCE, float('inf'))
    
    return smart_phone