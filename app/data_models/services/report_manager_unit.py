from __future__ import annotations
from typing import TYPE_CHECKING


from data_models.report_management.report.report_models import ReportType


from data_models.events.simulation_events import EventRecord, EventState, SimulationEventManager, VerificationState



from data.simulation.scenario_constants import Constants as sc

import trust_management.trust_request_management_unit.request_management_unit as request_management

if TYPE_CHECKING:
    from data_models.iot_devices.device_handler import Devices_Group_Handler
    from data_models.report_management.report.report import SendingPacket
    from data_models.iot_devices.genric_iot_device import GenericDevice
    


class ReportManagementComponent:

    def __init__(self, trustor : GenericDevice,  devices=None):
        self.devices : Devices_Group_Handler = devices
        self.trustor = trustor

    def is_emergency_report(self,accident_report: SendingPacket):
        return accident_report.request_type == ReportType.EmergencyReport

    def handle_verified_report(self,accident_report : SendingPacket, simulation_event_mananger : SimulationEventManager):
        if accident_report.trustworthiness == VerificationState.AUTHENTIC:
            self.update_event_state(accident_report, simulation_event_mananger)
            accident_report.receiving_entity.trust_manager.update_request_status(accident_report)

            # TODO: Log DECISION-MAKING
            # accident_report.update_status

        elif accident_report.trustworthiness == VerificationState.NOT_AUTHENTIC:
            self.update_event_state(accident_report, simulation_event_mananger)
            accident_report.receiving_entity.trust_manager.update_request_status(accident_report)

        elif accident_report.trustworthiness == VerificationState.NOT_VERIFIEDABLE:
            pass


    def update_event_state(self,accident_report : SendingPacket, simulation_event_mananger : SimulationEventManager):
        event_record = EventRecord(
            accident_report.simulation_event.id,
            EventState.VERIFIED,
            sc.TIME,
            accident_report.object_of_interest.location
        )
        simulation_event_mananger.simulation_events[accident_report.simulation_event.id].update_state(event_record)

    def is_emergency_report(self,accident_report: SendingPacket):
        return accident_report.request_type == ReportType.EmergencyReport

    def handle_unverified_requests(self, report: SendingPacket, simulation_event_mananger: SimulationEventManager):
        if not (report.trustworthiness == VerificationState.UNVERIFIED or report.trustworthiness == VerificationState.NOT_VERIFIEDABLE):
            return
        
        trust_decision = request_management.send_trust_request(self.trustor, report)
        report.trustworthiness = trust_decision
        return trust_decision
        