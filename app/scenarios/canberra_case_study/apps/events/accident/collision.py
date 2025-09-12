# import json
# import math
# import random

# from typing import Dict, List, Optional, Tuple

# import traci
# import traci.constants as tc
# from traci import exceptions, vehicle,edge, simulation
# from core.models.devices.common import DeviceType

# from core.models.devices.device_handler import DevicesGroupHandler
# from core.models.devices.genric_iot_device import DeviceBehaviour
# from core.models.devices.smart_phone import SmartPhone
# from core.models.devices.vehicle import Vehicle

# from core.models.events.simulation_events import EventType, SimulationEvent, SimulationEventManager

# from core.models.uniform.components.report_models import AuthenticityRole
# from core.models.uniform.components.reporter import SendersEntity


# from core.simulation import network
# from core.simulation.logging import ObjectType
# from experiments.settings import Settings

# from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings

# from scenarios.canberra_case_study.core.networks import NetworkConstants
# import utils.logging as logger
# from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters


# def filter_vehicle_candidates(vehicles: Dict[str, Vehicle]):
#     return {key: value for key, value in vehicles.items() if key.startswith('veh')}


# def get_vehicle_candidates(vehicles: Dict[str, Vehicle]):
#     return random.choice(list(vehicles.items()))


# def is_valid_simulation_context(vehicle_key: str, events_manager: SimulationEventManager):
#     return not events_manager.has_event_for_vehicle(vehicle_key)


# def calculate_required_braking_distance(vehicle_key):
#     max_decel = vehicle.getDecel(vehicle_key)
#     current_speed = vehicle.getSpeed(vehicle_key)
#     time = round((current_speed / max_decel) + 0.5)
#     return current_speed * time + (max_decel * time * time) / 2


# def get_base_edge_id(edge_id : str):
#     if ':' in edge_id:
#         edge_id = edge_id.split('_')[0]
#         edge_id = edge_id.removeprefix(':')
#     return edge_id


# def is_legit_vehicle_on_lane(edge_id):
#     edges =  traci.edge.getIDList()
#     junctions = traci.junction.getIDList()
#     return get_base_edge_id(edge_id) in edges and get_base_edge_id(edge_id) not in junctions


# def is_fake_collision_condition_fulfilled(veh_id: str, vehicles: Dict[str, Vehicle], events_manager: SimulationEventManager):
#     vehicle = vehicles[veh_id]
#     vehicle_exists = veh_id in vehicles.keys()
#     vehicle_is_not_collided = not events_manager.has_event_for_vehicle(veh_id)
#     vehicle_type_is_correct = vehicle._type in AccidentSettings.ALLOWED_VEHICLE_FAKE_COLLISION_TYPES
#     return vehicle_exists and vehicle_is_not_collided and vehicle_type_is_correct


# def find_index_of_edge_in_route(route : List[str], edge_id : str):
#     for index, edge in enumerate(route):
#         if edge == edge_id:
#             return index    
#     return -1

# def log_route_info(route_info: dict):
#     logger.info(ObjectType.ROUTE_MESSAGE, route_info)


# def is_valid_route(origin: str, destination: str, vehicle_type: str) -> bool:
#     route = traci.simulation.findRoute(origin, destination, vType=vehicle_type)
#     return len(route.edges) > 1


# def is_accessable_from_hospital(vehicle: Vehicle, edge_id: str, lane_position: float) -> bool:
#     destination = edge_id
#     route_info = {
#         'message': f"Route to accident successful for emergency vehicle from {AccidentSettings.EMERGENCY_DROP_OFF} to {destination}"
#     }
    
#     if not is_valid_route(AccidentSettings.EMERGENCY_DROP_OFF, destination, 'emergency_vehicle'):
#         route_info['message'] = f"Route to accident can not been establsihed for vehicle {vehicle._id} at {destination}, no collision triggered"
#         log_route_info(route_info)
#         return False
    
#     log_route_info(route_info)
#     return True


