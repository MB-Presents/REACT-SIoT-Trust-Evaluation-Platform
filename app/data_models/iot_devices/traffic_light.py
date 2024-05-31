
from __future__ import annotations
import random
from typing import Any, Dict, List, TYPE_CHECKING

import numpy as np
from data_models.iot_devices.genric_iot_device import GenericDevice


from data_models.services.report_manager_unit import ReportManagementComponent
from scenario.intelligent_traffic_light.constants import RequestLifecycleStatus

if TYPE_CHECKING:
    from data_models.iot_devices.vehicle import Vehicle
    from data_models.iot_devices.device_handler import Devices_Group_Handler

    from data_models.report_management.report.report import SendingPacket
    from data_models.report_management.report_manager import ReportManager

    
from traci import trafficlight
import traci

from data_models.report_management.report.report_models import ReportType, Situation
from data_alterantion_model.generate_device_profiles import generate_profiles
from data.simulation.scenario_constants import Constants as sc

from data_models.events.simulation_events import SimulationEventManager, VerificationState
from data_models.simulation.logging import ObjectType
from data_models.iot_devices.common import DeviceBehaviour, DeviceRecordType, DeviceType



from experiments.settings import Settings


import utils.logging as logger
import traci.constants as tc




class TrafficLightSystem(GenericDevice):
    
    def __init__(self, traffic_light_id : str, position,  profile, devices : Devices_Group_Handler) -> None:
       
        super().__init__(   traffic_light_id, 
                            position=position,
                            manufacturer=profile['manufacturer'],
                            model=profile['model'],
                            firmware_version=profile['firmware_version'],
                            hardware_version=profile['hardware_version'],
                            serial_number=profile['serial_number'],  
                            date_of_manufacture=profile['manufacture_date'],  
                            last_maintenance_date=profile['last_maintenance_date'],
                            next_maintenance_date=profile['next_maintenance_date'],  
                            device_type=DeviceType.TRAFFIC_LIGHT,
                            device_behaviour=DeviceBehaviour.TRUSTWORTHY)
        
        self._id: str = traffic_light_id
        self._priority_backlog_vehicles : List[str] = []
        self._assessed_vehicle : List[str] = []
        self._requesting_vehicles : List[str] = []
        self._service_providers : Dict[int,Any] = {}
        self._controlled_lanes : List[str] = []
        self._controlled_links : List[str] = []
        self._current_program : int = 0
        self._current_phase : int = 0
        self._next_switch : int = 0
        self._phase_duration : int = 0
        self._ryg_state : str = ""
        self.report_manager = ReportManagementComponent(self,devices=devices)
        
    def update(self, controlled_lanes, controlled_links, current_program, current_phase, next_switch, phase_duration, ryg_state):
            self._controlled_lanes = controlled_lanes
            self._controlled_links = controlled_links
            self._current_program = current_program
            self._current_phase = current_phase
            self._next_switch = next_switch
            self._phase_duration = phase_duration
            self._ryg_state = ryg_state    
    
    
    def hasPassed(self, vehicle_id : str):
        return vehicle_id in self._priority_backlog_vehicles
    
    def remove_passed_vehicle(self, vehicle_id : str):
        if vehicle_id in self._priority_backlog_vehicles:
            self._priority_backlog_vehicles.remove(vehicle_id)


    def process_reports(self, 
                        reports : Dict[str,SendingPacket], 
                        simulation_event_manager : SimulationEventManager):
        
        if len(self._requesting_vehicles) == 0:
            return
        
        for report_id, report in reports.items():    
            if not Settings.VERIFY_TRAFFIC_LIGHT_REQUEST_AUTHENTICITY:
                report.trustworthiness = VerificationState.NOT_AUTHENTIC

            if report.request_type != ReportType.TraffiCPriorityRequest: 
                raise Exception("Invalid report type")
                continue
            
            if report.event_status == RequestLifecycleStatus.VERIFIED:
                continue
                
            report.remaining_decision_time = report.remaining_decision_time - 1
            
            # Update of Location
            report.object_of_interest.location = report.sending_entities[report.object_of_interest.object_id].device._position
            
            if report.trustworthiness == VerificationState.UNVERIFIED and report.event_status == RequestLifecycleStatus.PENDING:
                self.report_manager.handle_unverified_requests(report, simulation_event_manager)
                self.report_manager.handle_verified_report(report, simulation_event_manager)
                
                self.update_traffic_light_schedule(report)

            # If TrafficRequest is verified
            if report.trustworthiness != VerificationState.UNVERIFIED and report.event_status == RequestLifecycleStatus.FINISHED: 
                
                
                position_traffic_light = report.receiving_entity._position

                for sender_id, sending_vehicles in report.sending_entities.items():
                    
                    
                    position_requestor = sending_vehicles.device._position

                    distance = np.linalg.norm(np.array(position_traffic_light) - np.array(position_requestor))
                    
                    if distance <= 10:
                        report.receiving_entity.update_request_status(report)
                        print(f"Traffic light {report.receiving_entity._id} - Authenticity:  {report.trustworthiness} at {report.time} with trustworthiness {report.trustworthiness} and distance {distance}")
                        




    def update_traffic_light_schedule(self, report):
        if report.trustworthiness == VerificationState.AUTHENTIC: 
            traffic_light_system : TrafficLightSystem  = report.receiving_entity
            traffic_light_system.schedule_priority_request(report)
                    
        elif report.trustworthiness == VerificationState.NOT_AUTHENTIC:
            traffic_light_system : TrafficLightSystem  = report.receiving_entity
            traffic_light_system.remove_rejected_requests(report)     
                    
                
            
            
            
            
            
        
    def schedule_priority_request(self, report : SendingPacket):
        

        if report.object_of_interest.object_id not in self._assessed_vehicle:
            self._assessed_vehicle.append(report.object_of_interest.object_id)
        

        if report.object_of_interest.object_id in self._requesting_vehicles:
            self._requesting_vehicles.remove(report.object_of_interest.object_id)
            
        if report.object_of_interest.object_id not in self._priority_backlog_vehicles:
            self._priority_backlog_vehicles.append(report.object_of_interest.object_id)    

    def remove_rejected_requests(self, report : SendingPacket):
            
        if report.object_of_interest.object_id not in self._assessed_vehicle:
            self._assessed_vehicle.append(report.object_of_interest.object_id)
        
        if report.object_of_interest.object_id in self._requesting_vehicles:
            self._requesting_vehicles.remove(report.object_of_interest.object_id)
        
    def update_service_providers(self, report_id, service_providers : dict):
        
        if  report_id not in self._service_providers.keys():
            self._service_providers[report_id] = dict()
            
        report_based_service_providers = self._service_providers[report_id] 
        report_based_service_providers = report_based_service_providers | service_providers
        self._service_providers[report_id] = report_based_service_providers
        
        return self._service_providers[report_id]


    def request_priority(self,requesting_vehicle_id):
        self._requesting_vehicles.append(requesting_vehicle_id)
        
    def get_dict(self):
        device_dict = super().to_dict()
        device_dict['record_type'] = DeviceRecordType.STATUS.name
        
        return device_dict


