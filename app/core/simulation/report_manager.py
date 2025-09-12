from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Union, Optional

from core.models.events.simulation_events import VerificationState
from core.models.devices.common import DeviceType
from core.models.uniform.components.object_of_interest import ObjectOfInterest
from core.models.uniform.components.report import SendingPacket
from core.models.uniform.components.report_models import ReportType, ReporterType, Situation
from core.models.uniform.components.reporter import SendersEntity
from core.simulation.logging import ObjectType
from core.simulation.simulation_context import SimulationContext
from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import RequestLifecycleStatus
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentStatus
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters
from utils.simulation import is_object_in_simulation
import utils.logging as logger

from loguru import logger as loguru_logger

if TYPE_CHECKING:
    from core.models.events.simulation_events import SimulationEvent
    from core.models.devices.vehicle import Vehicle
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.device_handler import DevicesGroupHandler

class ReportManager:
    
    def __init__(self, simulation_context : SimulationContext) -> None:
        
        self.context : SimulationContext = simulation_context
        
        self.reports: Dict[int, SendingPacket] = {}
        
        # Cached dictionaries for quick lookups
        self._report_of_object_of_interest_id: Dict[str, SendingPacket] = {}
        self._solved_accidents: Dict[int, SendingPacket] = {}
        self._unsolved_accidents: Dict[int, SendingPacket] = {}
        self._authentic_accident_reports: Dict[int, SendingPacket] = {}
        self._authentic_traffic_lights_requests: Dict[int, SendingPacket] = {}
        self._unauthentic_accident_reports: Dict[int, SendingPacket] = {}
        self._unauthentic_traffic_light_reports: Dict[int, SendingPacket] = {}
        self._reporter_type_by_id: Dict[str, ReporterType] = {}
        self._unsolved_reports: Dict[int, SendingPacket] = {}
        self._unverified_reports_by_situation: Dict[Situation, Dict[int, SendingPacket]] = {
            situation: {} for situation in Situation
        }

        self.context.register_report_provider(self)

    def get_report(self, report_id: int) -> Optional[SendingPacket]:
        """Get a report by its ID."""
        assert isinstance(report_id, int), "Report ID must be an integer."
        if report_id not in self.reports:
            loguru_logger.warning(ObjectType.REPORT.name, f"Report with ID {report_id} not found.")
        return self.reports.get(report_id)




    def add(self, report: SendingPacket) -> None:
        """Add a report and update all relevant caches."""
        
        assert isinstance(report, SendingPacket)
        assert report._id not in self.reports, f"Report with ID {report._id} already exists."
        assert isinstance(report._id, int), "Report ID must be an integer."
        self.reports[report._id] = report
        self._update_caches(report)
        logger.info(ObjectType.REPORT.name, report.get_accident_dict())

    def update(self) -> None:
        """Update report locations and refresh caches for modified reports."""

        vehicles_simulation = self.context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        for report_id, report in self.reports.items():
            if report.situation == Situation.TRAFFIC_PRIORITY_REQUEST:
                if not is_object_in_simulation(report.object_of_interest.object_id):
                    continue
                assert report.object_of_interest.object_id in vehicles_simulation, \
                    f"Vehicle {report.object_of_interest.object_id} not found in simulation."
                assert isinstance(vehicles_simulation[report.object_of_interest.object_id], str), \
                    f"Vehicle {report.object_of_interest.object_id} is not a string."

                vehicle = vehicles_simulation[report.object_of_interest.object_id]
                assert isinstance(vehicle, Vehicle), " Expected Vehicle instance."
                assert isinstance(vehicle._position, tuple) and len(vehicle._position) == 2, " Invalid vehicle position."
                
                report.object_of_interest.location = vehicle._position
                # Recompute caches for updated reports
                self._update_caches(report)

    def _update_caches(self, report: SendingPacket) -> None:
        """Update all cached dictionaries for a given report."""
        # Object of interest cache
        self._report_of_object_of_interest_id[report.object_of_interest.object_id] = report
        assert isinstance(report._id, int), "Report ID must be an integer."
        # Solved and unsolved accidents
        if report.event_status == AccidentStatus.COMPLETE_SOLVED:
            self._solved_accidents[report._id] = report
            self._unsolved_accidents.pop(report._id, None)
        elif report.event_status != AccidentStatus.IGNORE_UNSOLVED:
            self._unsolved_accidents[report._id] = report
            self._solved_accidents.pop(report._id, None)

        # Authentic reports
        if report.request_type == ReportType.EmergencyReport and report.trustworthiness == VerificationState.AUTHENTIC:
            self._authentic_accident_reports[report._id] = report
            self._unauthentic_accident_reports.pop(report._id, None)
        elif report.request_type == ReportType.TraffiCPriorityRequest and report.trustworthiness == VerificationState.AUTHENTIC:
            self._authentic_traffic_lights_requests[report._id] = report
            self._unauthentic_traffic_light_reports.pop(report._id, None)

        # Unauthentic reports
        if report.request_type == ReportType.EmergencyReport and report.trustworthiness == VerificationState.NOT_AUTHENTIC:
            self._unauthentic_accident_reports[report._id] = report
            self._authentic_accident_reports.pop(report._id, None)
        elif report.request_type == ReportType.TraffiCPriorityRequest and report.trustworthiness == VerificationState.NOT_AUTHENTIC:
            self._unauthentic_traffic_light_reports[report._id] = report
            self._authentic_traffic_lights_requests.pop(report._id, None)

        # Unsolved reports
        if report.event_status != AccidentStatus.UNSOLVED:
            self._unsolved_reports[report._id] = report
        else:
            self._unsolved_reports.pop(report._id, None)

        # Unverified reports by situation
        for situation in Situation:
            if report.trustworthiness == VerificationState.UNVERIFIED and report.situation == situation:
                self._unverified_reports_by_situation[situation][report._id] = report
            else:
                self._unverified_reports_by_situation[situation].pop(report._id, None)

        # Reporter type cache
        for reporter_id, _ in report.sending_entities.items():
            self._reporter_type_by_id[reporter_id] = self._get_reporter_type(reporter_id)

    def get_simulation_reports(self) -> Dict[int, SendingPacket]:
        """Return all reports."""
        return self.reports

    def exists(self, vehicle_id: str, traffic_light_id: str) -> bool:
        """Check if a report exists for the given vehicle and traffic light."""
        report = self._report_of_object_of_interest_id.get(vehicle_id)
        return report is not None and report.receiving_entity == traffic_light_id

    def get_report_of_object_of_interest_id(self, object_of_interest_id: str) -> Optional[SendingPacket]:
        """Get report by object of interest ID."""
        return self._report_of_object_of_interest_id.get(object_of_interest_id)

    def get_solved_accidents(self) -> Dict[int, SendingPacket]:
        """Get solved accidents."""
        return self._solved_accidents

    def get_number_of_solved_accidents(self) -> int:
        """Get the count of solved accidents."""
        return len(self._solved_accidents)

    def get_unsolved_accidents(self) -> Dict[int, SendingPacket]:
        """Get unsolved accidents."""
        return self._unsolved_accidents

    def get_number_of_unsolved_accidents(self) -> int:
        """Get the count of unsolved accidents."""
        return len(self._unsolved_accidents)

    def get_authentic_accident_reports(self) -> Dict[int, SendingPacket]:
        """Get authentic accident reports."""
        return self._authentic_accident_reports

    def get_authentic_traffic_lights_requests(self) -> Dict[int, SendingPacket]:
        """Get authentic traffic light requests."""
        return self._authentic_traffic_lights_requests

    def get_unauthentic_accident_reports(self) -> Dict[int, SendingPacket]:
        """Get unauthentic accident reports."""
        return self._unauthentic_accident_reports

    def get_unauthentic_traffic_light_reports(self) -> Dict[int, SendingPacket]:
        """Get unauthentic traffic light reports."""
        return self._unauthentic_traffic_light_reports

    def get_reporter_type(self, reporter_id: str) -> ReporterType:
        """Get reporter type by ID, using cache."""
        assert isinstance(reporter_id, str), "Reporter ID must be a string."
        return self._reporter_type_by_id.get(reporter_id, self._get_reporter_type(reporter_id))
        
    def _get_reporter_type(self, reporter_id: str) -> ReporterType:
        """Determine reporter type based on device metadata."""
        
        device = self.context._device_registry.get_device(reporter_id)
        if device and device._type in {DeviceType.VEHICLE, DeviceType.EMERGENCY_VEHICLE}:
            return ReporterType.VEHICLE
        return ReporterType.PEDESTRIAN

    def get_unsolved_reports(self) -> Dict[int, SendingPacket]:
        """Get unsolved reports."""
        return self._unsolved_reports

    def get_unverified_reports_by_situation(self, situation: Situation) -> Dict[int, SendingPacket]:
        """Get unverified reports for a specific situation."""
        return self._unverified_reports_by_situation.get(situation, {})

    def get_reports_by_type(self, report_type: ReportType) -> Dict[int, SendingPacket]:
        """Get reports by type."""
        return {
            k: v for k, v in self.reports.items()
            if v.request_type == report_type
        }

    def create_report(
        self,
        reporters: Dict[str, SendersEntity],
        event: SimulationEvent,
        object_of_interest: Vehicle,
        receiver: Union[EmergencyResponseCenter, TrafficLightSystem],
        report_type: ReportType
    ) -> SendingPacket:
        """Create and add a new report."""
        created_reporters = self.create_reporters(reporters, event)
        assert isinstance(object_of_interest._position, tuple) and len(object_of_interest._position) == 2, "Invalid vehicle position."
        
        object_of_interest_data = ObjectOfInterest(
            object_id=object_of_interest._id,
            location=object_of_interest._position,
            edge_id=object_of_interest._edge_id,
            lane_position=object_of_interest._lane_position,
            lane_id=object_of_interest._lane_id
        )
        
        situation = (
            Situation.EMERGENCY_REPORT if report_type == ReportType.EmergencyReport
            else Situation.TRAFFIC_PRIORITY_REQUEST
        )
        report_status = (
            AccidentStatus.UNSOLVED if report_type == ReportType.EmergencyReport
            else RequestLifecycleStatus.PENDING
        )

        report = SendingPacket(
            time=self.context._current_time,
            receiver=receiver,
            sending_entities=created_reporters,
            situation=situation,
            object_of_interest=object_of_interest_data,
            type=report_type,
            report_status=report_status,
            simulation_event=event
        )
        
        self.add(report)
        for reporter_id, reporter in report.sending_entities.items():
            reporter.draw_reporter_location(reporter.authenticity)
                
        return report

    def create_reporters(self, filtered_reporters: Dict[str, SendersEntity], event: SimulationEvent) -> Dict[str, SendersEntity]:
        """Create reporters and draw their locations."""
        reporters: Dict[str, SendersEntity] = {}
        for reporter_id, reporter in filtered_reporters.items():
            reporter.draw_reporter_location(reporter.authenticity)
            reporters[reporter_id] = reporter
        return reporters