# def is_accessable_from_accident(vehicle: Vehicle, edge_id: str, lane_position: float) -> bool:
#     destination = edge_id
#     route_info = {
#         'message': f"Route to accident successful for emergency vehicle from {destination} to {AccidentSettings.EMERGENCY_DROP_OFF}"
#     }
    
#     if not is_valid_route(destination, AccidentSettings.EMERGENCY_DROP_OFF, 'emergency_vehicle'):
#         route_info['message'] = f"From accident to hospital can not been establsihed for vehicle {vehicle._id} at {destination}, no collision triggered"
#         log_route_info(route_info)
#         return False
    
#     log_route_info(route_info)
#     return True


# def is_allowed_on_lane(vehicle: Vehicle, edge_id: str) -> bool:
#     destination = edge_id
#     route_info = {
#         'message': f"Route to accident successful for emergency vehicle from {AccidentSettings.EMERGENCY_DROP_OFF} to {destination}"
#     }

#     allowed_vehicles = traci.lane.getAllowed(edge_id + '_0')
    
#     if 'emergency' not in allowed_vehicles:
#         route_info['message'] = f"Vehicle {vehicle._id} at {destination} is not allowed on lane: {vehicle._lane_id}"
#         log_route_info(route_info)
#         return False

#     return True


# def is_accident_routable_for_emergency_vehicle(vehicle: Vehicle, edgeId: str = None, lane_position: float = None) -> bool:
#     try:
#         if not is_accessable_from_hospital(vehicle, edgeId, lane_position):
#             return False
#         if not is_accessable_from_accident(vehicle, edgeId, lane_position):
#             return False
#         if not is_allowed_on_lane(vehicle, edgeId):
#             return False

#     except exceptions.TraCIException as e:
#         exception_info = {
#             'time': f"{ScenarioParameters.TIME}",
#             'exception_type': 'TraCIException',
#             'message': str(e)
#         }
#         print(exception_info)
#         logger.exception(json.dumps(exception_info))
#         return False

#     return True


# def is_valid_time_constraints(vehicles : Dict[str, Vehicle]) -> bool:
    
#     are_vehicles_in_simulation = len(vehicles) > 0
    
#     is_time_interval_triggered = ScenarioParameters.TIME % Settings.INTERVAL_OF_ACCIDENTS == 0
    
#     if not are_vehicles_in_simulation:
#         return False
#     elif ScenarioParameters.TIME  == 0:
#         return False
#     elif not is_time_interval_triggered:
#         return False
  
#     return True

# def is_vehicles_stoppable_at_edge(collision_vehicle: Vehicle, collision_vehicle_key: str, route: List[str], route_index: int, accumulated_length: float) -> Tuple[bool, Optional[str], Optional[float], float]:
    
#     edge_id = route[route_index]
#     required_distance = get_required_braking_distance(collision_vehicle_key)

#     try:
#         lane_length = traci.lane.getLength(edge_id + "_0")
        
#         if traci.edge.getLaneNumber(edge_id) <= 1:
#             if collision_vehicle._edge_id == edge_id:
#                 accumulated_length += lane_length - collision_vehicle._lane_position
#             else:
#                 accumulated_length += lane_length
#             return False, None, None, accumulated_length
        
#         length_to_end_of_current_edge = get_length_to_end_of_current_edge(collision_vehicle, lane_length, accumulated_length, edge_id, route, route_index)
#         accumulated_length = length_to_end_of_current_edge - lane_length
        
#         if length_to_end_of_current_edge > required_distance:
#             stop_position = length_to_end_of_current_edge - required_distance
            
            
#             offset = 30
#             min_lane_position_start_position = offset
#             max_lane_position_end_position = lane_length - offset
            
            
#             # if not is_valid_stop_position(stop_position, lane_length):
#             #     return False, None, None, accumulated_length
                        
#             if min_lane_position_start_position <= stop_position <= max_lane_position_end_position:
#                 stop_position = random.randint(
#                     round(min_lane_position_start_position),
#                     round(max_lane_position_end_position)
#                     )

