

# close all lanes up to one lane
# trigger police car to come
# trigger emergency vehicle
# reduce lane of traffic near by

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
import loguru
from core.models.events.simulation_events import EventState, EventType, SimulationEvent, SimulationEventManager
from core.models.devices.common import DeviceType


from core.models.devices.vehicle import Vehicle
from core.models.uniform.components.report_models import AuthenticityRole, ReportType

from core.models.uniform.components.reporter import SendersEntity
from core.simulation.event_bus.base_event import EmergencyVehicleDispatchEvent
from core.simulation.simulation_context import SimulationContext
from experiments.settings import Settings
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings, AccidentStatus, EmergencyVehicleStatus
if TYPE_CHECKING:
    from core.simulation.report_manager import ReportManager
    from core.models.devices.traffic_light import TrafficLightSystem

    from core.models.uniform.components.report import SendingPacket
    from core.models.devices.device_handler import DevicesGroupHandler

from typing import List
import utils.logging as logger
import traci

from traci import vehicle
from traci import constants as tc
from traci import exceptions
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters





class EmergencyReportRecord:

    def __init__(self, emergency_vehicle_status : EmergencyVehicleStatus, drived_distance : float = 0, time : float=ScenarioParameters.TIME) -> None:
        self.emergency_vehicle_status = emergency_vehicle_status
        self.time = time
        self.drived_distance = drived_distance



# class EmergencyVehicleManager:
    
#     EMERGENCY_BLUE_LIGHT = 0b100000000000
    
#     def __init__(self, devices : DevicesGroupHandler):
#         self.emergency_vehicles: Dict[str, EmergencyVehicle] = {}
#         self.devices : DevicesGroupHandler = devices
        
        
#     def initialise_emergency_vehicles(self):
#         for emergency_id, emergency_vehicle_configuration in AccidentSettings.EMERGENCY_VEHS.items():
            
#             self.add_new_emergency_vehicle(emergency_id, emergency_vehicle_configuration)
            
#     def get_emergency_vehicles(self):
#         return self.emergency_vehicles
    
#     def add_new_emergency_vehicle(self, emergency_id : str, emergency_vehicle_configuration : dict):
#         emergency_vehicle = EmergencyVehicle(emergency_id, emergency_vehicle_configuration, self.devices)
#         self.emergency_vehicles[emergency_id] = emergency_vehicle
        
        
#         vehicle.setSignals(emergency_id, self.EMERGENCY_BLUE_LIGHT)
        