# from __future__ import annotations
# from typing import TYPE_CHECKING
# from core.models.devices.device_handler import DevicesGroupHandler
# from core.models.events.simulation_events import VerificationState
# from core.models.devices.common import DeviceType


# from core.models.reports.components.object_of_interest import ObjectOfInterest
# from core.models.reports.components.report import SendingPacket
# from core.models.reports.components.report_models import ReportType, ReporterType, Situation
# from core.models.reports.components.reporter import SendersEntity


# from core.simulation.logging import ObjectType
# from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import RequestLifecycleStatus


# if TYPE_CHECKING:
#     from core.models.events.simulation_events import SimulationEvent
#     from core.models.devices.vehicle import Vehicle
#     from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
#     from core.models.devices.traffic_light import TrafficLightSystem

# from utils.simulation import is_object_in_simulation

# from typing import Dict, Union
# from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentStatus
# from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

# import utils.logging as logger


            
    
# class ReportManager:
    
#     reports : Dict[str, SendingPacket]  = {}

#     def __init__(self) -> None:
#         self.reports : Dict[str, SendingPacket] = {}
        
#     def get_simulation_reports(self) -> Dict[str, SendingPacket]:
#         return self.reports

#     def exists(self,vehicle_id: str, traffic_light_id: str) -> bool:
#         for report in self.reports.values():
            
            
#             if report.object_of_interest.object_id == vehicle_id and report.receiving_entity == traffic_light_id:
#                 return True

