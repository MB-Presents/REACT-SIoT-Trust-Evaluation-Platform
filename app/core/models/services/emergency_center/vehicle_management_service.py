
from __future__ import annotations
from typing import TYPE_CHECKING, Dict

import traci

from core.models.devices.common import DeviceType
from core.models.devices.device_handler import DevicesGroupHandler
from core.models.services.base_service import BaseService
from core.simulation.simulation_adapter import SimulationAdapter
from core.utils.log_util import LoggingUtil
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyReportRecord
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings, AccidentStatus, EmergencyVehicleStatus
from scenarios.canberra_case_study.apps.emergency_response.utils import log_status
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket
    from core.simulation.report_manager import ReportManager
    from core.models.devices.vehicle import Vehicle

from typing import Any
from core.models.interfaces.service import IService



if TYPE_CHECKING:
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle


class EmergencyManagementService(BaseService):
        
        
        
    def __init__(self) -> None:
        self.simulation_adapter = SimulationAdapter()
        self.logger = LoggingUtil()
        
        self.report_manager: ReportManager = ReportManager(self.devices)
        

        
        # self.emergency_vehicles : Dict[str, EmergencyVehicle] 

    def update(self, *args: Any, **kwargs: Any) -> None:
        
        authentic_accident_reports : Dict[str, SendingPacket] = self.report_manager.get_authentic_accident_reports()  
        
        for _, accident in authentic_accident_reports.items():

            accident_status = accident.event_status
            if accident_status == AccidentStatus.UNSOLVED:
                self.assign_emergency_vehicle(accident)
            elif accident_status == AccidentStatus.IN_PROGRESS:
                self.observe_emergency_response(accident)
            elif accident_status == AccidentStatus.ACCIDENT_SOLVED:
                self.handle_arrival_at_accident(accident)
            elif accident_status == AccidentStatus.IN_PROGRESS_HOSPITAL:
                self.observe_emergency_return(accident)
            elif accident_status == AccidentStatus.COMPLETE_SOLVED:
                return
            log_status(accident)
        
        
        
        
        
        
        return super().update(*args, **kwargs)


    def assign_emergency_vehicle(self, accident_report: SendingPacket):
        
        devices = self.devices.get_devices_by_group(DeviceType.EMERGENCY_CENTER)
        assert all(isinstance(device, EmergencyVehicle) and isinstance(key, str) for key, device in devices.items())
        self.emergency_vehicles : Dict[str, EmergencyVehicle] = devices # type: ignore
        
        for emergency_vehicle_key, emergency_vehicle in self.emergency_vehicles.items():
            if not emergency_vehicle.is_available():
                continue
            
            self.assign_emergency_vehicle_to_report(accident_report, emergency_vehicle)
            return
            # self.handle_assignment_of_emergency_vehicle(accident_report, emergency_vehicle)


    def assign_emergency_vehicle_to_report(self, accident_report : SendingPacket, emergency_vehicle: EmergencyVehicle):
        self.assign_vehicle_to_report(accident_report, emergency_vehicle)
        self.set_emergency_vehicle_route(emergency_vehicle, accident_report)
        self.update_report_and_vehicle_status(accident_report, emergency_vehicle)
        self.print_dispatch_message(emergency_vehicle, accident_report)
        
        emergency_vehicle.enable_emergency_lights()
        emergency_vehicle.request_fake_traffic_lights_on_route(self.report_manager)
        
        # emergency_vehicle.set_emergency_lights()

    
    def assign_vehicle_to_report(self, accident_report: SendingPacket, emergency_vehicle: EmergencyVehicle):
        accident_report.assigned_emergency_vehicle = emergency_vehicle

    def set_emergency_vehicle_route(self, emergency_vehicle: EmergencyVehicle, accident_report: SendingPacket):
        traci.vehicle.changeTarget(emergency_vehicle.emergency_veh_id, accident_report.object_of_interest.edge_id)
        # laneIndices = edge.getLaneNumber(accident_report.object_of_interest.edge_id) - 1

        laneIndices = 0
        emergency_vehicle.set_stop(accident_report.object_of_interest.edge_id,
                                    accident_report.object_of_interest.lane_position,
                                    laneIndices,
                        AccidentSettings.PARKING_TIME_ACCIDENT)
        
    def update_report_and_vehicle_status(self, accident_report: SendingPacket, emergency_vehicle : EmergencyVehicle):
        accident_report.update_status(AccidentStatus.IN_PROGRESS)
        emergency_vehicle.state = EmergencyVehicleStatus.HEADING_TO_ACCIDENT

    def print_dispatch_message(self, emergency_vehicle : EmergencyVehicle, accident_report: SendingPacket):
        
        
        self.logger._logger.info(f"{ScenarioParameters.TIME} \t | Emergency Vehicle DISPATCHED | {emergency_vehicle.emergency_veh_id} is heading to accident at lane {accident_report.object_of_interest.lane_id}")
        
        
        


    def get(self, device: EmergencyVehicle) -> None | EmergencyVehicle:

        assert isinstance(device, EmergencyVehicle)

        value = super().get(device=device)
        assert value is None or isinstance(value, EmergencyVehicle)
        return value

    
    



    def observe_emergency_response(self, accident: SendingPacket) -> None:
        emergency_veh = accident.assigned_emergency_vehicle
        if not emergency_veh or not emergency_veh.is_at_accident(accident):
            return

        is_authentic = accident.simulation_event.is_authentic
        emergency_center = accident.receiving_entity
        emergency_center.update_request_status(request=accident)

        emergency_veh.update_state(EmergencyVehicleStatus.AT_ACCIDENT)
        accident.update_status(AccidentStatus.ACCIDENT_SOLVED)
        distance_to_accident = self.simulation_adapter.get_distance_to_accident(accident)
        emergency_report_record = EmergencyReportRecord(EmergencyVehicleStatus.AT_ACCIDENT, drived_distance=distance_to_accident)
        emergency_veh.update_emergency_response_history(accident._id, emergency_report_record)

    def observe_emergency_return(self, accident: SendingPacket) -> None:
        emergency_vehicle = accident.assigned_emergency_vehicle
        if emergency_vehicle and emergency_vehicle.is_at_hospital():
            self.handle_arrival_at_hospital(accident)

    def handle_arrival_at_hospital(self, accident: SendingPacket) -> None:
        emergency_vehicle = accident.assigned_emergency_vehicle
        emergency_vehicle.state = EmergencyVehicleStatus.STOPPED_AT_HOSPITAL
        accident.update_status(AccidentStatus.COMPLETE_SOLVED)
        distance_to_hospital = self.simulation_adapter.get_distance_to_hospital(accident)
        emergency_report_record = EmergencyReportRecord(EmergencyVehicleStatus.STOPPED_AT_HOSPITAL, drived_distance=distance_to_hospital)
        emergency_vehicle.update_emergency_response_history(accident._id, emergency_report_record)
        emergency_vehicle.disable_emergency_lights()

    def handle_arrival_at_accident(self, accident: SendingPacket) -> None:
        emergency_veh = accident.assigned_emergency_vehicle
        emergency_veh_id = emergency_veh.emergency_veh_id
        emergency_drop_off = emergency_veh.emergency_drop_off
        emergency_drop_off_position = emergency_veh.emergency_drop_off_position
        parking_time = emergency_veh.parking_time_hospital

        self.simulation_adapter.set_hospital_route(emergency_veh, emergency_drop_off, emergency_drop_off_position, parking_time)
        self.logger.log_hospital_arrival(emergency_veh_id)
        emergency_veh.state = EmergencyVehicleStatus.HEADING_TO_HOSPITAL
        accident.update_status(AccidentStatus.IN_PROGRESS_HOSPITAL)


    