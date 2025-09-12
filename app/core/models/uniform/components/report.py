
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import copy
from core.models.events.simulation_events import VerificationState





from core.models.uniform.components.object_of_interest import ObjectOfInterest
from core.models.uniform.components.report_models import ReportType, Situation
from core.models.uniform.components.reporter import SendersEntity
from core.simulation.logging import ObjectType




if TYPE_CHECKING:
    from core.models.events.simulation_events import SimulationEvent
    from core.models.devices.vehicle import Vehicle
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.smart_phone import SmartPhone

    from core.models.devices.genric_iot_device import GenericDevice
    

import itertools
from typing import Dict, Union
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentStatus
from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import RequestLifecycleStatus
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

import utils.logging as logger



class SendingPacket:

    _id = itertools.count()
    _timestamp : float 
    sending_entities : Dict[str, SendersEntity] = {}
    situation : Situation 
    object_of_interest : ObjectOfInterest 
    trustworthiness : VerificationState = VerificationState.UNVERIFIED
    trust_score : float 
    event_status : Union[AccidentStatus, RequestLifecycleStatus] 


    def __init__(self, time: float, receiver : GenericDevice, sending_entities: Dict[str, SendersEntity],  situation: Situation, object_of_interest: ObjectOfInterest, type : ReportType, report_status: Union[AccidentStatus, RequestLifecycleStatus], simulation_event : SimulationEvent):

        self._id = next(SendingPacket._id)
        self.assigned_emergency_vehicle : EmergencyVehicle = None

        self.receiving_entity : GenericDevice = receiver
        self._timestamp: float = time
        
        self.sending_entities : Dict[str, SendersEntity] = sending_entities
        self.situation: Situation = situation
        self.object_of_interest: ObjectOfInterest = object_of_interest

        self.request_type: ReportType = type
        self.event_status:  Union[AccidentStatus, RequestLifecycleStatus] = report_status
        
        self.time_constraint_status : RequestLifecycleStatus = RequestLifecycleStatus.PENDING
        
        
        self.report_status_history: Dict[int,Union[AccidentStatus, RequestLifecycleStatus]] = {1 : {"sending_event_status" : self.event_status,
                                                                                                     "time": float(self._timestamp)}
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
                                                                            "time": ScenarioParameters.TIME} 
        
        accident_message = self.get_accident_dict()
        logger.info(ObjectType.REPORT, accident_message)
        
    
    def get_reporters(self) -> Dict[str, SendersEntity]:
        
        return self.sending_entities
    
    
    def add_reporters(self,reporters : Dict[str,SendersEntity]):
        
        for reporter_id, reporter in reporters.items():
            
            self.update_reporter(reporter)
            reporter.draw_reporter_location(reporter.authenticity)
            
   