#             if not is_on_lane(edge_id):
#                 return False, None, None, accumulated_length
#             if not is_allowed_on_lane(collision_vehicle, edge_id):
#                 return False, None, None, accumulated_length
#             if not is_accident_routable_for_emergency_vehicle(collision_vehicle, edge_id, stop_position):
#                 return False, None, None, accumulated_length
#             if edge_id == AccidentSettings.EMERGENCY_DROP_OFF:
#                 return False, None, None, accumulated_length
            
#             # print(f"{ScenarioParameters.TIME} \t| VALID COLLISION | Collision vehicle: {collision_vehicle_key}, Edge: {edge_id} at Position : {stop_position}, Accumulated length {accumulated_length}")
#             return True, edge_id, stop_position, accumulated_length
        
#         accumulated_length = length_to_end_of_current_edge
#         return False, None, None, accumulated_length
    
#     except exceptions.TraCIException as e:
#         print(e)
#         logger.exception(e, __file__)
#         route_index += 1


# # def is_valid_stop_position(stop_position: float, lane_length: float) -> bool:
# #     offset = 30
# #     min_lane_position_start_position = offset
# #     max_lane_position_end_position = lane_length - offset
    
# #     if lane_length < offset or stop_position <= min_lane_position_start_position:
# #         # print(f"stop position {stop_position} is not in range {min_lane_position_start_position} - {max_lane_position_end_position} for edge {edge_id} with collision vehicle {collision_vehicle_key}")
# #         return False
# #     return True

# def is_allowed_on_lane(collision_vehicle: Vehicle, edge_id: str) -> bool:
#     allowed_vehicles_on_lane = traci.lane.getAllowed(edge_id + "_0")
#     if allowed_vehicles_on_lane == collision_vehicle._vehicle_type:
#         return False
#     return True

# def get_required_braking_distance(collision_vehicle_key):
#     max_decel = vehicle.getDecel(collision_vehicle_key)
#     current_speed = vehicle.getSpeed(collision_vehicle_key)

#     time = (current_speed / max_decel)

#     time = round(time + 0.5)

#     required_distance = current_speed * time + (max_decel * time * time) / 2
#     return required_distance

# def get_length_to_end_of_current_edge(collision_vehicle: Vehicle, lane_length: float, accumulated_length: float, current_edge: str, route: List[str], route_index) -> float:
    
#     distance_to_end_of_next_edge : float = 0
#     if current_edge == collision_vehicle._edge_id:
#         distance_to_end_of_next_edge = lane_length - collision_vehicle._lane_position
        
#     elif current_edge != collision_vehicle._edge_id: 
#         length_of_next_edge = traci.lane.getLength(route[route_index] + "_0")
#         distance_to_end_of_next_edge = simulation.getDistanceRoad(collision_vehicle._edge_id, collision_vehicle._lane_position, route[route_index], length_of_next_edge, isDriving=True)
        
#     return distance_to_end_of_next_edge

# def is_on_lane(edge_id: str) -> bool:
#     # edges = traci.edge.getIDList()      # Extract this: Into seperate function
#     # junctions = traci.junction.getIDList()
#     # lanes = traci.lane.getIDList()
    
    
    
#     if '_' in edge_id:
#         edge_id = edge_id.split('_')[0]
    
#     # if edge_id.startswith(':'):
        
    
#     if edge_id not in NetworkConstants.EDGES:
#         return False
    
#     if edge_id in NetworkConstants.JUNCTIONS:
#         return False
        
#     return True

# def is_legit_collision_vehicle(vehicles: Dict[str, Vehicle], simulation_events: SimulationEventManager) -> Tuple[bool, Optional[str], Optional[Vehicle], Optional[str], Optional[float]]:
    
#     vehicle_candidates = {key: value for key, value in vehicles.items() if key.startswith('veh') }
    
#     while len(vehicle_candidates) != 0:
#         collision_vehicle_key, collision_vehicle = random.choice(list(vehicle_candidates.items()))
        
