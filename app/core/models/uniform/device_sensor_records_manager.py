
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Union
from core.models.devices.common import DeviceType
from core.models.devices.induction_loop import InductionLoop
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.traffic_camera import TrafficCamera
from core.models.devices.vehicle import Vehicle



if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler
    from core.models.uniform.components.report import SendingPacket

from core.models.uniform.object_sensor_records import ObjectSensorRecords
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings
from traci import poi, TraCIException
import traci.constants as tc
from scenarios.canberra_case_study.core.scenario_config import ScenarioDeviceConfiguration


from typing import Dict

from core.models.devices.genric_iot_device import GenericDevice


class ObjectSensorRecordManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObjectSensorRecordManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if ObjectSensorRecordManager._initialized:
            return
            
        from core.models.devices.device_handler import DevicesGroupHandler
        self.device_handler = DevicesGroupHandler
        self.dummy_object = GenericDevice(
            device_id="No Device",
            device_type=None,
            device_behaviour=None,
            position=None,
            color=None,
        )
        ObjectSensorRecordManager._initialized = True
    
    
    def get_service_provider_candidates(self, report : SendingPacket) -> dict:
            
        service_providers_candidates = {}
        
        try:
            for reporter_id, reporter in report.sending_entities.items():
                
                # poi.add(reporter_id, reporter.position[0], reporter.position[1], reporter.type, reporter.color, reporter.layer)
            
                poi.subscribeContext(reporter.poi_id, tc.CMD_GET_VEHICLE_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, ScenarioDeviceConfiguration.VEHICLE_FEATURES)
                poi.subscribeContext(reporter.poi_id, tc.CMD_GET_PERSON_VARIABLE, AccidentSettings.SERVICE_REQUESTOR_DISTANCE, ScenarioDeviceConfiguration.SMART_PHONE_FEATURES)
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
    
    
    
    def get_service_provider_status(self, service_providers_candidates : dict) -> dict:
    
        vehicles = self.device_handler.get_devices_by_group(DeviceType.VEHICLE)
        smart_phones = self.device_handler.get_devices_by_group(DeviceType.SMART_PHONE)
        selected_service_provider = {}
        
        for device_key, device in service_providers_candidates.items():

            if device[tc.VAR_TYPE] == "trafficCamera":
                traffic_camera: TrafficCamera = self.device_handler.get_device(device_key)
                selected_service_provider[device_key] = traffic_camera

            elif device[tc.VAR_TYPE] == "induction_loop":
                induction_loop: InductionLoop = self.device_handler.get_device(device_key)
                selected_service_provider[device_key] = induction_loop

            elif device_key in vehicles:
                vehicle_record: Vehicle = vehicles[device_key]
                selected_service_provider[device_key] = vehicle_record
                
            elif device_key in smart_phones:
                smart_phone_record: SmartPhone = smart_phones[device_key]
                selected_service_provider[device_key] = smart_phone_record
                
        return selected_service_provider
        
    
    
    def uniform_data_models(self, selected_service_provider:  Dict[str,Union[TrafficCamera, InductionLoop, Vehicle, SmartPhone]]) -> ObjectSensorRecords:

        # devices : DevicesGroupHandler  = handler.get_devices_group_handler()
        vehicles = self.device_handler.get_devices_by_group(DeviceType.VEHICLE)
        object_sensor_records = ObjectSensorRecords()

        service_provider_table : Dict[str, Any]= {}

        
        for service_provider_key, service_provider in selected_service_provider.items():

            if isinstance(service_provider,TrafficCamera): 
                
                
                if len(service_provider._captured_vehicles.keys()) > 0:
                
                    for observed_vehicle_key, vehicle_object in service_provider._captured_vehicles.items():
                        
                        sensed_device = service_provider._captured_vehicles[observed_vehicle_key]
                        object_sensor_records.add_record(service_provider, sensed_device)
                        
                elif len(service_provider._captured_vehicles.keys()) == 0:
                    # TODO: ADD DATA if no vehicles has been sensed
                    object_sensor_records.add_record(service_provider, self.dummy_object)
            elif isinstance(service_provider,InductionLoop):            
                
                if len(service_provider._captured_vehicles_features.keys()) > 0:
                    
                    for captured_vehicle_key, captured_vehicle in service_provider._captured_vehicles_features.items():
                        sensed_device = captured_vehicle
                        object_sensor_records.add_record(service_provider, sensed_device)
                elif len(service_provider._captured_vehicles_features.keys()) == 0:
                    # TODO: Add data if no vehicles has been sensed
                    object_sensor_records.add_record(service_provider, self.dummy_object)
    

            elif isinstance(service_provider, Vehicle):
                service_providers = {service_provider_key: service_provider}
                
                if len(service_provider._sensed_devices.keys()) > 0:
                
                    service_provider_table.update(service_provider._sensed_devices)
                elif len(service_provider._sensed_devices.keys()) == 0:
                    # TODO: Add data if no vehicles has been sensed
                    object_sensor_records.add_record(service_provider, self.dummy_object)
            
            
            elif isinstance(service_provider, SmartPhone):
                service_providers = {service_provider_key: service_provider}
                
                if len(service_provider._sensed_devices.keys()) > 0:
                    service_provider_table.update(service_provider._sensed_devices)
                
                
                elif len(service_provider._sensed_devices.keys()) == 0:
                    # TODO: Add data if no vehicles has been sensed
                    object_sensor_records.add_record(service_provider, self.dummy_object)
                    
                        
                    
            else:
                raise Exception("Unknown service provider type")
                        

        # return service_providers
        return object_sensor_records

