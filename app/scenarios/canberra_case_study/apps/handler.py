import sys
from typing import Dict, List, Union
from core.models.uniform.components.report_models import ReportType, Situation
from core.models.uniform.components.object_of_interest import ObjectOfInterest 
from core.models.uniform.components.report import SendingPacket
from core.simulation.report_manager import ReportManager

from core.models.events.simulation_events import EventRecord, EventState, EventType, SimulationEvent, SimulationEventManager, VerificationState



from core.simulation.environment import disable_accident_behaviour, enable_accident_behaviour
from core.simulation.logging import ObjectType
from core.simulation.simulation_context import SimulationContext
from experiments.settings import Settings
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentStatus

from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle

from traci import simulation,vehicle 
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters 
from utils import convert
import utils.logging as logger

from loguru import logger as loguru_logger


class ScenarioHandler:
    """Manages scenario-level logic for accidents and events"""
    
    def __init__(self, context: SimulationContext):
        self.context = context
        self._logger = loguru_logger.bind(context="scenario_handler")
        self._stdout_handler_id = None


        self.simulation_event_manager = self.context._simulation_event_manager
        self.device_manager = self.context._device_registry
        self.report_manager = self.context._report_provider


    def update_events(self, simulation_event_manager: SimulationEventManager) -> None:
        """Update the state of collision events"""
        
        
        
        accident_events = simulation_event_manager.get_events_by_type(EventType.COLLISION)
        
        for event_id, event in accident_events.items():
            if event.state == EventState.TRIGGERED and event.is_authentic:
                enable_accident_behaviour(event)
                event._update_state(EventRecord(
                    event_id=event.id, 
                    state=EventState.ONGOING, 
                    time=ScenarioParameters.TIME, 
                    location=event.location
                ))
            
            elif event.state == EventState.ONGOING and (ScenarioParameters.TIME - float(event.time)) > 900:
                event._update_state(EventRecord(
                    event_id=event.id, 
                    state=EventState.ONGOING_15_MIN, 
                    time=ScenarioParameters.TIME, 
                    location=event.location
                ))

    def update_accidents(self, report_manager: ReportManager) -> None:
        """Update the status of accident reports"""
        for accident_id, accident_report in report_manager.reports.items():
            if accident_report.event_status == AccidentStatus.IGNORE_UNSOLVED:
                disable_accident_behaviour(accident_report, color=(0, 0, 255, 255))
            elif accident_report.event_status == AccidentStatus.ACCIDENT_SOLVED and accident_report.simulation_event.is_authentic:
                disable_accident_behaviour(accident_report, color=(0, 255, 0, 255))

    def get_solved_accidents(self, accident_reports: Dict[int, 'SendingPacket'], event_manager: SimulationEventManager) -> int:
        """Count the number of solved authentic accidents"""
        solved_accidents = 0
        collision_events = event_manager.get_authentic_events_by_type(EventType.COLLISION)
        
        for accident_id, accident_report in accident_reports.items():
            ground_truth = collision_events.get(accident_report.simulation_event.id)
            if (ground_truth and ground_truth.is_authentic and 
                accident_report.trustworthiness == VerificationState.AUTHENTIC and
                accident_report.event_status == AccidentStatus.COMPLETE_SOLVED):
                solved_accidents += 1
                
        return solved_accidents

    def is_finished(self, report_manager: ReportManager, event_manager: SimulationEventManager) -> bool:
        """Check if the simulation is finished based on solved accidents"""
        if len(report_manager.reports) <= 2:
            return False
        
        accident_reports = report_manager.get_reports_by_type(ReportType.EmergencyReport)
        solved_accidents = self.get_solved_accidents(accident_reports, event_manager)
        
        self._log_simulation_status(report_manager, solved_accidents)
        
        return solved_accidents >= Settings.MAX_NUMBER_TRAFFIC_ACCIDENTS

    def _log_simulation_status(self, report_manager: ReportManager, solved_accidents: int) -> None:
        """Log the current simulation status"""
        if ScenarioParameters.TIME % 50 != 0:
            return
        
        authentic_accidents = self.report_manager.get_authentic_accident_reports()
        authentic_traffic_requests = self.report_manager.get_authentic_traffic_lights_requests()
        unverified_accidents = self.report_manager.get_unverified_reports_by_situation(Situation.EMERGENCY_REPORT)
        unverified_traffic_requests = self.report_manager.get_unverified_reports_by_situation(Situation.TRAFFIC_PRIORITY_REQUEST)
        unauthentic_accidents = self.report_manager.get_unauthentic_accident_reports()
        unauthentic_traffic_requests = self.report_manager.get_unauthentic_traffic_light_reports()
        
        self._logger.info(
            f"{ScenarioParameters.TIME} | Solved: {solved_accidents} | "
            f"Unverified Acc: {len(unverified_accidents)} | Unauthentic Acc: {len(unauthentic_accidents)} | "
            f"Authentic Acc: {len(authentic_accidents)} | Unverified Traffic: {len(unverified_traffic_requests)} | "
            f"Unauthentic Traffic: {len(unauthentic_traffic_requests)} | Authentic Traffic: {len(authentic_traffic_requests)}"
        )

    def log(self, objects: Union[SimulationEventManager, ReportManager, EmergencyVehicle]) -> None:
        """Log information about specified objects"""
        if isinstance(objects, EmergencyVehicle) and len(objects) != 0:
            loguru_logger.info(ObjectType.EMERGENCY_VEHICLE.name, objects.__dict__)

    def toggle_logging_stdout(self, activate: bool = True) -> None:
        """Toggle stdout logging for scenario events"""
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = loguru_logger.add(
                sys.stdout, 
                filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "scenario_handler"
            )
        elif not activate and self._stdout_handler_id is not None:
            loguru_logger.remove(self._stdout_handler_id)
            self._stdout_handler_id = None
            
            