#         if is_valid_for_simulation_context(collision_vehicle_key, simulation_events):
#             is_valid_collision_veh, stopping_edge, stopping_position = is_valid_collision_vehicle(collision_vehicle_key, collision_vehicle, vehicles)
            
#             if is_valid_collision_veh:
#                 return True, collision_vehicle_key, collision_vehicle, stopping_edge, stopping_position
            
#         del vehicle_candidates[collision_vehicle_key]
    
#     return False, None, None, None, None

# def is_valid_for_simulation_context(collision_vehicle_key: str, simulation_events : SimulationEventManager) -> bool:

#     if simulation_events.exists_for_vehicle(collision_vehicle_key):
#         return False
        
#     return True


# def is_valid_collision_vehicle(collision_vehicle_key: str, collision_vehicle: Vehicle, vehicles: Dict[str, Vehicle]) -> Tuple[bool, Optional[str], Optional[float]]:
#     if vehicles[collision_vehicle_key]._vehicle_type not in AccidentSettings.ALLOWED_VEHICLE_COLLISION_TYPES:
#         del vehicles[collision_vehicle_key]
#         return False, None, None
    
    
    
    
#     if collision_vehicle_key.startswith("emergency_veh"):
#         del vehicles[collision_vehicle_key]
#         return False, None, None
    
#     stopping_edge, stopping_position = get_stop_parameters(collision_vehicle, collision_vehicle_key)
    
#     if stopping_edge is None or collision_vehicle._edge_id not in NetworkConstants.EDGES or edge.getLaneNumber(collision_vehicle._edge_id) == 1 or not is_on_lane(collision_vehicle._edge_id):
#         del vehicles[collision_vehicle_key]
#         return False, None, None
    
    
#     wrong_edges = ['489467563','489692410']
    
#     if stopping_edge in wrong_edges:
#         del vehicles[collision_vehicle_key]
#         return False, None, None
    
    
    
    
#     return True, stopping_edge, stopping_position


# def get_stop_parameters(collision_vehicle: Vehicle, collision_vehicle_key: str) -> Tuple[Optional[str], Optional[float]]:
#     route = traci.vehicle.getRoute(collision_vehicle_key)
#     route_index = find_index_of_edge_in_route(route, collision_vehicle._edge_id)
#     final_index = len(route) - 1
#     accumulated_length = 0

#     while route_index < final_index:
#         try:
#             is_stoppable_at_edge, stopping_edge, stopping_position, accumulated_length = is_vehicles_stoppable_at_edge(collision_vehicle, collision_vehicle_key, route, route_index, accumulated_length)
            
#             if is_stoppable_at_edge:
#                 return stopping_edge, stopping_position
            
#             route_index += 1
            
#         except exceptions.TraCIException as e:
#             logger.exception(e, __file__)
#             route_index += 1

#     return None, None





# ##############################################################################################################
# # Collision specific functions
# ####


# def find_false_reporter(simulation_event_manager : SimulationEventManager ):
    
    
#     devices : DevicesGroupHandler  = DevicesGroupHandler()
#     vehicles : Dict[str,Vehicle] = devices.get_devices_by_group(DeviceType.VEHICLE)
#     smart_phones : Dict[str,SmartPhone] = devices.get_devices_by_group(DeviceType.SMART_PHONE)
    
#     legit_accident_events : Dict[str,SimulationEvent] = simulation_event_manager.get_authentic_events_by_type(EventType.COLLISION)
    
#     smart_phone_candidates = smart_phones.copy()
    
    
    
#     vehicle_candidates = {key: vehicle for key, vehicle in vehicles.items() if vehicle._behaviour == DeviceBehaviour.MALICIOUS}
#     smart_phone_candidates = {key: smart_phone for key, smart_phone in smart_phone_candidates.items() if smart_phone._behaviour == DeviceBehaviour.MALICIOUS}
    
#     reporter_candidates = {**vehicle_candidates, **smart_phone_candidates}
    
    
#     while len(reporter_candidates) > 0:
#         reporter_id, reporter =  random.choice(list(reporter_candidates.items()))


#         legit_accident_event_id : str
#         legit_accident_event : SimulationEvent
        
