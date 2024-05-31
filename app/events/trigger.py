

import sys
from typing import Dict

import traci
from data_models.iot_devices import device_handler
from data_models.iot_devices.common import DeviceType

from data_models.iot_devices.device_handler import Devices_Group_Handler, get_devices_group_handler
from data_models.iot_devices.genric_iot_device import DeviceBehaviour
from data_models.iot_devices.traffic_light import TrafficLightManager
from data_models.iot_devices.vehicle import Vehicle
from data_models.report_management.report.report_models import ReportType

from data_models.report_management.report_manager import ReportManager
from data_models.report_management.report.reporter import SendersEntity
from data_models.events.simulation_events import EventRecord, EventState, EventType, SimulationEvent, SimulationEventManager
from experiments.settings import Settings
from network_manager import network_manager
from scenario.emergency_response.emergency_response import EmergencyResponseCenter
import utils.simulation as simulation_utils

import utils.logging as logger
from data.simulation.scenario_constants import Constants as sc
import events.traffic_light_request.utils as traffic_event_utils

import events.accident.collision as collision_utils
import data_models.report_management.utils as reporter_utils
import environment.behavior as simulation_environment
from loguru import logger as logurulogger

import pathfinder

class SimulationEventHandler:
    def __init__(self) -> None:
        
        self._logger = logurulogger.bind(context="simulation_events")
        self._stdout_handler_id = None
        
        
        

    def trigger_collision(self,simulation_events: SimulationEventManager):
        
        devices: Devices_Group_Handler  = get_devices_group_handler()
        vehicles = devices.get(DeviceType.VEHICLE).all()

        if not collision_utils.is_valid_time_constraints(vehicles):
            return

        is_legit_collision_vehicle, collision_vehicle_key, collision_vehicle, stopping_edge, stopping_position = collision_utils.is_legit_collision_vehicle(vehicles, simulation_events)

        if not is_legit_collision_vehicle and collision_vehicle is None and collision_vehicle_key is None:
            return
        
        self._logger.info(f"{sc.TIME_STRING} \t| VALID COLLISION | Collision vehicle: {collision_vehicle_key}, Edge: {stopping_edge} at Position : {stopping_position}")

        simulation_utils.stop_vehicle(collision_vehicle_key, stopping_edge, stopping_position)

        simulation_event = SimulationEvent(event_catalyst=collision_vehicle_key,
                                        eventType= EventType.COLLISION,
                                        event_location=collision_vehicle._position,
                                        time =sc.TIME,
                                        authenticity=True,
                                        event_state=EventState.SCHEDULED)
        
        simulation_events.add(simulation_event)
        
        
        
        debug_accident_reports_path = pathfinder.get_accident_debug_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
        accident_reports_file_path = f"{debug_accident_reports_path}/accident_{simulation_event.id}_Catalyst_{simulation_event.event_catalyst}.pickle" 
        
        logger.write_pickle(accident_reports_file_path, simulation_event)
        
        
        

    def update_collisions(self,simulation_event_manager : SimulationEventManager):
        start_stopping_vehicles = traci.simulation.getStopStartingVehiclesIDList()
        schedulued_collisions : Dict[str,SimulationEvent] = simulation_event_manager.get_scheduled_events(EventType.COLLISION)
        
        devices: Devices_Group_Handler  = get_devices_group_handler()
        vehicles : Dict[str,Vehicle]= devices.get(DeviceType.VEHICLE).all()
        
        
        for veh_id in start_stopping_vehicles:
            
            vehicle : Vehicle = vehicles[veh_id]
            
            new_events = simulation_event_manager.get_new_collision_events(veh_id, schedulued_collisions, vehicle)
            self.trigger_collision_behaviour(new_events, vehicle)


    def report_false_accident(self,simulation_event_manager: SimulationEventManager, report_manager: ReportManager):
        time = sc.TIME

        if not collision_utils.are_false_accident_report_constraints_fulfilled(time):
            return

        reporter : SendersEntity
        vehicle : Vehicle

        reporter, vehicle = collision_utils.find_false_reporter(simulation_event_manager)

        if reporter is not None and  vehicle is not None:
                            
            event = simulation_event_manager.create_event(reporter.id, vehicle, EventType.COLLISION, authenticity=False, event_state=EventState.SCHEDULED)
            simulation_event_manager.add(event)

            reporter_dict : Dict[str,SendersEntity] = {}
            reporter_dict[reporter.id] = reporter
            
            devices   = device_handler.get_devices_group_handler() 
            emergency_response_center : EmergencyResponseCenter = devices.get(DeviceType.EMERGENCY_CENTER)
        
            report =report_manager.create_report(reporter_dict, event, vehicle,emergency_response_center, ReportType.EmergencyReport)
            report_manager.add(report)
            self._logger.info(f"{sc.TIME_STRING} \t| FAKE REPORT COLLISION | Reported vehicle: {report.object_of_interest.object_id}, Edge: {report.object_of_interest.edge_id} at Position : {report.object_of_interest.lane_position}; Reporter: {report.sending_entities.keys()}")

    def report_accidents(self,simulation_event_manager: SimulationEventManager, report_manager: ReportManager, devices: Devices_Group_Handler):
        
        collisions : Dict[str, SimulationEvent] = simulation_event_manager.filter_events(EventType.COLLISION)
            
        for event_id, event in collisions.items():
            if not event.is_valid_accident_event():
                continue

            report = report_manager.get_report(event.event_catalyst)
            accident_vehicle : Vehicle = simulation_event_manager.get_event_catalyst_object(event)
            reporters = network_manager.get_reporters(event,devices)

            if report is None and accident_vehicle is not None:                        
                reporters = reporter_utils.get_suitable_reporters(reporters, collisions)
                
                if len(reporters) == 0:
                    continue
                
                emergency_response_center : EmergencyResponseCenter = devices.get(DeviceType.EMERGENCY_CENTER)

                report = report_manager.create_report(reporters, event, accident_vehicle, emergency_response_center ,ReportType.EmergencyReport)
                report_manager.add(report)
                
                self._logger.info(f"{sc.TIME_STRING} \t| REPORT COLLISION | Reported vehicle: {report.object_of_interest.object_id}, Edge: {report.object_of_interest.edge_id} at Position : {report.object_of_interest.lane_position}; Reporter: {report.sending_entities.keys()}")
                
                event_record = EventRecord(event_id=event.id, event_state=EventState.REPORTED, time=sc.TIME, location=accident_vehicle._position)
                event.update_state(event_record)
                
            elif report is not None:
                filtered_reporters : Dict[str, SendersEntity] = reporter_utils.get_suitable_reporters(reporters, collisions)
                if len(filtered_reporters) == 0:
                    continue

                new_reporterts : Dict[str, SendersEntity] = reporter_utils.get_new_reporters(filtered_reporters, report)
                report.add_reporters(new_reporterts)
                

    def request_fake_traffic_light_priority(self, traffic_light_manager: TrafficLightManager, report_manager: ReportManager, simulation_event_manager: SimulationEventManager):
        
        if not traffic_event_utils.met_time_and_vehicles_preconditions():
            return
        
        vehicles_simulation : Dict[str,Vehicle] = get_devices_group_handler().get(DeviceType.VEHICLE).all()
        malicious_vehicles : Dict[str,Vehicle] = {veh_id: vehicle for veh_id, vehicle in vehicles_simulation.items() if vehicle._behaviour == DeviceBehaviour.MALICIOUS}
        
        requestor_id : Dict[str, Vehicle] = traffic_event_utils.select_vehicle(malicious_vehicles)
        
        if requestor_id is None:
            return
        
        selected_vehicle : Vehicle = malicious_vehicles[requestor_id]
        selected_vehicle.request_traffic_lights_on_route(traffic_light_manager, report_manager, malicious_vehicles, simulation_event_manager, authenticity=False)




    def trigger_collision_behaviour(self, events : Dict[str,SimulationEvent], vehicle :Vehicle):
        
        for event_id, event in events.items():

            event_record = EventRecord(event_id=event.id, event_state=EventState.TRIGGERED, time= sc.TIME, location=vehicle._position)
            event.update_state(event_record)
            simulation_environment.enable_accident_behaviour(event)




    def toggle_logging_stdout(self, activate=True):
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = logger.add(sys.stdout, filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "accident_handler")
        elif not activate and self._stdout_handler_id is not None:
            logger.remove(self._stdout_handler_id)
            self._stdout_handler_id = None