#         return False
    
    
#     def add(self, report: SendingPacket):
        
#         self.reports[report.report_id] = report

#     def update(self):
        
        
#         vehicles_simulation = DevicesGroupHandler().get_devices_by_group(DeviceType.VEHICLE)
        
#         for report_id, report in self.reports.items():
            
#             if report.situation == Situation.TRAFFIC_PRIORITY_REQUEST:
                
#                 if not is_object_in_simulation(report.object_of_interest.object_id):
#                     continue
                    
                    
                
#                 report.object_of_interest.location = vehicles_simulation[report.object_of_interest.object_id]._position
    
#     def get_report(self, object_of_interest_id: str) -> SendingPacket:
        
#         for report_id, report in self.reports.items():
            
#             if report.object_of_interest.object_id == object_of_interest_id:
#                 return report
    
#     def get_number_of_solved_accdients(self) -> int:
        
#         solved_acciednets = {k:v for (k,v) in self.reports.items() if v.event_status == AccidentStatus.COMPLETE_SOLVED}
        
        
#         return len(solved_acciednets)
      
#     def get_number_of_unsolved_accidents(self) -> int:
        
#         # accidents = emergency_center.accident_manager.get_all()
        
        
#         unsolved_acciednets = {k:v for (k,v) in self.reports.items() if v.event_status != AccidentStatus.IGNORE_UNSOVLED}
        
        
#         return len(unsolved_acciednets)
     
    
#     def get_reports_by_type(self, report_type : ReportType) -> Dict[str, SendingPacket]:
        