#         has_distance = True
#         for legit_accident_event_id, legit_accident_event in legit_accident_events.items():
#             position_accident = legit_accident_event.location
            
        
#             if not is_min_distance(position_accident, reporter._position):
#                 del reporter_candidates[reporter_id]
#                 has_distance = False
#                 break
        
#         if not has_distance:
#             continue
        
#         surrounding_vehicles = network.get_surrounding_vehicles(reporter_id, reporter, devices)
        
#         vehicle = has_legit_false_vehicle(simulation_event_manager, vehicles, surrounding_vehicles)
            
#         if vehicle == {}: # if empty
#             del reporter_candidates[reporter_id]
#             continue

#         if len(surrounding_vehicles) == 0:
#             del reporter_candidates[reporter_id]
#             continue
        
#         reporter = SendersEntity(reporter, AuthenticityRole.UNAUTHENTIC,ScenarioParameters.TIME)
            
#         return reporter, vehicle
    
#     return None, None

# def is_min_distance(position_accident, position_fake_caller, min_distance=80):
#     return math.dist(position_accident, position_fake_caller) >= min_distance
    
        

# def are_false_accident_report_constraints_fulfilled(time):
#     return time != 0 and time % Settings.INTERVAL_OF_FALSE_ACCIDENTS == 0

# def is_false_accident_report_possible(selected_reporter_object):
#     return selected_reporter_object is not None



# def adjust_vehicle_position(vehicle : Vehicle):
#     position = vehicle._lane_position
#     if position < 15:
#         position = 15
#     length_lane = traci.lane.getLength(vehicle._lane_id)
#     if position > length_lane - 15:
#         position = length_lane - 15
#     return position


# def has_legit_false_vehicle(simulation_event_manager, vehicles, surrounding_vehicles):
#     for veh_id, vehicle_object in surrounding_vehicles.items():
#         vehicle = vehicles.get(veh_id)
#         if vehicle_conditions_met(veh_id, vehicle, vehicle_object, simulation_event_manager):
#             return vehicle
#     return {}



# def vehicle_conditions_met(veh_id :str, vehicle : Vehicle, vehicle_object : dict, simulation_event_manager : SimulationEventManager):
    
    
    
    
    
    
#     vehicle_is_not_collided = not simulation_event_manager.exists_for_vehicle(veh_id)
    
#     vehicle_type_is_correct = vehicle_object[tc.VAR_TYPE] in AccidentSettings.ALLOWED_VEHICLE_FAKE_COLLISION_TYPES
#     is_legit_vehicle = is_on_lane(vehicle._edge_id)
    
#     is_valid_lane_position = valid_lane_position(vehicle)
#     is_allowed_on_lane = vehicle_allowed_on_lane(vehicle)
#     is_routable_for_emergency_vehicle = is_accident_routable_for_emergency_vehicle(vehicle, edgeId=vehicle._edge_id, lane_position=20)
    
#     is_not_on_emergency_drop_off = vehicle._edge_id != AccidentSettings.EMERGENCY_DROP_OFF
#     is_not_emergency_vehicle = not veh_id.startswith('emergency_veh')
    
    
#     if  (   vehicle_is_not_collided and 
#             vehicle_type_is_correct and 
#             is_legit_vehicle and 
#             is_valid_lane_position and 
#             is_allowed_on_lane and 
#             is_routable_for_emergency_vehicle and 
#             is_not_on_emergency_drop_off and 
#             is_not_emergency_vehicle):
        
#         return True
#     return False

# def valid_lane_position(vehicle : Vehicle) :
#     lane_length = traci.lane.getLength(vehicle._edge_id + "_0")
#     end_lane = lane_length - 15
#     return 15 <= vehicle._lane_position <= end_lane

# def vehicle_allowed_on_lane(vehicle : Vehicle):
#     allowed_vehicles_on_lane = traci.lane.getAllowed(vehicle._edge_id + "_0") 
    
    
#     return vehicle._vehicle_class in allowed_vehicles_on_lane
