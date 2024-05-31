
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Union
from data_models.iot_devices.common import DeviceBehaviour, DeviceType
from data_models.iot_devices.smart_phone import SmartPhone
from data_models.iot_devices.vehicle import Vehicle

from data_models.events.simulation_events import SimulationEvent


from scenario.intelligent_traffic_light.constants import TrafficLightApplicationSettings
if TYPE_CHECKING:
    from data_models.iot_devices.device_handler import Devices_Group_Handler
    from data_models.report_management.report.report import SendingPacket

from scenario.emergency_response.constants import AccidentSettings
from traci import poi, vehicle, TraCIException, simulation,vehicle, person
import traci.constants as tc
from data.simulation.scenario_constants import Constants as sc
import utils.logging as logger


from utils import simulation as simulation_util


def get_service_provider_candidates(report : SendingPacket) -> dict:
        
    service_providers_candidates = {}
    
    try:
        for reporter_id, reporter in report.sending_entities.items():
            
            # poi.add(reporter_id, reporter.position[0], reporter.position[1], reporter.type, reporter.color, reporter.layer)
          
            poi.subscribeContext(reporter.poi_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, sc.VEHICLE_FEATURES)
            poi.subscribeContext(reporter.poi_id, tc.CMD_GET_PERSON_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, sc.SMART_PHONE_FEATURES)
            poi.subscribeContext(reporter.poi_id, tc.CMD_GET_POI_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, [tc.VAR_POSITION, tc.VAR_TYPE])
            
            sensed_service_providers_candidates = poi.getContextSubscriptionResults(reporter.poi_id)
            
            poi.unsubscribeContext(reporter.poi_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE)
            poi.unsubscribeContext(reporter.poi_id, tc.CMD_GET_PERSON_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE)
            poi.unsubscribeContext(reporter.poi_id, tc.CMD_GET_POI_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE)
            
            if report.object_of_interest.object_id in sensed_service_providers_candidates.keys():     # Accident vehicle cannot be a service provider
                del sensed_service_providers_candidates[report.object_of_interest.object_id]
                
            service_providers_candidates.update(sensed_service_providers_candidates)
                
            if reporter_id in service_providers_candidates:                 # Reporter cannot be a service provider
                                                                            # del service_providers_candidates[reporter.id]
                pass
                    
        return service_providers_candidates
    except TraCIException as e:
        print(e.__dict__)
        

def get_service_provider_candidates_trafficlight(report : SendingPacket) -> dict:
        
    service_providers_candidates = {}
    
    
    try:
        for reporter_id, reporter in report.sending_entities.items():
            
            
            if not simulation_util.is_object_in_simulation(reporter_id):
                # del report.reporters[reporter_id]
                continue
            
            
            vehicle.subscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.SERVICE_REQUESTOR_DISTANCE, sc.VEHICLE_FEATURES)
            vehicle.subscribeContext(reporter_id, tc.CMD_GET_PERSON_VARIABLE, TrafficLightApplicationSettings.SERVICE_REQUESTOR_DISTANCE, sc.SMART_PHONE_FEATURES)
            vehicle.subscribeContext(reporter_id, tc.CMD_GET_POI_VARIABLE, TrafficLightApplicationSettings.SERVICE_REQUESTOR_DISTANCE, [tc.VAR_POSITION, tc.VAR_TYPE])
            
            service_providers_candidates = vehicle.getContextSubscriptionResults(reporter_id)
            
            vehicle.unsubscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, TrafficLightApplicationSettings.SERVICE_REQUESTOR_DISTANCE)
            vehicle.unsubscribeContext(reporter_id, tc.CMD_GET_PERSON_VARIABLE, TrafficLightApplicationSettings.SERVICE_REQUESTOR_DISTANCE)
            vehicle.unsubscribeContext(reporter_id, tc.CMD_GET_POI_VARIABLE, TrafficLightApplicationSettings.SERVICE_REQUESTOR_DISTANCE)
            
            
            if report.object_of_interest in service_providers_candidates:       # Accident vehicle cannot be a service provider
                del service_providers_candidates[report.object_of_interest]
                
            if reporter_id in service_providers_candidates:                     # Reporter cannot be a service provider
                del service_providers_candidates[reporter.id]
                
                    
        return service_providers_candidates
    except TraCIException as e:
        print(e.__dict__)
        
        
def get_reporters(event_object : SimulationEvent, devices : Devices_Group_Handler) -> Dict[str,Union[SmartPhone,Vehicle]]:
    
    domain_variable =  tc.CMD_GET_VEHICLE_VARIABLE
    poi.subscribeContext(event_object.poi_id, domain_variable, AccidentSettings.REPORTER_RADIUS, sc.REPORTER_FEATURES)
    reporter_objects = poi.getContextSubscriptionResults(event_object.poi_id)
    poi.unsubscribeContext(event_object.poi_id, domain_variable, AccidentSettings.REPORTER_RADIUS)
        
    # Avoid self reporting
    if event_object.event_catalyst in reporter_objects:
        del reporter_objects[event_object.event_catalyst]
    
    vehicles : Dict[str, Vehicle] = devices.get(DeviceType.VEHICLE).all()
    smartphones : Dict[str, SmartPhone] = devices.get(DeviceType.SMART_PHONE).all()
    
    reporters = {}
    
    for reporter_id, reporter_object in reporter_objects.items():
        
        
        
        
        
        if reporter_id in vehicles.keys():
            
            if vehicles[reporter_id]._behaviour != DeviceBehaviour.TRUSTWORTHY:
                continue
            
            
            reporters[reporter_id] = vehicles[reporter_id]
            
        elif reporter_id in smartphones.keys():
            
            
            if smartphones[reporter_id]._behaviour != DeviceBehaviour.TRUSTWORTHY:
                continue
            
            reporters[reporter_id] = smartphones[reporter_id]
        
    
    return reporters


def get_surrounding_vehicles(reporter_id: str, reporter : SmartPhone, devices : Devices_Group_Handler) -> Dict[str, Vehicle]:

    try:
        surrounding_vehicles = {}
        filtered_vehicle_results: Dict[str, Vehicle] = {}

        smart_phones: Dict[str, SmartPhone] = devices.get(DeviceType.SMART_PHONE).all()

        vehicles: Dict[str, Vehicle] = devices.get(DeviceType.VEHICLE).all()

        if reporter_id in vehicles:

            vehicle.subscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, sc.VEHICLE_FEATURES)
            surrounding_vehicles = vehicle.getContextSubscriptionResults(reporter_id)
            vehicle.unsubscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE)

        elif reporter_id in smart_phones and reporter_id.startswith('ped'):

            person.subscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, sc.VEHICLE_FEATURES)
            surrounding_vehicles = person.getContextSubscriptionResults(reporter_id)
            person.unsubscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE)

        elif reporter_id in smart_phones and reporter_id.startswith('bike'):

            vehicle.subscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, sc.VEHICLE_FEATURES)
            surrounding_vehicles = vehicle.getContextSubscriptionResults(reporter_id)
            vehicle.unsubscribeContext(reporter_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE)

        for veh_id, vehicle_object in surrounding_vehicles.items():
            if veh_id in vehicles:
                filtered_vehicle_results[veh_id] = vehicle_object

    except TraCIException as e:
        logger.exception(e, e.__dict__)

    return filtered_vehicle_results