#         reports = {k:v for (k,v) in self.reports.items() if v.request_type == report_type}
        
#         return reports
            
#     def get_authentic_reports_by_type(self, report_type: ReportType) -> Dict[str, SendingPacket]:
    
#         reports = {k:v for (k,v) in self.reports.items() if v.request_type == report_type and v.trustworthiness == VerificationState.AUTHENTIC}
        
#         return reports
    
#     def get_unauthentic_reports_by_type(self, report_type: ReportType) -> Dict[str, SendingPacket]:
    
#         reports = {k:v for (k,v) in self.reports.items() if v.request_type == report_type and v.trustworthiness == VerificationState.NOT_AUTHENTIC}
        
#         return reports
    
#     def get_unsolved_accidents(self) -> Dict[str, SendingPacket]:
        
#         # accidents = emergency_center.accident_manager.get_all()
        
        
#         unsolved_acciednets = {k:v for (k,v) in self.reports.items() if v.event_status != AccidentStatus.UNSOLVED}
        
        
#         return unsolved_acciednets
    
#     def get_reporter_type(self, reporter_id: str) -> ReporterType:
        
#         for report_id, report in self.reports.items():
            
            
#             if reporter_id.startswith("ped"):
#                 return ReporterType.PEDESTRIAN
            
#             elif reporter_id.startswith("bike"):
#                 return ReporterType.VEHICLE
            
#             elif reporter_id.startswith("veh"):
#                 return ReporterType.VEHICLE
            
#             elif reporter_id.startswith("bus"):
#                 return ReporterType.VEHICLE
            
#             elif reporter_id.startswith("truck"):
#                 return ReporterType.VEHICLE
#             elif reporter_id.startswith("moto"):
#                 return ReporterType.VEHICLE
            
            
#             else:
#                 return ReporterType.VEHICLE
                
#     def get_unverified_reports(self) -> Dict[str, SendingPacket]:
        
#         unverified_reports = {k:v for (k,v) in self.reports.items() if v.trustworthiness == VerificationState.UNVERIFIED}
        
#         return unverified_reports
    
#     def get_unverified_reports_by_situation(self, situation: Situation) -> Dict[str, SendingPacket]:

        
#         unverified_reports = {k:v for (k,v) in self.reports.items() if v.trustworthiness == VerificationState.UNVERIFIED and v.situation == situation}
        
#         return unverified_reports
     
#     def create_report(self, reporters : Dict[str,SendersEntity], event: SimulationEvent, object_of_interest: Vehicle, receiver : Union[EmergencyResponseCenter,TrafficLightSystem], report_type : ReportType):



#         created_reporters = self.create_reporters(reporters, event)
#         object_of_interest = ObjectOfInterest(object_id=object_of_interest._id, location=object_of_interest._position,
#                                             edge_id=object_of_interest._edge_id, lane_position=object_of_interest._lane_position,
#                                             lane_id=object_of_interest._lane_id)
        
#         situation : Situation = None
        
#         if report_type == ReportType.EmergencyReport:
#             situation = Situation.EMERGENCY_REPORT
#             report_status = AccidentStatus.UNSOLVED
#         elif report_type == ReportType.TraffiCPriorityRequest:
#             situation = Situation.TRAFFIC_PRIORITY_REQUEST
#             report_status =  RequestLifecycleStatus.PENDING
                
#         report = SendingPacket(time=ScenarioParameters.TIME,
#                     receiver=receiver,
#                     sending_entities=created_reporters,
#                     situation=situation,
#                     object_of_interest=object_of_interest,
#                     type=report_type,
#                     report_status=report_status,
#                     simulation_event=event)
        
        
#         report_message = report.get_accident_dict()
        
#         try:
#             logger.info(ObjectType.REPORT,report_message)
#         except Exception as e:
#             logger.error(ObjectType.REPORT, e.__dict__)
        
#         for reporter_id, reporter in report.sending_entities.items():
#             reporter.draw_reporter_location(reporter.authenticity)
                
#         return report
        
#     def create_reporters(self,filtered_reporters : Dict[str, SendersEntity],  event : SimulationEvent) -> Dict[str,SendersEntity]:
        
#         reporters : Dict[str, SendersEntity] = {}
        
        
#         for reporter_id, reporter in filtered_reporters.items():
            
#             # reporter_type = self.get_reporter_type(reporter_id)
#             # reporter = ReporterObject(reporter_id, reporter_object.location , reporter_type)
#             reporter.draw_reporter_location(reporter.authenticity)
#             reporters[reporter_id] = reporter
            
#         return reporters
    
            
