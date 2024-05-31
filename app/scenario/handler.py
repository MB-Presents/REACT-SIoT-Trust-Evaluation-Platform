import sys
from typing import Dict, List, Union
from data_models.report_management.report.report_models import ReportType, Situation
from data_models.report_management.report.object_of_interest import ObjectOfInterest 
from data_models.report_management.report.report import SendingPacket
from data_models.report_management.report_manager import ReportManager

from data_models.events.simulation_events import EventRecord, EventState, EventType, SimulationEvent, SimulationEventManager, VerificationState
from data_models.simulation.logging import ObjectType
from experiments.settings import Settings

from environment.behavior import disable_accident_behaviour, enable_accident_behaviour
from scenario.emergency_response.constants import AccidentStatus

from scenario.emergency_response.emergency_vehicle import EmergencyVehicle

from traci import simulation,vehicle 
from data.simulation.scenario_constants import Constants as sc
from utils import convert
import utils.logging as logger

from loguru import logger as logurulogger

class ScenarioHandler:

    def __init__(self) -> None:
        
        self._logger = logurulogger.bind(context="scenario_handler")
        self._stdout_handler_id = None


    def update_events(self, simulation_event_manager : SimulationEventManager):



        accident_events : Dict[str,SimulationEvent] = simulation_event_manager.get_simulation_events_by_event(EventType.COLLISION)

        for event_id, event in accident_events.items():

            if event.state == EventState.TRIGGERED and event.is_authentic:
                
                enable_accident_behaviour(event)
                event_record: EventRecord = EventRecord(event.id, EventState.ONGOING, sc.TIME, event.location)
                event.update_state(event_record)
                    
            elif event.state == EventState.ONGOING and (sc.TIME - float(event.time)) > 900:
                event_record: EventRecord = EventRecord(event.id, EventState.ONGING_FOR_15_MIN, sc.TIME, event.location)
                event.update_state(event_record)
            
            elif event.state == EventState.REPORTED:
                pass
            
            elif event.state == EventState.SOLVED:
                pass
            
            elif event.state == EventState.ONGOING:
                pass 


    def update_accidents(self, report_manager: ReportManager):
        
        for accident_id, accident_report in report_manager.reports.items():
            if accident_report.event_status == AccidentStatus.IGNORE_UNSOVLED:
                disable_accident_behaviour(accident_report,color=(0,0,255,255))
                
            elif accident_report.event_status == AccidentStatus.ACCIDENT_SOLVED and accident_report.simulation_event.is_authentic:
                disable_accident_behaviour(accident_report, color=(0, 255, 0, 255))



    def get_solved_accidents(self, accident_reports : Dict[str,SendingPacket], event_manager : SimulationEventManager):
        
        solved_accidents = 0
        collision_events = event_manager.get_simulation_events_by_event(EventType.COLLISION)
        
        for accident_id, accident_report in accident_reports.items():
            
            ground_truth = collision_events[accident_report.simulation_event.id]
            
            if not (ground_truth.is_authentic == True and accident_report.trustworthiness == VerificationState.AUTHENTIC):
                continue
            
            if accident_report.event_status == AccidentStatus.COMPLETE_SOLVED:
                solved_accidents += 1
                
        return solved_accidents


    def is_finished(self, report_manager: ReportManager, event_manager: SimulationEventManager):
        
        
        if len(report_manager.reports) <= 2:
            return False

        accidnet_reports = report_manager.get_reports_by_type(ReportType.EmergencyReport)
        number_of_solved_accidents = self.get_solved_accidents(accidnet_reports,event_manager)
        
        
        authentic_accidnets = report_manager.get_authentic_reports_by_type(ReportType.EmergencyReport)
        authentic_traffic_light_requests = report_manager.get_authentic_reports_by_type(ReportType.TraffiCPriorityRequest)
        
        
        unverified_accidents = report_manager.get_unverified_reports_by_situation(Situation.EMERGENCY_REPORT)
        unverfied_traffic_light_requests = report_manager.get_unverified_reports_by_situation(Situation.TRAFFIC_PRIORITY_REQUEST)
        
        unauthentic_accidnets = report_manager.get_unauthentic_reports_by_type(ReportType.EmergencyReport)
        unauthentic_traffic_light_requests = report_manager.get_unauthentic_reports_by_type(ReportType.TraffiCPriorityRequest)
        
        
        
        
        
        if sc.TIME % 50 == 0:
            self._logger.info(f"{sc.TIME_STRING} \t | Solved Accidents: {number_of_solved_accidents}  \t | Unverified Accidents: {len(unverified_accidents)} \t | Unauthentic Accidents: {len(unauthentic_accidnets)} \t | Authentic Accidents: {len(authentic_accidnets)} \t | Unverified Traffic Light Requests: {len(unverfied_traffic_light_requests)} \t | Unauthentic Traffic Light Requests: {len(unauthentic_traffic_light_requests)} \t | Authentic Traffic Light Requests: {len(authentic_traffic_light_requests)}")
            
            
            
        if number_of_solved_accidents < Settings.MAX_NUMBER_TRAFFIC_ACCIDENTS:
            return False 
        
        return True


    def log(self, objects: Union[SimulationEventManager, ReportManager, EmergencyVehicle]):
                
        if isinstance(objects, EmergencyVehicle) and  len(objects) != 0:
            logger.info(ObjectType.EMERGENCY_VEHICLE, objects.__dict__)
            
        

            
    def toggle_logging_stdout(self, activate=True):
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = logger.add(sys.stdout, filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "accident_handler")
        elif not activate and self._stdout_handler_id is not None:
            logger.remove(self._stdout_handler_id)
            self._stdout_handler_id = None