
from __future__ import annotations
from typing import TYPE_CHECKING
from data_models.events.simulation_events import VerificationState
from data_models.iot_devices.common import DeviceType
from data_models.report_management.report.report_models import ReportType, ReporterType, Situation




from data_models.simulation.logging import ObjectType

import data_models.iot_devices.device_handler as device_handler
from scenario.intelligent_traffic_light.constants import RequestLifecycleStatus


if TYPE_CHECKING:
    from data_models.events.simulation_events import SimulationEvent
    from data_models.iot_devices.vehicle import Vehicle
    from scenario.emergency_response.emergency_response import EmergencyResponseCenter
    from data_models.iot_devices.traffic_light import TrafficLightSystem

    from data_models.report_management.report.reporter import SendersEntity
    
from data_models.report_management.report.object_of_interest import ObjectOfInterest
from utils.simulation import is_object_in_simulation
from data_models.report_management.report.report import  SendingPacket
from typing import Dict, Union
from scenario.emergency_response.constants import AccidentStatus
from data.simulation.scenario_constants import Constants as sc

import utils.logging as logger


            
    
class ReportManager:
    
    reports : Dict[str, SendingPacket]  = {}

    def __init__(self, devices) -> None:
        self.reports : Dict[str, SendingPacket] = {}
        self.devices = devices
        pass

    def get_simulation_reports(self) -> Dict[str, SendingPacket]:
        return self.reports

    def exists(self,vehicle_id: str, traffic_light_id: str) -> bool:
        for report in self.reports.values():
            
            
            if report.object_of_interest.object_id == vehicle_id and report.receiving_entity == traffic_light_id:
                return True

        return False
    
    
    def add(self, report: SendingPacket):
        
        self.reports[report.report_id] = report

    def update(self):
        
        devices: device_handler.Devices_Group_Handler = device_handler.get_devices_group_handler()
        vehicles_simulation = devices.get(DeviceType.VEHICLE).all()
        
        for report_id, report in self.reports.items():
            
            if report.situation == Situation.TRAFFIC_PRIORITY_REQUEST:
                
                if not is_object_in_simulation(report.object_of_interest.object_id):
                    continue
                    
                    
                
                report.object_of_interest.location = vehicles_simulation[report.object_of_interest.object_id]._position
    
    
    def get_report(self, object_of_interest_id: str) -> SendingPacket:
        
        for report_id, report in self.reports.items():
            
            if report.object_of_interest.object_id == object_of_interest_id:
                return report
    
    
    
    def get_number_of_solved_accdients(self) -> int:
        
        solved_acciednets = {k:v for (k,v) in self.reports.items() if v.event_status == AccidentStatus.COMPLETE_SOLVED}
        
        
        return len(solved_acciednets)
    
    

    def get_number_of_unsolved_accidents(self) -> int:
        
        # accidents = emergency_center.accident_manager.get_all()
        
        
        unsolved_acciednets = {k:v for (k,v) in self.reports.items() if v.event_status != AccidentStatus.IGNORE_UNSOVLED}
        
        
        return len(unsolved_acciednets)
    
    
    
    def get_reports_by_type(self, report_type : ReportType) -> Dict[str, SendingPacket]:
        
        reports = {k:v for (k,v) in self.reports.items() if v.request_type == report_type}
        
        return reports
            
    def get_authentic_reports_by_type(self, report_type: ReportType) -> Dict[str, SendingPacket]:
    
        reports = {k:v for (k,v) in self.reports.items() if v.request_type == report_type and v.trustworthiness == VerificationState.AUTHENTIC}
        
        return reports
    
    
    def get_unauthentic_reports_by_type(self, report_type: ReportType) -> Dict[str, SendingPacket]:
    
        reports = {k:v for (k,v) in self.reports.items() if v.request_type == report_type and v.trustworthiness == VerificationState.NOT_AUTHENTIC}
        
        return reports

    
    
    def get_unsolved_accidents(self) -> Dict[str, SendingPacket]:
        
        # accidents = emergency_center.accident_manager.get_all()
        
        
        unsolved_acciednets = {k:v for (k,v) in self.reports.items() if v.event_status != AccidentStatus.UNSOLVED}
        
        
        return unsolved_acciednets
    
    def get_reporter_type(self, reporter_id: str) -> ReporterType:
        
        for report_id, report in self.reports.items():
            
            
            if reporter_id.startswith("ped"):
                return ReporterType.PEDESTRIAN
            
            elif reporter_id.startswith("bike"):
                return ReporterType.VEHICLE
            
            elif reporter_id.startswith("veh"):
                return ReporterType.VEHICLE
            
            elif reporter_id.startswith("bus"):
                return ReporterType.VEHICLE
            
            elif reporter_id.startswith("truck"):
                return ReporterType.VEHICLE
            elif reporter_id.startswith("moto"):
                return ReporterType.VEHICLE
            
            
            else:
                return ReporterType.VEHICLE
            
    
    def get_unverified_reports(self) -> Dict[str, SendingPacket]:
        
        unverified_reports = {k:v for (k,v) in self.reports.items() if v.trustworthiness == VerificationState.UNVERIFIED}
        
        return unverified_reports
    
    def get_unverified_reports_by_situation(self, situation: Situation) -> Dict[str, SendingPacket]:

        
        unverified_reports = {k:v for (k,v) in self.reports.items() if v.trustworthiness == VerificationState.UNVERIFIED and v.situation == situation}
        
        return unverified_reports
    
    
    def create_report(self, reporters : Dict[str,SendersEntity], event: SimulationEvent, object_of_interest: Vehicle, receiver : Union[EmergencyResponseCenter,TrafficLightSystem], report_type : ReportType):



        created_reporters = self.create_reporters(reporters, event)
        object_of_interest = ObjectOfInterest(object_id=object_of_interest._id, location=object_of_interest._position,
                                            edge_id=object_of_interest._edge_id, lane_position=object_of_interest._lane_position,
                                            lane_id=object_of_interest._lane_id)
        
        situation : Situation = None
        
        if report_type == ReportType.EmergencyReport:
            situation = Situation.EMERGENCY_REPORT
            report_status = AccidentStatus.UNSOLVED
        elif report_type == ReportType.TraffiCPriorityRequest:
            situation = Situation.TRAFFIC_PRIORITY_REQUEST
            report_status =  RequestLifecycleStatus.PENDING
                
        report = SendingPacket(time=sc.TIME,
                    receiver=receiver,
                    sending_entities=created_reporters,
                    situation=situation,
                    object_of_interest=object_of_interest,
                    type=report_type,
                    report_status=report_status,
                    simulation_event=event)
        
        
        report_message = report.get_accident_dict()
        
        try:
            logger.info(ObjectType.REPORT,report_message)
        except Exception as e:
            logger.error(ObjectType.REPORT, e.__dict__)
        
        for reporter_id, reporter in report.sending_entities.items():
            reporter.draw_reporter_location(reporter.authenticity)
                
        return report
        
        
        
    
    def create_reporters(self,filtered_reporters : Dict[str, SendersEntity],  event : SimulationEvent) -> Dict[str,SendersEntity]:
        
        reporters : Dict[str, SendersEntity] = {}
        
        
        for reporter_id, reporter in filtered_reporters.items():
            
            # reporter_type = self.get_reporter_type(reporter_id)
            # reporter = ReporterObject(reporter_id, reporter_object.location , reporter_type)
            reporter.draw_reporter_location(reporter.authenticity)
            reporters[reporter_id] = reporter
            
        return reporters
    
            
