from __future__ import annotations
from typing import TYPE_CHECKING, Union, Tuple, List
import random
import copy
from git import Optional
import traci

from core.data_alteration.common import AlterationType, SignificanceLevel
from core.models.devices.common import DeviceType
from scenarios.canberra_case_study.core.networks import NetworkConstants

if TYPE_CHECKING:
    from models.devices.smart_phone import SmartPhone
    from models.devices.vehicle import Vehicle

# Constants
ROUTING_MODE_DEFAULT: int = 0
ROUTING_MODE_AGGREGATED: int = 1
VEHICLE_TYPES: List[str] = ["truck_truck", "veh_passenger", "emergency_vehicle", 
                           "moto_motorcycle", "bus_bus", "bicycle_bicycle"]

def get_alternated_data(device: Union[Vehicle, SmartPhone]) -> Union[Vehicle, SmartPhone]:
    """Get alternated data for a device based on its type."""
    assert device is not None, "Device cannot be None"
    assert isinstance(device, (Vehicle, SmartPhone)), "Invalid device type"
    
    result: Optional[Union[Vehicle, SmartPhone]] = None
    
    # Initialize alternated data if not present
    if device._alternated_device_data is None:
        device._alternated_device_data = copy.deepcopy(device)
    
    if device._type == DeviceType.VEHICLE:
        assert isinstance(device, Vehicle), "Device must be an instance of Vehicle"
        alternative_vehicle_representation = device._alternated_device_data
        assert isinstance(alternative_vehicle_representation, Vehicle), "Alternated data must be a Vehicle instance"
        
        result = alternate_vehicle_data(vehicle=alternative_vehicle_representation)
    elif device._type == DeviceType.SMART_PHONE:
        assert isinstance(device, SmartPhone), "Device must be an instance of SmartPhone"
        alternative_smartphone_representation = device._alternated_device_data
        assert isinstance(alternative_smartphone_representation, SmartPhone), "Alternated data must be a SmartPhone instance"
        result = alternate_smart_phone_data(smart_phone=alternative_smartphone_representation)
    else:
        raise ValueError(f"Unsupported device type: {device._type}")
    
    assert result is not None, "Alternated data must not be None"
    assert isinstance(result, (Vehicle, SmartPhone)), "Result must be Vehicle or SmartPhone"
    return result

def major_edge_id_manipulation(device: Union[Vehicle, SmartPhone]) -> None:
    """Perform major edge ID manipulation with minimum distance of 200."""
    assert hasattr(device, '_edge_id'), "Device must have edge_id attribute"
    # assert device._edge_id in NetworkConstants.EDGES, "Current edge_id not in valid edges"
    assert NetworkConstants.EDGES, "NetworkConstants.EDGES cannot be empty"
    
    original_edge: str = device._edge_id
    while True:
        potential_edge: str = random.choice(NetworkConstants.EDGES)
        distance = traci.simulation.getDistanceRoad(original_edge, 0, potential_edge, 0)
        assert isinstance(distance, float), "Distance must be a float"
        assert distance >= 0, "Distance must be non-negative"
        
        if distance > 200:
            device._edge_id = potential_edge
            potential_lane_id: str = f"{potential_edge}_0"
            
            # if potential_lane_id in NetworkConstants.LANES:
            device._lane_id = potential_lane_id
            break
            # raise ValueError(f"Invalid lane ID: {potential_lane_id}")
    
    assert device._edge_id in NetworkConstants.EDGES, "New edge_id must be valid"
    # assert device._lane_id in NetworkConstants.LANES, "New lane_id must be valid"
    # assert traci.simulation.getDistanceRoad(original_edge, 0, device._edge_id, 0) > 200, "New edge must be more than 200 units away"

