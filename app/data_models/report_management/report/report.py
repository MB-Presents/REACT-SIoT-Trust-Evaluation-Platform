
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import copy
from data_models.events.simulation_events import VerificationState


from data_models.report_management.report.report_models import ReportType, Situation




from data_models.simulation.logging import ObjectType



if TYPE_CHECKING:
    from data_models.events.simulation_events import SimulationEvent
    from data_models.iot_devices.vehicle import Vehicle
    from scenario.emergency_response.emergency_vehicle import EmergencyVehicle
    from scenario.emergency_response.emergency_response import EmergencyResponseCenter
    from data_models.iot_devices.traffic_light import TrafficLightSystem
    from data_models.iot_devices.smart_phone import SmartPhone
    from data_models.report_management.report.reporter import SendersEntity
    from data_models.report_management.report.object_of_interest import ObjectOfInterest
    from data_models.iot_devices.genric_iot_device import GenericDevice
    

import itertools
from typing import Dict, Union
from scenario.emergency_response.constants import AccidentStatus
from scenario.intelligent_traffic_light.constants import RequestLifecycleStatus
from data.simulation.scenario_constants import Constants as sc

import utils.logging as logger



class SendingPacket:

    report_id = itertools.count()
    time : float = None
    sending_entities : Dict[str, SendersEntity] = {}
    situation : Situation = None
    object_of_interest : ObjectOfInterest = None
    trustworthiness : VerificationState = VerificationState.UNVERIFIED
    trust_score : float = None
    event_status : Union[AccidentStatus, RequestLifecycleStatus] = None


    def __init__(self, time: str, receiver : str, sending_entities: Dict[str, SendersEntity],  situation: Situation, object_of_interest: ObjectOfInterest, type : ReportType = None, report_status: Union[AccidentStatus, RequestLifecycleStatus] = None, simulation_event : SimulationEvent = None):

        self.report_id = next(SendingPacket.report_id)
        self.assigned_emergency_vehicle : EmergencyVehicle = None

        self.receiving_entity : GenericDevice = receiver
        self.time: str = time
        
        self.sending_entities : Dict[str, SendersEntity] = sending_entities
        self.situation: Situation = situation
        self.object_of_interest: ObjectOfInterest = object_of_interest

        self.request_type: ReportType = type
        self.event_status:  Union[AccidentStatus, RequestLifecycleStatus] = report_status
        
        self.time_constraint_status : RequestLifecycleStatus = RequestLifecycleStatus.PENDING
        
        
        self.report_status_history: Dict[int,Union[AccidentStatus, RequestLifecycleStatus]] = {1 : {"sending_event_status" : self.event_status,
                                                                                                     "time": float(self.time)}
                                                                                                }
        
        if self.request_type == ReportType.TraffiCPriorityRequest:
            self.remaining_decision_time : float = 600
        elif self.request_type == ReportType.EmergencyReport:
            self.remaining_decision_time : float = 600
        
        
        self.trustworthiness: VerificationState = VerificationState.UNVERIFIED
        self.simulation_event : SimulationEvent = simulation_event
        
        self.service_providers : Dict[str,Any] = {}
        self.selected_service_provider : Dict[str,Any] = {}
        
    def get_accident_dict(self):
        
        accident_report = copy.copy(self)
        accident_report = accident_report.__dict__        
        
        accident_report['event_status'] = self.event_status.name
        del accident_report['assigned_emergency_vehicle']
        
        accident_report['sending_entities'] = [reporter for reporter in self.sending_entities.keys()]
        accident_report['situation'] = self.situation.name
        accident_report['object_of_interest'] = self.object_of_interest.object_id
        accident_report['request_type'] = self.request_type.name
        del accident_report['report_status_history']
        accident_report['trustworthiness'] = self.trustworthiness.name
        accident_report['simulation_event'] = self.simulation_event.id
        del accident_report['service_providers']
        accident_report['time_constraint_status'] = self.time_constraint_status.name
        accident_report['ground_truth'] = self.simulation_event.is_authentic
        del accident_report['receiving_entity'] 
        
        if 'authenticity_score' in accident_report:
            del accident_report['trust_score']
        return accident_report        
        
    def update_reporter(self, reporter: SendersEntity):
        self.sending_entities[reporter.id] = reporter
        
    def update_status(self, status: Union[AccidentStatus, RequestLifecycleStatus]):
        self.event_status = status
        self.report_status_history[len(self.report_status_history) + 1] = {"sending_event_status" : self.event_status,
                                                                            "time": sc.TIME} 
        
        accident_message = self.get_accident_dict()
        logger.info(ObjectType.REPORT, accident_message)
        
    
    def get_reporters(self) -> Dict[str, SendersEntity]:
        
        return self.sending_entities
    
    
    def add_reporters(self,reporters : Dict[str,SendersEntity]):
        
        for reporter_id, reporter in reporters.items():
            
            self.update_reporter(reporter)
            reporter.draw_reporter_location(reporter.authenticity)
            
   