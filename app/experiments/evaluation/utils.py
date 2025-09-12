from __future__ import annotations
from typing import TYPE_CHECKING, Dict
import sys

from typing import Dict
from core.models.uniform.components.report_models import ReportType, Situation
from core.models.events.simulation_events import EventType, SimulationEvent, VerificationState


if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket
    from core.simulation.report_manager import ReportManager





def get_reports_and_events(reports: Dict[str, SendingPacket], events: Dict[str,SimulationEvent], reportType: ReportType, situation: EventType):

    reports_of_interest = {}
    events_of_interest = {}

    report_id: str
    report: SendingPacket
    
    for report_id, report in reports.items():

        if report.request_type == reportType and (report.trustworthiness == VerificationState.AUTHENTIC or report.trustworthiness == VerificationState.NOT_AUTHENTIC):
            reports_of_interest[report_id] = report

    for event_id, event in events.items():

        if event.situation == situation:

            events_of_interest[event.id] = event

    return reports_of_interest, events_of_interest



def print_unverified_reports(report_manager : ReportManager, situation : Situation):
    
    unverfied_reports = report_manager.get_unverified_reports_by_situation(situation)
    
    print(f"Unverified Reports of {situation.name}: " + str(len(unverfied_reports)))