def edge_id_manipulation(device: Union[Vehicle, SmartPhone], min_distance: float, max_distance: float) -> None:
    """Manipulate edge ID within specified distance range."""
    assert hasattr(device, '_edge_id'), "Device must have edge_id attribute"
    # assert device._edge_id in NetworkConstants.EDGES, "Current edge_id not in valid edges"
    assert min_distance < max_distance, "min_distance must be less than max_distance"
    assert min_distance >= 0, "min_distance must be non-negative"
    assert NetworkConstants.EDGES, "NetworkConstants.EDGES cannot be empty"
    
    original_edge: str = device._edge_id
    while True:
        potential_edge: str = random.choice(NetworkConstants.EDGES)
        distance = traci.simulation.getDistanceRoad(original_edge, 0, potential_edge, 0)
        assert isinstance(distance, float), "Distance must be a float"
        assert distance >= 0, "Distance must be non-negative"
        
        if min_distance < distance < max_distance:
            device._edge_id = potential_edge
            break
    
    assert device._edge_id in NetworkConstants.EDGES, "New edge_id must be valid"
    

def lane_position_manipulation(device: Union[Vehicle, SmartPhone], offset: float, interval_length: float) -> None:
    """Manipulate lane position with random offset."""
    
    assert isinstance(device, (Vehicle, SmartPhone)), "Device must be Vehicle or SmartPhone"
    assert hasattr(device, '_lane_position'), "Device must have lane_position attribute"
    assert interval_length >= 0, "interval_length must be non-negative"
    
    original_position: float = device._lane_position
    device._lane_position += random.uniform(offset - interval_length, offset + interval_length)
    
    assert device._lane_position != original_position, "Lane position must change"
    assert device._lane_position >= 0, "Lane position must be non-negative"

def position_manipulation(device: Union[Vehicle, SmartPhone], offset: float, interval_length: float) -> None:
    """Manipulate 2D position with random deviation."""
    assert hasattr(device, '_position'), "Device must have position attribute"
    assert isinstance(device._position, tuple), "Position must be a tuple"
    assert len(device._position) == 2, "Position must be 2D"
    assert interval_length >= 0, "interval_length must be non-negative"
    
    original_position: Tuple[float, float] = device._position
    deviation_x: float = random.uniform(offset - interval_length, offset + interval_length)
    deviation_y: float = random.uniform(offset - interval_length, offset + interval_length)
    device._position = (device._position[0] + deviation_x, device._position[1] + deviation_y)
    
    assert device._position != original_position, "Position must change"
    assert isinstance(device._position, tuple), "Position must remain a tuple"
    assert len(device._position) == 2, "Position must remain 2D"

def speed_manipulation(device: Union[Vehicle, SmartPhone], offset: float, interval_length: float) -> float:
    """Manipulate speed with random variation."""
    assert hasattr(device, '_speed'), "Device must have speed attribute"
    assert device._speed >= 0, "Speed must be non-negative"
    assert offset >= 0, "offset must be non-negative"
    assert interval_length >= 0, "interval_length must be non-negative"
    
    original_speed: float = device._speed
    min_speed: float = random.uniform(device._speed - offset - interval_length, 
                                   device._speed - offset)
    max_speed: float = random.uniform(device._speed + offset, 
                                   device._speed + offset + interval_length)
    new_speed: float = random.choice([min_speed, max_speed])
    
    assert new_speed >= 0, "New speed must be non-negative"
    assert new_speed != original_speed, "Speed must change"
    return new_speed

def signal_manipulation(vehicle: Vehicle, major: bool = False) -> None:
    """Manipulate signal strength."""
    assert isinstance(vehicle, Vehicle), "Input must be a Vehicle instance"
    assert hasattr(vehicle, '_signal'), "Device must have signal attribute"

    original_signal: int = vehicle._signal
    if major:
        vehicle._signal ^= 1
    else:
        vehicle._signal ^= random.randint(0, 1)

    assert vehicle._signal in [0, 1], "Signal must be 0 or 1"
    if major:
        assert vehicle._signal != original_signal, "Signal must change for major manipulation"

def vehicle_type_manipulation(device: Vehicle, vehicle_types: List[str]) -> None:
    """Change vehicle type randomly from provided list."""
    assert hasattr(device, '_vehicle_type'), "Device must have vehicle_type attribute"
    assert vehicle_types, "Vehicle types list cannot be empty"
    
    original_type: str = device._vehicle_type
    device._vehicle_type = random.choice(vehicle_types)
    
    assert device._vehicle_type in vehicle_types, "New vehicle type must be valid"
    assert device._vehicle_type != original_type, "Vehicle type must change"

