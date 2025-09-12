from __future__ import annotations
from typing import TYPE_CHECKING
from core.simulation.simulation_adapter import SimulationAdapter
from core.utils.log_util import LoggingUtil
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyReportRecord
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentStatus, EmergencyVehicleStatus

if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket
    from core.simulation.report_manager import ReportManager
    from core.models.devices.vehicle import Vehicle


class AccidentStateManager:
    """Manages accident state transitions and monitoring."""
    def __init__(self, report_manager: ReportManager, simulation_adapter: SimulationAdapter, logger: LoggingUtil):
        self.report_manager = report_manager
        self.simulation_adapter = simulation_adapter
        self.logger = logger

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