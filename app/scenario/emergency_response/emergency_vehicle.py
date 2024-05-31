

# close all lanes up to one lane
# trigger police car to come
# trigger emergency vehicle
# reduce lane of traffic near by

from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING, Dict
from data_models.events.simulation_events import EventState, EventType, SimulationEvent, SimulationEventManager
from data_models.iot_devices.common import DeviceType


from data_models.iot_devices.traffic_light import TrafficLightManager, TrafficLightSystem
from data_models.iot_devices.vehicle import Vehicle
from data_models.report_management.report.report_models import ReportType

from data_models.report_management.report.report_models import AuthenticityRole
from experiments.settings import Settings
if TYPE_CHECKING:
    from data_models.report_management.report_manager import ReportManager

    from data_models.report_management.report.report import SendingPacket
    from data_models.iot_devices.device_handler import Devices_Group_Handler

from data_models.report_management.report.reporter import  SendersEntity
from typing import List
import utils.logging as logger
import traci

from traci import vehicle
from traci import constants as tc
from traci import exceptions
from data.simulation.scenario_constants import Constants as sc
import pathfinder
from scenario.emergency_response.constants import AccidentSettings, AccidentStatus, EmergencyVehicleStatus

from loguru import logger as logurulogger



class EmergencyReportRecord:

    def __init__(self, emergency_vehicle_status : EmergencyVehicleStatus, drived_distance : float = 0, time : float=sc.TIME) -> None:
        self.emergency_vehicle_status = emergency_vehicle_status
        self.time = time
        self.drived_distance = drived_distance



class EmergencyVehicleManager:
    
    EMERGENCY_BLUE_LIGHT = 0b100000000000
    
    def __init__(self, devices : Devices_Group_Handler):
        self.emergency_vehicles: Dict[str, EmergencyVehicle] = {}
        self.devices : Devices_Group_Handler = devices
        
        
    def initialise_emergency_vehicles(self):
        for emergency_id, emergency_vehicle_configuration in AccidentSettings.EMERGENCY_VEHS.items():
            
            self.add_new_emergency_vehicle(emergency_id, emergency_vehicle_configuration)
            
    def get_emergency_vehicles(self):
        return self.emergency_vehicles
    
    def add_new_emergency_vehicle(self, emergency_id : str, emergency_vehicle_configuration : dict):
        emergency_vehicle = EmergencyVehicle(emergency_id, emergency_vehicle_configuration, self.devices)
        self.emergency_vehicles[emergency_id] = emergency_vehicle
        
        
        vehicle.setSignals(emergency_id, self.EMERGENCY_BLUE_LIGHT)
        
    def enable_access(self, traffic_light_manager : TrafficLightManager):
        
        for emergency_vehicle_key, emergency_vehicle in self.emergency_vehicles.items():
            
            emergency_vehicle.set_traffic_light_manager(traffic_light_manager)
            

