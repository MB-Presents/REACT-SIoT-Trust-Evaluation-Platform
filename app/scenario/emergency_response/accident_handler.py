from __future__ import annotations
from typing import TYPE_CHECKING, Dict


import sys
from data_models.iot_devices.common import DeviceType
from data_models.events.simulation_events import SimulationEventManager



from scenario.emergency_response.emergency_vehicle import EmergencyReportRecord, EmergencyVehicle, EmergencyVehicleManager
from typing import Dict
from scenario.emergency_response.constants import AccidentSettings, AccidentStatus, EmergencyVehicleStatus

 
from traci import vehicle, simulation
from scenario.emergency_response.utils import log_status

from traci import TraCIException


import utils.logging as logger
from loguru import logger as logurulogger
 
 
from data_models.report_management.report.report_models import ReportType
 
if TYPE_CHECKING:
    from data_models.report_management.report.report import SendingPacket
    from data_models.report_management.report_manager import ReportManager
    from data_models.iot_devices.vehicle import Vehicle

class AccidentHandler:
    
    def __init__(self, emergency_vehicles_manager : EmergencyVehicleManager, report_manager: ReportManager, simulation_event_manager : SimulationEventManager):
        
        self.emergency_vehicles_manager : EmergencyVehicleManager = emergency_vehicles_manager
        self.report_manager: ReportManager = report_manager
        self.simulation_event_manager : SimulationEventManager = simulation_event_manager
        
        self._logger = logurulogger.bind(context="vehicle")
        self._stdout_handler_id = None
        
        pass

    def schedule_emergency_response(self, report_manager: ReportManager):
        
        
            authentic_accident_reports : Dict[str, SendingPacket] = report_manager.get_authentic_reports_by_type(
                ReportType.EmergencyReport)

            for accident_key, accident in authentic_accident_reports.items():
                self.handle_accident(accident)


    def handle_accident(self, accident: SendingPacket):
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
        
        
        
    def observe_emergency_return(self, accident: SendingPacket):
            emergency_vehicle = accident.assigned_emergency_vehicle
            if emergency_vehicle.is_at_hospital():
                 self.handle_arrival_at_hospital(accident)

    def handle_arrival_at_hospital(self, accident: SendingPacket):
        emergency_vehicle = accident.assigned_emergency_vehicle
        emergency_vehicle.state = EmergencyVehicleStatus.STOPPED_AT_HOSPITAL
        accident.update_status(AccidentStatus.COMPLETE_SOLVED)
        stops: tuple = vehicle.getStops(emergency_vehicle.emergency_veh_id)
        distance_to_hospital = simulation.getDistanceRoad(accident.object_of_interest.edge_id, accident.object_of_interest.         lane_position,
                                                            AccidentSettings.EMERGENCY_DROP_OFF, AccidentSettings.EMERGENCY_DROP_OFF_LANE_POSITION)
        emergency_report_record = EmergencyReportRecord(EmergencyVehicleStatus.STOPPED_AT_HOSPITAL, drived_distance=distance_to_hospital)
        emergency_vehicle.update_emergency_response_history(accident.report_id, emergency_report_record)
        emergency_vehicle.disable_emergency_lights()

    def observe_emergency_response(self, accident_request: SendingPacket):
        
        emergency_veh = accident_request.assigned_emergency_vehicle
        if not emergency_veh.is_at_accident(accident_request):
            return
        
        # Simplifiy the accident verification check through checking the simulation_event state.
        is_authentic = accident_request.simulation_event.is_authentic
        emergency_center = accident_request.receiving_entity
        
        
        emergency_center.update_request_status(request=accident_request)
        
        
        
        # transactions = emergency_center.trust_manager.trust_transaction_controller.get_transactions_by_request_id(accident_request)
        # emergency_center.trust_manager.trust_transaction_controller.update_verification_status_of_request(transactions,is_authentic)

        
        
        emergency_veh.update_state(EmergencyVehicleStatus.AT_ACCIDENT)
        accident_request.update_status(AccidentStatus.ACCIDENT_SOLVED)
        
        distance_to_accident = simulation.getDistanceRoad(AccidentSettings.EMERGENCY_DROP_OFF, AccidentSettings.EMERGENCY_DROP_OFF_LANE_POSITION, accident_request.object_of_interest.edge_id, accident_request.object_of_interest.lane_position)
        
        emergency_report_record = EmergencyReportRecord(EmergencyVehicleStatus.AT_ACCIDENT, drived_distance=distance_to_accident)
        emergency_veh.update_emergency_response_history(accident_request.report_id, emergency_report_record)

    def assign_emergency_vehicle(self, accident_report: SendingPacket):
        for emergency_vehicle_key, emergency_vehicle in self.emergency_vehicles_manager.emergency_vehicles.items():
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
        emergency_vehicle.request_traffic_lights_on_route(self.report_manager,self.simulation_event_manager)
        
        # emergency_vehicle.set_emergency_lights()

    def assign_vehicle_to_report(self, accident_report: SendingPacket, emergency_vehicle: EmergencyVehicle):
        accident_report.assigned_emergency_vehicle = emergency_vehicle

    def set_emergency_vehicle_route(self, emergency_vehicle: EmergencyVehicle, accident_report: SendingPacket):
        vehicle.changeTarget(emergency_vehicle.emergency_veh_id, accident_report.object_of_interest.edge_id)
        # laneIndices = edge.getLaneNumber(accident_report.object_of_interest.edge_id) - 1
        emergency_vehicle
        
        laneIndices = 0 
        emergency_vehicle.set_stop(accident_report.object_of_interest.edge_id, 
                        accident_report.object_of_interest.lane_position, 
                        laneIndices, 
                        AccidentSettings.PARKING_TIME_ACCIDENT)
        
    def update_report_and_vehicle_status(self, accident_report: SendingPacket, emergency_vehicle : EmergencyVehicle):
        accident_report.update_status(AccidentStatus.IN_PROGRESS)
        emergency_vehicle.state = EmergencyVehicleStatus.HEADING_TO_ACCIDENT

    def print_dispatch_message(self, emergency_vehicle : EmergencyVehicle, accident_report: SendingPacket):
        
        
        self._logger.info(f"{simulation.getTime()} \t | Emergency Vehicle DISPATCHED | {emergency_vehicle.emergency_veh_id} is heading to accident at lane {accident_report.object_of_interest.lane_id}")
        
        
    def handle_arrival_at_accident(self, accident: SendingPacket):
        emergency_veh_id = accident.assigned_emergency_vehicle.emergency_veh_id
        emergency_veh = accident.assigned_emergency_vehicle

        emergency_drop_off = self.emergency_vehicles_manager.emergency_vehicles[emergency_veh_id].emergency_drop_off 
        emergency_drop_off_position = self.emergency_vehicles_manager.emergency_vehicles[emergency_veh_id].emergency_drop_off_position
        
        emergency_parking_time = self.emergency_vehicles_manager.emergency_vehicles[emergency_veh_id].parking_time_hospital
        
        try:
            
            vehicles = accident.assigned_emergency_vehicle.devices.get(DeviceType.VEHICLE).all()
            emergency_vehicle : Vehicle = vehicles[emergency_veh_id]

            if emergency_vehicle._edge_id == emergency_drop_off:
                
                route = simulation.findRoute(emergency_veh_id, emergency_vehicle._edge_id, 333934001, "passenger")
                
                vehicle.setRoute(emergency_veh_id, route.edges + [emergency_drop_off]) 
                
            elif emergency_vehicle._edge_id != emergency_drop_off:
                vehicle.changeTarget(emergency_veh_id, emergency_drop_off)
            
            emergency_veh.set_stop(emergency_drop_off, emergency_drop_off_position, laneIndex=0, parking_duration=emergency_parking_time)
            
            self._logger.info(f"Emergency Vehicle {emergency_veh_id} is heading to hospital from lane {vehicle.getLaneID(emergency_veh_id)} at time {simulation.getTime()}")
        except TraCIException as e:
            e.with_traceback()
            return  # Terminate current iteration of handle_arrival_at_accident and return to caller
        
        
        # Currently there is no stop at the emeergency locations

        emergency_veh.state = EmergencyVehicleStatus.HEADING_TO_HOSPITAL    
        accident.update_status(AccidentStatus.IN_PROGRESS_HOSPITAL)



    def toggle_logging_stdout(self, activate=True):
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = logger.add(sys.stdout, filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "accident_handler")
        elif not activate and self._stdout_handler_id is not None:
            logger.remove(self._stdout_handler_id)
            self._stdout_handler_id = None