class TrafficLightManager:

    traffic_lights: Dict[str, TrafficLightSystem] = {}
    

    def __init__(self, device_handler : Devices_Group_Handler):
        self._devices = device_handler
        self.traffic_lights : Dict[str,TrafficLightSystem] = {}
        
        trustworthy_traffic_light_profile, _ = generate_profiles('traffic_lights', 4, 0)
        
        self.trustworthy_traffic_light_profile = trustworthy_traffic_light_profile


        for traffic_light_id in trafficlight.getIDList():
            position = traci.junction.getPosition(traffic_light_id)
            
            profile = random.choice(self.trustworthy_traffic_light_profile)
            
            
            self.traffic_lights[traffic_light_id] = TrafficLightSystem(traffic_light_id,
                                                                       position=position,
                                                                       profile=profile,
                                                                       devices=self._devices)
    
    def subscribe(self):
        trafficlights = traci.trafficlight.getIDList()
        for traffic_light_id in trafficlights:
            traci.trafficlight.subscribe(traffic_light_id,sc.TRAFFIC_LIGHT_FEATURES)
            
    def update(self) -> None:
        
        trafficlights =traci.trafficlight.getIDList()
        
        for traffic_light_id in trafficlights:

            traffic_light = traci.trafficlight.getSubscriptionResults(traffic_light_id)
            
            controlled_lanes = traffic_light[tc.TL_CONTROLLED_LANES] 
            controlled_links = traffic_light[tc.TL_CONTROLLED_LINKS] 
            current_program =  traffic_light[tc.TL_CURRENT_PROGRAM] 
            current_phase = traffic_light[tc.TL_CURRENT_PHASE]
            next_switch = traffic_light[tc.TL_NEXT_SWITCH] 
            phase_duration = traffic_light[tc.TL_PHASE_DURATION]
            ryg_state =     traffic_light[tc.TL_RED_YELLOW_GREEN_STATE]
            
            self.traffic_lights[traffic_light_id].update(controlled_lanes, controlled_links, current_program, current_phase, next_switch, phase_duration, ryg_state)
            
    def get_status(self):
        return self.vehicles.__dict__
   
    def log(self):
        
        for traffic_light_id, traffic_light_object in self.traffic_lights.items():
    
            try:                
                message = traffic_light_object.get_dict()
                logger.info(ObjectType.TRAFFIC_LIGHT, message, logger.LoggingBehaviour.STATUS)      

            except Exception as e:
                str(e)

    def get_vehicle(self,index : str) -> Vehicle:
    
        return self.vehicles[index]


    def process_traffic_requests(self, report_manager: ReportManager, simulation_event_manager: SimulationEventManager):
        
        unverified_reports : Dict[str,SendingPacket] = report_manager.get_unverified_reports_by_situation(Situation.TRAFFIC_PRIORITY_REQUEST)
        traffic_request_reports: Dict[str, Dict[str, SendingPacket]] = self.get_reports(unverified_reports)

        if len(traffic_request_reports) == 0:
            return

        for traffic_light_id, reports in traffic_request_reports.items():
            if traffic_light_id in self.traffic_lights:
                traffic_light = self.traffic_lights[traffic_light_id]
            traffic_light.process_reports(reports, simulation_event_manager)

    def get_reports(self, unverified_traffic_reports: Dict[str,SendingPacket]) -> Dict[str, Dict[str, SendingPacket]]:
        traffic_light_reports: Dict[str, Dict[str, SendingPacket]] = {}

        for report_id, report in unverified_traffic_reports.items():
            traffic_light_id = report.receiving_entity._id

            if traffic_light_id not in traffic_light_reports:
                traffic_light_reports[traffic_light_id] = {}

            traffic_light_reports[traffic_light_id][str(report_id)] = report

        return traffic_light_reports
    
    
    def all(self):
        return self.traffic_lights
    
    


                    
                    

        
                
        
        
        
        