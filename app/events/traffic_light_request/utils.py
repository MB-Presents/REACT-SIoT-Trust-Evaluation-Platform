import random
from typing import Dict
import traci
from data_models.iot_devices.common import DeviceType
from data_models.iot_devices.device_handler import Devices_Group_Handler, get_devices_group_handler
from data_models.iot_devices.vehicle import Vehicle
from experiments.settings import Settings
import utils.simulation as simulation_utils
from data.simulation.scenario_constants import Constants as sc


def met_time_and_vehicles_preconditions():
    time = sc.TIME_STRING
    devices: Devices_Group_Handler = get_devices_group_handler()
    vehicles_simulation = devices.get(DeviceType.VEHICLE).all()
    return sc.TIME % Settings.INTERVAL_OF_FALSE_TRAFFIC_LIGHT_REQUESTS == 0 and len(vehicles_simulation) > 0


def select_vehicle(vehicles_simulation : Dict[str,Vehicle]):
    
    
    while len(vehicles_simulation) > 0:
        
        requestor_id, requestor = random.choice(list(vehicles_simulation.items()))
        
        if is_vehicle_suitable(requestor_id, requestor):
            return requestor_id
        
        del vehicles_simulation[requestor_id]
        
    return None



def is_vehicle_suitable(requestor_id : str, requestor : Vehicle):
    
    is_not_emergency_vehicle = not requestor_id.startswith("emergency_veh")
    is_not_in_arrived_vehicle_list = requestor_id not in traci.simulation.getArrivedIDList()
    
    is_in_simulation = simulation_utils.is_object_in_simulation(requestor_id)
    has_trafficLights_on_route = are_traffic_lights_in_distance(requestor_id) 
    
    
    return (
        is_not_emergency_vehicle and
        is_not_in_arrived_vehicle_list and
        is_in_simulation and
        has_trafficLights_on_route
    )
    
def are_traffic_lights_in_distance(requestor_id):
    traffic_lights = traci.vehicle.getNextTLS(requestor_id)
    for traffic_light in traffic_lights:
        if traffic_light[2] <= 50: # traffic_light[2] is the distance to the traffic light.
            return False
    return len(traffic_lights) > 0