class EmergencyVehicle:
    
    def __init__(self, emergency_id : str, emergency_vehicle_configuration : dict, devices):
        
        self.emergency_veh_id : str = emergency_id  
        self.state = EmergencyVehicleStatus.AT_START
        self.route_Index : int = 0
        self.assigend_accident : SendingPacket = 0
        self.stop_status : bool = False
        
        
        self.devices : Devices_Group_Handler = devices
        
        self.emergency_response_history : Dict[str, List[EmergencyReportRecord]] = {}
        
        self.type = 'emergency_vehicle'
        
        self.emergency_drop_off = emergency_vehicle_configuration['emergency_drop_off']
        self.emergency_drop_off_position = emergency_vehicle_configuration['emergency_drop_off_position']
        self.initial_emergency_location = emergency_vehicle_configuration['initial_emergency_location']
        self.parking_time_hospital = emergency_vehicle_configuration['initial_parking_time']
        
        self.traffic_light_manager : TrafficLightManager = None
        self.initialize_start(self.emergency_drop_off,
                              self.initial_emergency_location,
                              self.emergency_drop_off_position,
                            #   AccidentSettings.INITIAL_EMERGENCY_LOCATION,
                              depart=300)
        
        
        # self._logger = logurulogger.bind(context="emergency_vehicle")
        self._stdout_handler_id = None
        

    def get_logger(self):
        return logurulogger.bind(context="emergency_vehicle")

    def get_return_vehicles(self):
        return {emergency_vehicle_key: emergency_vehicle for emergency_vehicle_key, emergency_vehicle in self.emergency_vehicles.items() if emergency_vehicle.state == EmergencyVehicleStatus.HEADING_TO_HOSPITAL}
    

      
    def getRouteID(self):
        routeID = self.emergency_veh_id + '_route_' + str(self.route_Index)
        self.route_Index = self.route_Index + 1
        return routeID
            
        
    def initialize_start(self,start,end,drop_off_position,depart=0):
        
        try: 
        
            route = traci.simulation.findRoute( start,
                                                end,
                                                vType= AccidentSettings.EMERGENCY_TYPE_ID,
                                                routingMode=tc.ROUTING_MODE_DEFAULT)
            
            if len(route.edges) < 2:
                return False
            
            routeID = self.getRouteID()
            traci.route.add(routeID,route.edges)
            traci.vehicle.add(self.emergency_veh_id, routeID, AccidentSettings.EMERGENCY_TYPE_ID)
            
            # get_edge_length = traci.lane.getLength(start + "_0") 
            
            traci.vehicle.insertStop(self.emergency_veh_id, nextStopIndex=0, edgeID=start, pos=drop_off_position, laneIndex=0, duration=AccidentSettings.INITIAL_EMEREGENCY_PARKING_TIME)

        except exceptions.TraCIException as e:

            e.with_traceback()        
    
    
    def update_emergency_response_history(self, accident_key : str, emergency_report_record : EmergencyReportRecord):
        
        if accident_key not in self.emergency_response_history.keys():
            self.emergency_response_history[accident_key] = []
        
        self.emergency_response_history[accident_key].append(emergency_report_record)
    
    
    def update_state(self, state : EmergencyVehicleStatus):
        self.state = state
    
    def enable_emergency_lights(self):
        
        if Settings.VERIFY_TRAFFIC_LIGHT_REQUEST_AUTHENTICITY:
            vehicle.setParameter(self.emergency_veh_id, "device.bluelight.reactiondist", str(25))
        
    
    def disable_emergency_lights(self):
        vehicle.setParameter(self.emergency_veh_id, "device.bluelight.reactiondist", str(0))
        
    
    def is_route_assigned(self,start,end,depart=0):
        
        try: 
            route = traci.simulation.findRoute( start,
                                                end,
                                                vType= AccidentSettings.EMERGENCY_TYPE_ID,
                                                depart=300,
                                                routingMode=tc.ROUTING_MODE_DEFAULT)
            if len(route.edges) < 2:
                return False
            
            routeID = self.getRouteID()
            traci.route.add(routeID,route.edges)
            traci.vehicle.add(self.emergency_veh_id, routeID, AccidentSettings.EMERGENCY_TYPE_ID)
            
            last_edge= route.edges[-1]
            traci.vehicle.setStop(self.emergency_veh_id, edgeID=last_edge, pos=10, laneIndex=0, duration=AccidentSettings.PARKING_TIME_HOSPITAL)
        
        except exceptions.TraCIException as e:
            e.with_traceback()
            
    def get_status(self):
        return self.state
    
    def is_available(self):
        if self.state == EmergencyVehicleStatus.STOPPED_AT_HOSPITAL or self.state == EmergencyVehicleStatus.AT_START:
            return True
        return False
        
    def find_route_accident(self,accident_report: SendingPacket):
        
        try:
            vehicle.changeTarget(self.emergency_veh_id, accident_report.object_of_interest.edge_id)
            self.state = EmergencyVehicleStatus.HEADING_TO_ACCIDENT    
    
            return True
            
        except exceptions.TraCIException as e:
            
            logger.exception(e,f"EXEPCTION: {traci.simulation.getTime()}  | Route could not be assigend for Accident with {accident_report.object_of_interest.object_id} towards {self.emergency_veh_id} at edge ID={accident_report.object_of_interest.edge_id} with position={accident_report.object_of_interest.location}")
            
            
            # TODO: Resolve accident as solution?        

            return False
    
    
    def is_at_accident(self, accident_report: SendingPacket):

        current_position_emergency_vehicle = traci.vehicle.getRoadID(self.emergency_veh_id)

        position_emergency_vehicle =traci.vehicle.getPosition(self.emergency_veh_id)
        position_accidnet_vehicle = accident_report.object_of_interest.location
        
        is_minimal_distance = traci.simulation.getDistance2D(x1=position_emergency_vehicle[0],y1=position_emergency_vehicle[1],x2=position_accidnet_vehicle[0],y2=position_accidnet_vehicle[1])
        
        
        
        is_stopped = traci.vehicle.isStopped(self.emergency_veh_id) or is_minimal_distance < 20
        
        # Problem if the vehicle stops at the beginning and the emergency vehicle stops beforehand
        # is_same_edge = (current_position_emergency_vehicle == accident_report.object_of_interest.edge_id) 
        
        is_status_to_accident = ((self.state == EmergencyVehicleStatus.AT_ACCIDENT) or (self.state == EmergencyVehicleStatus.HEADING_TO_ACCIDENT)) 
        is_accident_status_in_progress = (accident_report.event_status == AccidentStatus.IN_PROGRESS)
        
        is_at_accident = is_stopped and is_status_to_accident and is_accident_status_in_progress # and is_same_edge 
        
        if is_at_accident:
            logger = self.get_logger()
            logger.info(f"Emergency Vehicle {self.emergency_veh_id} is at accident {accident_report.object_of_interest.object_id} at edge {accident_report.object_of_interest.edge_id} at position {accident_report.object_of_interest.location} at time {traci.simulation.getTime()}")
            return True
        
        return False

    def is_at_hospital(self):
        
        vehicles_simulation : Dict[str,Vehicle]= self.devices.get(DeviceType.VEHICLE).all()
        
        current_edge = vehicles_simulation[self.emergency_veh_id]._edge_id    
        current_position = vehicles_simulation[self.emergency_veh_id]._lane_position
        
        is_at_hospital_lane = (current_edge == self.emergency_drop_off)
        
        has_lane_position = (self.emergency_drop_off_position - current_position) < 20
        
        if is_at_hospital_lane and has_lane_position:
            logger = self.get_logger()
            logger.info(f"Emergency Vehicle {self.emergency_veh_id} is at hospital at time {traci.simulation.getTime()}")
            return True
        
        return False

    def request_traffic_lights_on_route(self, report_manager : ReportManager, simulation_event_manager : SimulationEventManager, authenticity=True):
        
        
        vehicles_simulation = simulation_event_manager.devices.get(DeviceType.VEHICLE).all()
        
        traffic_lights = traci.vehicle.getNextTLS(self.emergency_veh_id)
        
        for traffic_light in traffic_lights:
            traffic_light_id = traffic_light[0]
            
            traffic_light: TrafficLightSystem = self.traffic_light_manager.traffic_lights[traffic_light_id]
            
            if self.emergency_veh_id not in traffic_light._requesting_vehicles and not report_manager.exists(self.emergency_veh_id, traffic_light._id):        
            
                traffic_request_event : SimulationEvent = SimulationEvent(  event_catalyst=self.emergency_veh_id,
                                                                            event_location=vehicles_simulation[self.emergency_veh_id]._position,
                                                                            eventType=EventType.TRAFFIC_LIGHT_PRIORITY_REQUEST,
                                                                            time=sc.TIME,
                                                                            authenticity=True,
                                                                            event_state=EventState.TRIGGERED)
                                        
                simulation_event_manager.add(traffic_request_event)
                
                # debug_traffic_light_path = pathfinder.get_traffic_light_debug_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
        
                # debug_traffic_light_path_file = os.path.join(debug_traffic_light_path, f"traffic_light_{traffic_request_event.id}.pickle")
                # logger.write_pickle(debug_traffic_light_path_file, traffic_request_event)

                                
                vehicle: Vehicle = vehicles_simulation[self.emergency_veh_id]
                    
                reporters : Dict[str, SendersEntity] = {}
                reporters[self.emergency_veh_id] = SendersEntity(vehicle,AuthenticityRole.AUTHENTIC,sc.TIME) 
                
                report = report_manager.create_report(reporters,traffic_request_event, vehicle, traffic_light , ReportType.TraffiCPriorityRequest)
                report_manager.add(report)
                    
                # debug_traffic_light_path = pathfinder.get_traffic_light_debug_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
        
                # debug_traffic_light_path_file = os.path.join(debug_traffic_light_path, f"traffic_light_{traffic_request_event.id}_report_id_{report.report_id}.pickle")
                # logger.write_pickle(debug_traffic_light_path_file, report)
                
                
    def set_stop(self, selected_edge : str, lane_position : float, laneIndex : int, parking_duration: int):
    
        emergency_veh_id = self.emergency_veh_id
    
        if vehicle.isStopped(emergency_veh_id):
            vehicle.resume(emergency_veh_id)
            logger = self.get_logger()
            logger.info(f"Emergency vehicle {emergency_veh_id} is resuming at time {sc.TIME}")
            vehicle.insertStop(emergency_veh_id, nextStopIndex=0, edgeID= selected_edge, pos=lane_position, laneIndex=laneIndex, duration=parking_duration)
            
        number_of_stops = len(vehicle.getStops(emergency_veh_id))
            
        if number_of_stops  > 0:
            vehicle.replaceStop(emergency_veh_id, nextStopIndex=0, edgeID= selected_edge, pos= lane_position, laneIndex=laneIndex, duration=parking_duration)
        elif number_of_stops == 0:
            vehicle.setStop(emergency_veh_id, edgeID= selected_edge, pos= lane_position, laneIndex=laneIndex, duration=parking_duration)
        elif number_of_stops > 1:
            return Exception(f"Emergency vehicle {emergency_veh_id} has more than one stop at time {sc.TIME} ")



    def set_traffic_light_manager(self, traffic_light_manager : TrafficLightManager):
        self.traffic_light_manager : TrafficLightManager = traffic_light_manager
        
        
        
        
        
        
    def toggle_logging_stdout(self, activate=True):
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = logger.add(sys.stdout, filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "accident_handler")
        elif not activate and self._stdout_handler_id is not None:
            logger.remove(self._stdout_handler_id)
            self._stdout_handler_id = None