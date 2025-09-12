def get_inductive_object_count(induction_loop: InductionLoop, devices: DevicesGroupHandler) -> Dict[str, Dict]:
    """Retrieve vehicles detected by an induction loop with their attributes."""
    
    vehicles: Dict[str, Vehicle] = devices.get(DeviceType.VEHICLE)
    vehicle_ids : Dict[str,Union[str,float]] = edge.getLastStepVehicleIDs(induction_loop._observed_street)
    
    captured_vehicles = {
        veh_id: {
            'device_id': veh_id,
            'dimension': get_vehicle_dimensions(veh_id),
            'speed': vehicles[veh_id]._speed,
            'lanePosition': vehicles[veh_id]._lane_position,
            'laneIndex': vehicles[veh_id]._lane_index,
            'laneID': vehicles[veh_id]._lane_id,
            'edgeID': vehicles[veh_id]._edge_id
        }
        for veh_id in vehicle_ids if veh_id in vehicles
    }
    
    induction_loop._captured_vehicles_features = captured_vehicles
    return captured_vehicles