class EmergencyVehicle(Vehicle):
    
    def __init__(self, 
                 emergency_id : str,
                 emergency_vehicle_configuration : dict,
                 simulation_context : Optional[SimulationContext]= None):
        
        super().__init__(
            veh_id=emergency_id,
            simulation_context=simulation_context)


        self._type = DeviceType.EMERGENCY_VEHICLE
        self.emergency_veh_id : str = emergency_id  
        self.state = EmergencyVehicleStatus.AT_START
        self.route_Index : int = 0
        self.assigend_accident : SendingPacket 
        self.stop_status : bool = False
        
        
        self.emergency_response_history : Dict[str, List[EmergencyReportRecord]] = {}
        
        # self.type = 'emergency_vehicle'
        
        self.emergency_drop_off = emergency_vehicle_configuration['emergency_drop_off']
        self.emergency_drop_off_position = emergency_vehicle_configuration['emergency_drop_off_position']
        self.initial_emergency_location = emergency_vehicle_configuration['initial_emergency_location']
        self.parking_time_hospital = emergency_vehicle_configuration['initial_parking_time']
        
        
        self.is_emergency_emergency_route_setup(self.emergency_drop_off,
                              self.initial_emergency_location,
                              self.emergency_drop_off_position,
                            #   AccidentSettings.INITIAL_EMERGENCY_LOCATION,
                              depart=300)
        
        
        # self._logger = loguru.logger.bind(context="emergency_vehicle")
        self._stdout_handler_id = None
        
        assert self._simulation_context is not None, "Simulation context is None"
        self._simulation_context.get_event_bus().subscribe(EmergencyVehicleDispatchEvent, self._handle_emergency_vehicle_dispatch_event, receiver_id=self.emergency_veh_id)

    def _handle_emergency_vehicle_dispatch_event(self, event: EmergencyVehicleDispatchEvent):   
        raise NotImplementedError("This method should be implemented in subclasses")
    


    def get_logger(self) -> loguru.Logger:
        return loguru.logger.bind(context="emergency_vehicle")

    def get_return_vehicles(self) -> Dict[str, EmergencyVehicle]:
        if self.state == EmergencyVehicleStatus.HEADING_TO_HOSPITAL:
            return {self.emergency_veh_id: self}
        return {}
        

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()

      
    def getRouteID(self) -> str:
        routeID = self.emergency_veh_id + '_route_' + str(self.route_Index)
        self.route_Index = self.route_Index + 1
        return routeID
            
        
    def is_emergency_emergency_route_setup(self,start,end,drop_off_position,depart=0) -> bool:
        
        try: 
        
            route = traci.simulation.findRoute( start,
                                                end,
                                                vType= AccidentSettings.EMERGENCY_TYPE_ID,
                                                routingMode=tc.ROUTING_MODE_DEFAULT)
            
            assert route, f"Route could not be found for emergency vehicle {self.emergency_veh_id} from {start} to {end}"
            assert hasattr(route, 'edges'), f"Route has no edges for emergency vehicle {self.emergency_veh_id} from {start} to {end}"
            # assert len(route.edges) > 0, f"Route has no valid edges for emergency vehicle {self.emergency_veh_id} from {start} to {end}"

            if len(route.edges) < 2: # type: ignore
                return False
            
            routeID = self.getRouteID()
            traci.route.add(routeID,route.edges) # type: ignore
            traci.vehicle.add(self.emergency_veh_id, routeID, AccidentSettings.EMERGENCY_TYPE_ID)
            
            # get_edge_length = traci.lane.getLength(start + "_0") 
            
            traci.vehicle.insertStop(self.emergency_veh_id, nextStopIndex=0, edgeID=start, pos=drop_off_position, laneIndex=0, duration=AccidentSettings.INITIAL_EMEREGENCY_PARKING_TIME)
            return True

        except exceptions.TraCIException as e:

            logger.exception(e,f"EXEPCTION: {traci.simulation.getTime()}  | Route could not be assigend for Emergency Vehicle towards {self.emergency_veh_id} at edge ID={start} with position={drop_off_position}")
            return False     
    
    
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
            
            assert route, f"Route could not be found for emergency vehicle {self.emergency_veh_id} from {start} to {end}"
            assert hasattr(route, 'edges'), f"Route has no edges for emergency vehicle {self.emergency_veh_id} from {start} to {end}"
            assert isinstance(route.edges, list), f"Route edges is not a list for emergency vehicle {self.emergency_veh_id} from {start} to {end}" # type: ignore
            
            
            if len(route.edges) < 2: # type: ignore
                return False
            
            routeID = self.getRouteID()
            traci.route.add(routeID,route.edges) # type: ignore
            traci.vehicle.add(self.emergency_veh_id, routeID, AccidentSettings.EMERGENCY_TYPE_ID)
            
            last_edge= route.edges[-1] # type: ignore
            traci.vehicle.setStop(self.emergency_veh_id, edgeID=last_edge, pos=10, laneIndex=0, duration=AccidentSettings.PARKING_TIME_HOSPITAL)
        
        except exceptions.TraCIException as e:
            logger.exception(e,f"EXEPCTION: {traci.simulation.getTime()}  | Route could not be assigend for Emergency Vehicle towards {self.emergency_veh_id} at edge ID={start} with position={0}")
            
    def get_status(self):
        return self.state
    
    def is_available(self) -> bool:
        if self.state == EmergencyVehicleStatus.STOPPED_AT_HOSPITAL or self.state == EmergencyVehicleStatus.AT_START:
            return True
        return False

    def find_route_accident(self, accident_report: SendingPacket):
        
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
        
        
        assert isinstance(is_minimal_distance, float), f"Distance is not a float value for emergency vehicle {self.emergency_veh_id} at time {traci.simulation.getTime()}"
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
        
        vehicles_simulation : Dict[str,Vehicle] = DevicesGroupHandler().get_devices_by_group(DeviceType.VEHICLE) # type: ignore
        assert all(isinstance(v, Vehicle) for v in vehicles_simulation.values()), "Not all devices in vehicles_simulation are of type Vehicle"
        
        current_edge = vehicles_simulation[self.emergency_veh_id]._edge_id    
        current_position = vehicles_simulation[self.emergency_veh_id]._lane_position
        
        is_at_hospital_lane = (current_edge == self.emergency_drop_off)
        
        has_lane_position = (self.emergency_drop_off_position - current_position) < 20
        
        if is_at_hospital_lane and has_lane_position:
            logger = self.get_logger()
            logger.info(f"Emergency Vehicle {self.emergency_veh_id} is at hospital at time {traci.simulation.getTime()}")
            return True
        
        return False

    def request_fake_traffic_lights_on_route(self, report_manager : ReportManager, authenticity=True):
        
        assert self._simulation_context is not None, "Simulation context is None"
        assert self._simulation_context._device_registry is not None, "Device registry is None in simulation context"
        vehicles_simulation = self._simulation_context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        
        traffic_lights = traci.vehicle.getNextTLS(self.emergency_veh_id)
        
        # traffic_light : Tuple[str, int, float, str]
        for traffic_light in traffic_lights:
            assert isinstance(traffic_light, Tuple), f"Traffic light is not a tuple for emergency vehicle {self.emergency_veh_id} at time {ScenarioParameters.TIME}"
            traffic_light_id = traffic_light[0]
            
            
            
            assert isinstance(traffic_light_id, str), f"Traffic light ID is not a string for emergency vehicle {self.emergency_veh_id} at time {ScenarioParameters.TIME}"
            
            device = self._simulation_context._device_registry.get_device(traffic_light_id)
            assert device is not None, f"Device with ID {traffic_light_id} not found in device registry" 
            assert isinstance(device, TrafficLightSystem), f"Device with ID {traffic_light_id} is not of type TrafficLightSystem"
            traffic_light : TrafficLightSystem = device    
        
            
            if self.emergency_veh_id not in traffic_light._requesting_vehicles and not report_manager.exists(self.emergency_veh_id, traffic_light._id):        


                assert isinstance(self._position, Tuple), f"Emergency vehicle {self.emergency_veh_id} position is not a tuple at time {ScenarioParameters.TIME}"
                assert len(self._position) == 2, f"Emergency vehicle {self.emergency_veh_id} position does not have 2 elements at time {ScenarioParameters.TIME}"   
                assert isinstance(ScenarioParameters.TIME, int), f"ScenarioParameters.TIME is not an integer at time {ScenarioParameters.TIME}"
                
                traffic_request_event : SimulationEvent = SimulationEvent(  catalyst_id=self.emergency_veh_id,
                                                                            location=self._position,
                                                                            event_type=EventType.TRAFFIC_LIGHT_PRIORITY_REQUEST,
                                                                            time=ScenarioParameters.TIME,
                                                                            is_authentic=True,
                                                                            state=EventState.TRIGGERED)
                                        
                
                SimulationEventManager().add_event(traffic_request_event)
                
                # debug_traffic_light_path = pathfinder.get_traffic_light_debug_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
        
                # debug_traffic_light_path_file = os.path.join(debug_traffic_light_path, f"traffic_light_{traffic_request_event.id}.pickle")
                # logger.write_pickle(debug_traffic_light_path_file, traffic_request_event)

                                
                device = vehicles_simulation[self.emergency_veh_id]
                assert isinstance(device, Vehicle), f"Device with ID {self.emergency_veh_id} is not of type Vehicle"

                vehicle: Vehicle = device

                reporters: Dict[str, SendersEntity] = {}
                reporters[self.emergency_veh_id] = SendersEntity(vehicle, AuthenticityRole.AUTHENTIC, ScenarioParameters.TIME)

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
            logger.info(f"Emergency vehicle {emergency_veh_id} is resuming at time {ScenarioParameters.TIME}")
            vehicle.insertStop(emergency_veh_id, nextStopIndex=0, edgeID= selected_edge, pos=lane_position, laneIndex=laneIndex, duration=parking_duration)
            
        number_of_stops = len(vehicle.getStops(emergency_veh_id))
            
        if number_of_stops  > 0:
            vehicle.replaceStop(emergency_veh_id, nextStopIndex=0, edgeID= selected_edge, pos= lane_position, laneIndex=laneIndex, duration=parking_duration)
        elif number_of_stops == 0:
            vehicle.setStop(emergency_veh_id, edgeID= selected_edge, pos= lane_position, laneIndex=laneIndex, duration=parking_duration)
        elif number_of_stops > 1:
            return Exception(f"Emergency vehicle {emergency_veh_id} has more than one stop at time {ScenarioParameters.TIME} ")



        
        
        
    def toggle_logging_stdout(self, activate=True):
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = self.get_logger().add(sys.stdout, filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "accident_handler")
        elif not activate and self._stdout_handler_id is not None:
            self.get_logger().remove(self._stdout_handler_id)
            self._stdout_handler_id = None