def dimension_manipulation(device: Union[Vehicle, SmartPhone], attribute: str, 
                         offset: float, interval_length: float) -> None:
    """Manipulate dimension attributes (width/length)."""
    assert hasattr(device, attribute), f"Device must have {attribute} attribute"
    assert interval_length >= 0, "interval_length must be non-negative"
    assert offset >= 0, "offset must be non-negative"
    
    original_value: float = getattr(device, attribute)
    new_value: float = original_value * random.uniform(1 - interval_length, 1 + interval_length)
    setattr(device, attribute, new_value)
    
    assert getattr(device, attribute) > 0, f"{attribute} must be positive"
    assert getattr(device, attribute) != original_value, f"{attribute} must change"

def alternate_vehicle_data(vehicle: Vehicle) -> Vehicle:
    """Apply data alterations to vehicle based on significance level."""
    assert isinstance(vehicle, Vehicle), "Input must be a Vehicle instance"
    assert vehicle._device_behavior_profile._alteration_type in AlterationType, "Invalid alteration type"
    assert vehicle._device_behavior_profile._significance_level in SignificanceLevel, "Invalid significance level"
    
    original_state = copy.deepcopy(vehicle)
    if vehicle._device_behavior_profile._alteration_type == AlterationType.STATIC:
        return vehicle

    if vehicle._device_behavior_profile._alteration_type == AlterationType.DYNAMIC:
        if vehicle._device_behavior_profile._significance_level == SignificanceLevel.SLIGHT:
            edge_id_manipulation(vehicle, 60.0, 150.0)
            lane_position_manipulation(vehicle, -5.0, 5.0)
            vehicle._speed = speed_manipulation(vehicle, 0.95, 0.05)
            signal_manipulation(vehicle)
            vehicle_type_manipulation(vehicle, VEHICLE_TYPES)
            dimension_manipulation(vehicle, '_width', 0.95, 0.05)
            dimension_manipulation(vehicle, '_length', 0.95, 0.05)
        elif vehicle._device_behavior_profile._significance_level == SignificanceLevel.SIGNIFICANT:
            major_edge_id_manipulation(vehicle)
            lane_position_manipulation(vehicle, -30.0, 30.0)
            vehicle._speed = speed_manipulation(vehicle, 0.5, 0.5)
            signal_manipulation(vehicle, major=True)
            vehicle_type_manipulation(vehicle, VEHICLE_TYPES)
            dimension_manipulation(vehicle, '_width', 0.8, 0.2)
            dimension_manipulation(vehicle, '_length', 0.8, 0.2)
    
    assert vehicle != original_state, "Vehicle state must change after dynamic alteration"
    return vehicle

def alternate_smart_phone_data(smart_phone: SmartPhone) -> SmartPhone:
    """Apply data alterations to smartphone based on significance level."""
    assert isinstance(smart_phone, SmartPhone), "Input must be a SmartPhone instance"
    assert smart_phone._device_behavior_profile._alteration_type in AlterationType, "Invalid alteration type"
    assert smart_phone._device_behavior_profile._significance_level in SignificanceLevel, "Invalid significance level"

    original_state = copy.deepcopy(smart_phone)
    if smart_phone._device_behavior_profile._alteration_type == AlterationType.STATIC:
        return smart_phone
    
    elif smart_phone._device_behavior_profile._alteration_type == AlterationType.DYNAMIC:
        if smart_phone._device_behavior_profile._significance_level == SignificanceLevel.SLIGHT:
            position_manipulation(smart_phone, -5.0, 5.0)
            smart_phone._speed = speed_manipulation(smart_phone, 0.95, 0.05)
            edge_id_manipulation(smart_phone, 60.0, 150.0)
        elif smart_phone._device_behavior_profile._significance_level == SignificanceLevel.SIGNIFICANT:
            position_manipulation(smart_phone, -30.0, 30.0)
            smart_phone._speed = speed_manipulation(smart_phone, 0.5, 0.5)
            major_edge_id_manipulation(smart_phone)
    
    assert smart_phone != original_state, "SmartPhone state must change after dynamic alteration"
    return smart_phone