# class ScenarioHandler:

#     def __init__(self, context : SimulationContext) -> None:
        
#         self._logger = logurulogger.bind(context="scenario_handler")
#         self._stdout_handler_id = None
#         self.context = context
        
#         self._register_scenario_hanlder(self)


#     def update_events(self, self.simulation_event_manager : SimulationEventManager):



#         accident_events : Dict[str,SimulationEvent] = self.simulation_event_manager.get_events_by_type(EventType.COLLISION)

#         for event_id, event in accident_events.items():

#             if event.state == EventState.TRIGGERED and event.is_authentic:
                
#                 enable_accident_behaviour(event)
#                 event_record: EventRecord = EventRecord(event.id, EventState.ONGOING, ScenarioParameters.TIME, event.location)
#                 event._update_state(event_record)
                    
#             elif event.state == EventState.ONGOING and (ScenarioParameters.TIME - float(event.time)) > 900:
#                 event_record: EventRecord = EventRecord(event.id, EventState.ONGOING_15_MIN, ScenarioParameters.TIME, event.location)
#                 event._update_state(event_record)
            
#             elif event.state == EventState.REPORTED:
#                 pass
            
#             elif event.state == EventState.SOLVED:
#                 pass
            
#             elif event.state == EventState.ONGOING:
#                 pass 


#     def update_accidents(self, report_manager: ReportManager):
        
#         for accident_id, accident_report in report_manager.reports.items():
#             if accident_report.event_status == AccidentStatus.IGNORE_UNSOLVED:
#                 disable_accident_behaviour(accident_report,color=(0,0,255,255))
                
#             elif accident_report.event_status == AccidentStatus.ACCIDENT_SOLVED and accident_report.simulation_event.is_authentic:
#                 disable_accident_behaviour(accident_report, color=(0, 255, 0, 255))



#     def get_solved_accidents(self, accident_reports : Dict[str,SendingPacket], event_manager : SimulationEventManager):
        
#         solved_accidents = 0
#         collision_events = event_manager.get_authentic_events_by_type(EventType.COLLISION)
        
#         for accident_id, accident_report in accident_reports.items():
            
#             ground_truth = collision_events[accident_report.simulation_event.id]
            
#             if not (ground_truth.is_authentic == True and accident_report.trustworthiness == VerificationState.AUTHENTIC):
#                 continue
            
#             if accident_report.event_status == AccidentStatus.COMPLETE_SOLVED:
#                 solved_accidents += 1
                
#         return solved_accidents


#     def is_finished(self, report_manager: ReportManager, event_manager: SimulationEventManager):
        
        
#         if len(report_manager.reports) <= 2:
#             return False

#         accidnet_reports = report_manager.get_reports_by_type(ReportType.EmergencyReport)
#         number_of_solved_accidents = self.get_solved_accidents(accidnet_reports,event_manager)
        
        
#         authentic_accidnets = report_manager.get_authentic_reports_by_type(ReportType.EmergencyReport)
#         authentic_traffic_light_requests = report_manager.get_authentic_reports_by_type(ReportType.TraffiCPriorityRequest)
        
        
#         unverified_accidents = report_manager.get_unverified_reports_by_situation(Situation.EMERGENCY_REPORT)
#         unverfied_traffic_light_requests = report_manager.get_unverified_reports_by_situation(Situation.TRAFFIC_PRIORITY_REQUEST)
        
#         unauthentic_accidnets = report_manager.get_unauthentic_reports_by_type(ReportType.EmergencyReport)
#         unauthentic_traffic_light_requests = report_manager.get_unauthentic_reports_by_type(ReportType.TraffiCPriorityRequest)
        
        
        
        
        
#         if ScenarioParameters.TIME % 50 == 0:
#             self._logger.info(f"{ScenarioParameters.TIME} \t | Solved Accidents: {number_of_solved_accidents}  \t | Unverified Accidents: {len(unverified_accidents)} \t | Unauthentic Accidents: {len(unauthentic_accidnets)} \t | Authentic Accidents: {len(authentic_accidnets)} \t | Unverified Traffic Light Requests: {len(unverfied_traffic_light_requests)} \t | Unauthentic Traffic Light Requests: {len(unauthentic_traffic_light_requests)} \t | Authentic Traffic Light Requests: {len(authentic_traffic_light_requests)}")
            
            
            
#         if number_of_solved_accidents < Settings.MAX_NUMBER_TRAFFIC_ACCIDENTS:
#             return False 
        
#         return True


#     def log(self, objects: Union[SimulationEventManager, ReportManager, EmergencyVehicle]):
                
#         if isinstance(objects, EmergencyVehicle) and  len(objects) != 0:
#             logger.info(ObjectType.EMERGENCY_VEHICLE, objects.__dict__)
            
        

            
#     def toggle_logging_stdout(self, activate=True):
#         if activate and self._stdout_handler_id is None:
#             self._stdout_handler_id = logger.add(sys.stdout, filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "accident_handler")
#         elif not activate and self._stdout_handler_id is not None:
#             logger.remove(self._stdout_handler_id)
#             self._stdout_handler_id = None