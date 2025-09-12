

def get_vehicle_status(vehicle: Vehicle, vehicle_data: Dict) -> None:
    """Update a vehicle's attributes based on provided data."""
    vehicle._speed = vehicle_data[VAR_SPEED]
    vehicle._position = vehicle_data[VAR_POSITION]
    vehicle._edge_id = vehicle_data[VAR_ROAD_ID]
    vehicle._lane_id = vehicle_data[VAR_LANE_ID]
    vehicle._lane_position = vehicle_data[VAR_LANEPOSITION]
    vehicle._lane_index = vehicle_data[VAR_LANE_INDEX]
    vehicle._color = vehicle_data[VAR_COLOR]
    vehicle._signal = vehicle_data.get(VAR_SIGNALS, 0)