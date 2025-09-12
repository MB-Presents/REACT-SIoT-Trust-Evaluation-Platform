def update_mobile_device_position(device: Union[SmartPhone, Vehicle], device_data: Dict) -> None:
    """Update position-related attributes for a mobile device."""
    device._speed = device_data[VAR_SPEED]
    device._position = device_data[VAR_POSITION]
    device._edge_id = device_data[VAR_ROAD_ID]
    device._lane_id = device_data[VAR_LANE_ID]
    device._lane_position = device_data[VAR_LANEPOSITION]
    
    if device._type == DeviceType.VEHICLE:
        device._lane_index = device_data[VAR_LANE_INDEX]