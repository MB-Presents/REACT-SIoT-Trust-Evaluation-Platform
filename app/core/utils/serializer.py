from __future__ import annotations
from typing import TYPE_CHECKING

from core.models.devices.common import DeviceType
# from core.models.devices.genric_iot_device import GenericDevice
from core.models.uniform.components.report import SendingPacket




if TYPE_CHECKING:
# from core.models.devices.device_handler import DevicesGroupHandler
    
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.vehicle import Vehicle
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.induction_loop import InductionLoop


from pandas import DataFrame


import core.models.devices.device_handler as handler



import traci.constants as tc
import copy





# def uniform_data_models(selected_service_provider: dict) -> Dict[str, Union[TrafficCamera, InductionLoop, Vehicle, SmartPhone]]:

#     # devices : DevicesGroupHandler  = handler.get_devices_group_handler()
#     vehicles = DevicesGroupHandler().get_devices_by_group(DeviceType.VEHICLE)

#     service_provider_table : Dict[str, Any]= {}
    
#     id: int = itertools.count()
    
#     service_provider : Union[TrafficCamera, InductionLoop, Vehicle, SmartPhone]
#     service_providers : Dict[str, Union[TrafficCamera, InductionLoop, Vehicle, SmartPhone]] = {}
    
#     for service_provider_key, service_provider in selected_service_provider.items():

#         if isinstance(service_provider,TrafficCamera): 
            
            
#             if len(service_provider._captured_vehicles.keys()) > 0:
            
#                 for observed_vehicle_key, vehicle_object in service_provider._captured_vehicles.items():
                    
#                     sensed_device = service_provider._captured_vehicles[observed_vehicle_key]
#                     # service_providers = {service_provider_key: service_provider}
#                     add_sensed_device(service_provider_table, id, service_provider, sensed_device)
                    
#             elif len(service_provider._captured_vehicles.keys()) == 0:
#                 # TODO: ADD DATA if no vehicles has been sensed
                
#                 no_sensed_device = add_no_sensed_device_object()
#                 add_sensed_device(service_provider_table, id, service_provider, no_sensed_device)
            
#         elif isinstance(service_provider,InductionLoop):            
            
#             if len(service_provider._captured_vehicles_features.keys()) > 0:
                
#                 for captured_vehicle_key, captured_vehicle in service_provider._captured_vehicles_features.items():
#                     sensed_device = captured_vehicle
#                     # service_providers = { captured_vehicle_key: captured_vehicle }
#                     add_sensed_device(service_provider_table, id, service_provider, sensed_device)
#             elif len(service_provider._captured_vehicles_features.keys()) == 0:
#                 # TODO: Add data if no vehicles has been sensed
                
                
#                 no_sensed_device = add_no_sensed_device_object()
#                 add_sensed_device(service_provider_table, id, service_provider, no_sensed_device)

#         elif isinstance(service_provider, Vehicle):
#             service_providers = {service_provider_key: service_provider}
            
#             if len(service_provider._sensed_devices.keys()) > 0:
            
#                 service_provider_table.update(service_provider._sensed_devices)
#             elif len(service_provider._sensed_devices.keys()) == 0:
#                 # TODO: Add data if no vehicles has been sensed
                
#                 no_sensed_device = add_no_sensed_device_object()
#                 add_sensed_device(service_provider_table, id, service_provider, no_sensed_device)
           
           
#         elif isinstance(service_provider, SmartPhone):
#             service_providers = {service_provider_key: service_provider}
            
#             if len(service_provider._sensed_devices.keys()) > 0:
            
#                 service_provider_table.update(service_provider._sensed_devices)
            
#             elif len(service_provider._sensed_devices.keys()) == 0:
#                 # TODO: Add data if no vehicles has been sensed
#                 no_sensed_device = add_no_sensed_device_object()
#                 add_sensed_device(service_provider_table, id, service_provider, no_sensed_device)
                
                    
                   
#         else:
#             raise Exception("Unknown service provider type")
                    

#     # return service_providers
#     return service_provider_table

# def add_no_sensed_device_object():
#     from core.models.devices.genric_iot_device import GenericDevice
#     no_device_object_dummy = GenericDevice(
#         device_id="No Device",
#         device_type=None,
#         device_behaviour=None,
#         position=None,
#         color=None,
#     )
    
#     return no_device_object_dummy
    
    
    


# def add_sensed_device(service_provider_table, id, service_provider, sensed_device):
#     record = SensedDeviceRecord(service_provider, sensed_device)
#     key = (ScenarioParameters.TIME, service_provider._id, sensed_device._id)
#     service_provider_table[key] = record.__dict__
        
        
def get_service_provider_status(service_providers_candidates : dict) -> dict:
    
    devices : handler.DevicesGroupHandler= handler.get_device_handler()
    vehicles = devices.get_devices_by_group(DeviceType.VEHICLE)
    smart_phones = devices.get_devices_by_group(DeviceType.SMART_PHONE)
    selected_service_provider = {}
    
    for device_key, device in service_providers_candidates.items():

        if device[tc.VAR_TYPE] == "trafficCamera":
            traffic_camera: TrafficCamera = devices.get_devices_by_group(DeviceType.TRAFFIC_CAMERA)
            selected_service_provider[device_key] = traffic_camera

        elif device[tc.VAR_TYPE] == "induction_loop":
            induction_loop: InductionLoop = devices.get_devices_by_group(DeviceType.INDUCTION_LOOP)
            selected_service_provider[device_key] = induction_loop

        elif device_key in vehicles:
            vehicle_record: Vehicle = vehicles[device_key]
            selected_service_provider[device_key] = vehicle_record
            
        elif device_key in smart_phones:
            smart_phone_record: SmartPhone = smart_phones[device_key]
            selected_service_provider[device_key] = smart_phone_record
            
    return selected_service_provider


def report_to_dataframe(report : SendingPacket) -> DataFrame:
    
    report_dict = copy.deepcopy(report.__dict__)
    
    reporter_list_id = []
    reporter_locations = []
    
    for reporter_key, reporter_object in report.sending_entities.items():        
        reporter_list_id.append(reporter_object.id)
        reporter_locations.append(reporter_object.location)
         
    report_dict['reporters_id'] = list(reporter_list_id)
    report_dict['reporters_location'] = list(reporter_locations)

    report_dict['object_of_interest_' + 'object_id'] = report.object_of_interest.object_id
    report_dict['object_of_interest_' + 'edge_id'] = report.object_of_interest.edge_id
    report_dict['object_of_interest_' + 'lane_id'] = report.object_of_interest.lane_id
    report_dict['object_of_interest_' + 'lane_position'] = report.object_of_interest.lane_position
    report_dict['object_of_interest_' + 'location'] = report.object_of_interest.location
    
    
    if 'reporters' in report_dict.keys():
        del report_dict['reporters']  
        
    if 'object_of_interest' in report_dict.keys():
        del report_dict['object_of_interest']
        
    vehicle = report.object_of_interest
        
    
    # file_name = f"/temp/dict_traffic_light_report_{ report.report_id }_vehicle_{vehicle.object_id}.pickle"
    
    
    df_report: DataFrame = pd.DataFrame.from_dict({0: report_dict}, orient='index')

    return df_report