from __future__ import annotations
import re
from typing import TYPE_CHECKING, Dict






from core.models.events.simulation_events import EventRecord, EventState, SimulationEventManager, VerificationState



from core.models.services.base_service import BaseService
from core.models.uniform.components.report_models import ReportType, Situation
from core.simulation.event_bus.base_event import CollisionDetectionEvent
from core.simulation.report_manager import ReportManager
from experiments.settings import Settings
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

import trust.trust_request_management_unit.request_management_unit as request_management
from core.models.interfaces.service import IService

if TYPE_CHECKING:

    from core.models.devices.induction_loop import InductionLoop
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.traffic_light import TrafficLightSystem
    from core.models.devices.vehicle import Vehicle
    from core.models.uniform.components.report import SendingPacket
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
    


class EmergencyReportManagementService(BaseService):

    def __init__(self):

        assert self.simulation_context is not None, "Simulation context is None"
        self.simulation_context.get_event_bus().subscribe(CollisionDetectionEvent, self._handle_collision_detection_event)

    def get(self, device: SmartPhone | Vehicle | EmergencyVehicle | InductionLoop | TrafficCamera | TrafficLightSystem | EmergencyResponseCenter) -> Dict[str, SmartPhone | Vehicle | EmergencyVehicle | InductionLoop | TrafficCamera | TrafficLightSystem | EmergencyResponseCenter]:
        
        return super().get(device) # type: ignore
    
    
    def update(self, *args, **kwargs):
        
        self.handle_unverified_requests(*args, **kwargs)


        # Handle accident reports that have been verified
        self.process_unverified_accident_reports()

        
        self.handle_verified_report(*args, **kwargs)

        return super().update(*args, **kwargs)

    
    def _handle_collision_detection_event(self, event: CollisionDetectionEvent):
        pass
    
    
    def process_unverified_accident_reports(self):
        
        assert self.simulation_context is not None, "Simulation context is None"
        assert self.simulation_context._report_provider is not None, "Report provider is None"
        unverified_reports = self.simulation_context._report_provider.get_unverified_reports_by_situation(Situation.EMERGENCY_REPORT)

        accident_report: SendingPacket
        
        for id, accident_report in unverified_reports.items():
            if not self.is_emergency_report(accident_report):
                continue


            if not Settings.VERIFY_ACCIDENT_REPORT_AUTHENTICITY:
                accident_report.trustworthiness = VerificationState.AUTHENTIC
    

    def handle_verified_report(self,accident_report : SendingPacket, simulation_event_mananger : SimulationEventManager):
        if accident_report.trustworthiness == VerificationState.AUTHENTIC:
            self.update_event_state(accident_report, simulation_event_mananger)
            accident_report.receiving_entity.trust_manager.update_request_status(accident_report)

            # TODO: Log DECISION-MAKING
            # accident_report.update_status

        elif accident_report.trustworthiness == VerificationState.NOT_AUTHENTIC:
            self.update_event_state(accident_report, simulation_event_mananger)
            accident_report.receiving_entity.trust_manager.update_request_status(accident_report)

        elif accident_report.trustworthiness == VerificationState.NOT_VERIFIABLE:
            pass


    def update_event_state(self,accident_report : SendingPacket, simulation_event_mananger : SimulationEventManager):
        event_record = EventRecord(
            accident_report.simulation_event.id,
            EventState.VERIFIED,
            ScenarioParameters.TIME,
            accident_report.object_of_interest.location
        )
        simulation_event_mananger.get_event_by_id(accident_report.simulation_event.id)._update_state(event_record)



    def is_emergency_report(self,accident_report: SendingPacket):
        return accident_report.request_type == ReportType.EmergencyReport

    def handle_unverified_requests(self, report: SendingPacket, simulation_event_mananger: SimulationEventManager):
        if not (report.trustworthiness == VerificationState.UNVERIFIED or report.trustworthiness == VerificationState.NOT_VERIFIABLE):
            return
        
        trust_decision = request_management.send_trust_request(self.trustor, report)
        report.trustworthiness = trust_decision
        return trust_decision
        