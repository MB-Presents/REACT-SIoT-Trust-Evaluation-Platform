import random
import sys
from typing import Dict, List, Union, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import traci
from core.models.devices.common import DeviceBehaviour, DeviceType
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.vehicle import Vehicle
from core.models.uniform.components.report_models import AuthenticityRole, ReportType, Situation
from core.models.uniform.components.object_of_interest import ObjectOfInterest 
from core.models.uniform.components.report import SendingPacket
from core.models.uniform.components.reporter import SendersEntity
from core.models.uniform.utils import get_new_reporters, get_suitable_reporters
from core.simulation import network
from core.simulation.report_manager import ReportManager

from core.models.events.simulation_events import EventRecord, EventState, EventType, SimulationEvent, SimulationEventManager, VerificationState

from core.simulation.environment import disable_accident_behaviour, enable_accident_behaviour
from core.simulation.logging import ObjectType
from core.simulation.simulation_context import SimulationContext
from experiments.settings import Settings
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings, AccidentStatus

from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle

from traci import simulation, vehicle 
from scenarios.canberra_case_study.core.networks import NetworkConstants
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters 
from utils import convert
import utils.logging as logger

from loguru import logger as loguru_logger


# Configuration and validation interfaces
@dataclass
class CollisionConstraints:
    min_vehicles: int = 1
    min_lane_position_offset: float = 15.0
    max_lane_position_offset: float = 15.0
    min_route_edges: int = 2
    nearby_accident_distance: float = 80.0
    route_distance_offset: float = 30.0


class ICollisionValidator(ABC):
    """Interface for collision validation logic"""
    
    @abstractmethod
    def is_valid_time_constraints(self, vehicles: Dict[str, Vehicle]) -> bool:
        pass
    
    @abstractmethod
    def is_valid_route(self, origin: str, destination: str, vehicle_type: str) -> bool:
        pass
    
    @abstractmethod
    def is_accident_routable_for_emergency_vehicle(self, vehicle: Vehicle, edge_id: str, lane_position: float) -> bool:
        pass
    
    @abstractmethod
    def is_valid_lane_position(self, vehicle: Vehicle, edge_id: str) -> bool:
        pass
    
    @abstractmethod
    def is_on_valid_lane(self, edge_id: str) -> bool:
        pass


class ICollisionCalculator(ABC):
    """Interface for collision calculations"""
    
    @abstractmethod
    def get_required_braking_distance(self, vehicle_key: str) -> float:
        pass
    
    @abstractmethod
    def get_length_to_end_of_edge(self, vehicle: Vehicle, lane_length: float, 
                                 accumulated_length: float, current_edge: str, 
                                 route: List[str], route_index: int) -> float:
        pass
    
    @abstractmethod
    def adjust_vehicle_position(self, vehicle: Vehicle) -> float:
        pass


class ICollisionSelector(ABC):
    """Interface for collision vehicle selection"""
    
    @abstractmethod
    def select_collision_vehicle(self, vehicles: Dict[str, Vehicle], 
                               simulation_events: SimulationEventManager) -> Tuple[bool, Optional[str], Optional[Vehicle], Optional[str], Optional[float]]:
        pass


# Concrete implementations
class CollisionValidator(ICollisionValidator):
    """Handles validation logic for collision scenarios"""

    def __init__(self, constraints: CollisionConstraints, network_constants: NetworkConstants, accident_settings: AccidentSettings):
        self.constraints = constraints
        self.network_constants = network_constants
        self.accident_settings = accident_settings
        self._logger = loguru_logger.bind(context="collision_validator")

    def is_valid_time_constraints(self, vehicles: Dict[str, Vehicle]) -> bool:
        return (
            len(vehicles) > self.constraints.min_vehicles - 1 and
            ScenarioParameters.TIME != 0 and
            ScenarioParameters.TIME % Settings.INTERVAL_OF_ACCIDENTS == 0
        )

    def is_valid_route(self, origin: str, destination: str, vehicle_type: str) -> bool:
        try:
            route = traci.simulation.findRoute(origin, destination, vType=vehicle_type)
            return len(route.edges) > self.constraints.min_route_edges - 1
        except Exception as e:
            self._logger.error(f"Route validation failed: {e}")
            return False

    def is_accessible_from_hospital(self, vehicle: Vehicle, edge_id: str, lane_position: float) -> bool:
        destination = edge_id
        route_info = {
            'message': f"Route to accident successful for emergency vehicle from {self.accident_settings.EMERGENCY_DROP_OFF} to {destination}"
        }
        if not self.is_valid_route(self.accident_settings.EMERGENCY_DROP_OFF, destination, 'emergency_vehicle'):
            route_info['message'] = f"Route to accident cannot be established for vehicle {vehicle._id} at {destination}"
            logger.info(ObjectType.ROUTE_MESSAGE.name, route_info)
            return False
        logger.info(ObjectType.ROUTE_MESSAGE.name, route_info)
        return True

    def is_accessible_from_accident(self, vehicle: Vehicle, edge_id: str, lane_position: float) -> bool:
        destination = edge_id
        route_info = {
            'message': f"Route to hospital successful for emergency vehicle from {destination} to {self.accident_settings.EMERGENCY_DROP_OFF}"
        }
        if not self.is_valid_route(destination, self.accident_settings.EMERGENCY_DROP_OFF, 'emergency_vehicle'):
            route_info['message'] = f"Route from accident to hospital cannot be established for vehicle {vehicle._id} at {destination}"
            logger.info(ObjectType.ROUTE_MESSAGE.name, route_info)
            return False
        logger.info(ObjectType.ROUTE_MESSAGE.name, route_info)
        return True

    def is_allowed_on_lane(self, vehicle: Vehicle, edge_id: str) -> bool:
        try:
            allowed_vehicles = traci.lane.getAllowed(f"{edge_id}_0")
            if 'emergency' not in allowed_vehicles and vehicle._vehicle_class not in allowed_vehicles:
                logger.info(ObjectType.ROUTE_MESSAGE.name, {
                    'message': f"Vehicle {vehicle._id} at {edge_id} is not allowed on lane: {vehicle._lane_id}"
                })
                return False
            return True
        except Exception as e:
            self._logger.error(f"Lane permission check failed: {e}")
            return False

    def is_accident_routable_for_emergency_vehicle(self, vehicle: Vehicle, edge_id: str, lane_position: float) -> bool:
        try:
            return (
                self.is_accessible_from_hospital(vehicle, edge_id, lane_position) and
                self.is_accessible_from_accident(vehicle, edge_id, lane_position) and
                self.is_allowed_on_lane(vehicle, edge_id)
            )
        except Exception as e:
            exception_info = {
                'time': ScenarioParameters.TIME,
                'exception_type': type(e).__name__,
                'message': str(e)
            }
            self._logger.error(f"Emergency vehicle routing failed: {exception_info}")
            return False

    def is_valid_lane_position(self, vehicle: Vehicle, edge_id: str) -> bool:
        try:
            lane_length = traci.lane.getLength(f"{edge_id}_0")
            assert isinstance(lane_length, float), "Lane length must be a float value"
            
            return (self.constraints.min_lane_position_offset <= vehicle._lane_position <= 
                   lane_length - self.constraints.max_lane_position_offset)
        except Exception as e:
            self._logger.error(f"Lane position validation failed: {e}")
            return False

    def is_on_valid_lane(self, edge_id: str) -> bool:
        base_edge_id = edge_id.split('_')[0].lstrip(':')
        assert isinstance(base_edge_id, str), "Base edge ID must be a string"
        
        return (base_edge_id in self.network_constants.EDGES and 
                base_edge_id not in self.network_constants.JUNCTIONS)


class CollisionCalculator(ICollisionCalculator):
    """Handles calculations related to collision scenarios"""
    
    def __init__(self):
        self._logger = loguru_logger.bind(context="collision_calculator")

    def get_required_braking_distance(self, vehicle_key: str) -> float:
        try:
            max_decel = vehicle.getDecel(vehicle_key)
            current_speed = vehicle.getSpeed(vehicle_key)
            
            assert isinstance(max_decel, float) and isinstance(current_speed, float), "Deceleration and speed must be float values"
            
            if max_decel <= 0 or current_speed <= 0:
                return 0.0
                
            time = round((current_speed / max_decel) + 0.5)
            return current_speed * time + (max_decel * time * time) / 2
        except Exception as e:
            self._logger.error(f"Braking distance calculation failed: {e}")
            return 0.0

    def get_length_to_end_of_edge(self, vehicle: Vehicle, lane_length: float, 
                                 accumulated_length: float, current_edge: str, 
                                 route: List[str], route_index: int) -> float:
        try:
            if current_edge == vehicle._edge_id:
                return lane_length - vehicle._lane_position
                
            length_of_next_edge = traci.lane.getLength(f"{route[route_index]}_0")
            distance = simulation.getDistanceRoad(
                vehicle._edge_id, vehicle._lane_position, route[route_index],
                length_of_next_edge, isDriving=True
            )
            assert isinstance(distance, float), "Distance must be a float value"
            
            return distance
        except Exception as e:
            self._logger.error(f"Edge length calculation failed: {e}")
            return 0.0

    def adjust_vehicle_position(self, vehicle: Vehicle) -> float:
        try:
            position = vehicle._lane_position
            lane_length = traci.lane.getLength(f"{vehicle._edge_id}_0")
            assert isinstance(lane_length, float), "Lane length must be a float value"
            return max(15, min(position, lane_length - 15))
        except Exception as e:
            self._logger.error(f"Position adjustment failed: {e}")
            return vehicle._lane_position


class CollisionSelector(ICollisionSelector):
    """Handles selection of vehicles and positions for collisions"""
    
    def __init__(self, validator: ICollisionValidator, calculator: ICollisionCalculator, 
                 constraints: CollisionConstraints, accident_settings, network_constants):
        self.validator = validator
        self.calculator = calculator
        self.constraints = constraints
        self.accident_settings = accident_settings
        self.network_constants = network_constants
        self._logger = loguru_logger.bind(context="collision_selector")

    def select_collision_vehicle(self, vehicles: Dict[str, Vehicle], 
                               simulation_events: SimulationEventManager) -> Tuple[bool, Optional[str], Optional[Vehicle], Optional[str], Optional[float]]:
        vehicle_candidates = {k: v for k, v in vehicles.items() if k.startswith('veh')}
        
        while vehicle_candidates:
            collision_vehicle_key, collision_vehicle = random.choice(list(vehicle_candidates.items()))
            
            if not simulation_events.has_event_for_vehicle(collision_vehicle_key):
                is_valid, stopping_edge, stopping_position = self._is_valid_collision_vehicle(
                    collision_vehicle_key, collision_vehicle, vehicles
                )
                if is_valid:
                    return True, collision_vehicle_key, collision_vehicle, stopping_edge, stopping_position
            
            del vehicle_candidates[collision_vehicle_key]
        
        return False, None, None, None, None

    def _is_valid_collision_vehicle(self, vehicle_key: str, vehicle: Vehicle, 
                                  vehicles: Dict[str, Vehicle]) -> Tuple[bool, Optional[str], Optional[float]]:
        if (vehicle._vehicle_type not in self.accident_settings.ALLOWED_VEHICLE_COLLISION_TYPES or 
            vehicle_key.startswith("emergency_veh")):
            return False, None, None
        
        if (vehicle._edge_id not in self.network_constants.EDGES or 
            traci.edge.getLaneNumber(vehicle._edge_id) == 1):
            return False, None, None
        
        if vehicle._edge_id in ['489467563', '489692410']:
            return False, None, None
        
        stopping_edge, stopping_position = self._get_stop_parameters(vehicle, vehicle_key)
        if stopping_edge is None or not self.validator.is_on_valid_lane(stopping_edge):
            return False, None, None
        
        return True, stopping_edge, stopping_position

    def _get_stop_parameters(self, vehicle: Vehicle, vehicle_key: str) -> Tuple[Optional[str], Optional[float]]:
        try:
            route = traci.vehicle.getRoute(vehicle_key)
            route_index = route.index(vehicle._edge_id) if vehicle._edge_id in route else -1
            accumulated_length = 0.0
            
            assert isinstance(route, list) and route_index != -1, "Route must be a list and contain the vehicle's current edge"
            
            while route_index < len(route) - 1:
                is_stoppable, stopping_edge, stopping_position, accumulated_length = self._is_vehicle_stoppable_at_edge(
                    vehicle, vehicle_key, route, route_index, accumulated_length
                )
                
                if is_stoppable:
                    return stopping_edge, stopping_position
                route_index += 1
            
            return None, None
        except Exception as e:
            self._logger.error(f"Stop parameters calculation failed: {e}")
            return None, None

    def _is_vehicle_stoppable_at_edge(self, vehicle: Vehicle, vehicle_key: str, 
                                    route: List[str], route_index: int, 
                                    accumulated_length: float) -> Tuple[bool, Optional[str], Optional[float], float]:
        try:
            edge_id = route[route_index]
            required_distance = self.calculator.get_required_braking_distance(vehicle_key)
            
            lane_length = traci.lane.getLength(f"{edge_id}_0")
            lane_number = traci.edge.getLaneNumber(edge_id)
            
            assert isinstance(lane_length, float) and isinstance(lane_number, int), "Lane length must be float and lane number must be int"
            
            if lane_number <= 1:
                if vehicle._edge_id == edge_id:
                    accumulated_length += lane_length - vehicle._lane_position
                else:
                    accumulated_length += lane_length
                return False, None, None, accumulated_length
            
            length_to_end = self.calculator.get_length_to_end_of_edge(
                vehicle, lane_length, accumulated_length, edge_id, route, route_index
            )
            accumulated_length = length_to_end - lane_length
            
            if length_to_end > required_distance:
                stop_position = length_to_end - required_distance
                offset = self.constraints.route_distance_offset
                min_position, max_position = offset, lane_length - offset
                
                if min_position <= stop_position <= max_position:
                    stop_position = random.randint(round(min_position), round(max_position))
                
                if not self._is_valid_stop_location(vehicle, edge_id, stop_position):
                    return False, None, None, accumulated_length
                
                return True, edge_id, stop_position, accumulated_length
            
            accumulated_length = length_to_end
            return False, None, None, accumulated_length
            
        except Exception as e:
            self._logger.error(f"Vehicle stoppability check failed: {e}")
            return False, None, None, accumulated_length

    def _is_valid_stop_location(self, vehicle: Vehicle, edge_id: str, stop_position: float) -> bool:
        return (self.validator.is_on_valid_lane(edge_id) and
                self.validator.is_allowed_on_lane(vehicle, edge_id) and
                self.validator.is_accident_routable_for_emergency_vehicle(vehicle, edge_id, stop_position) and
                edge_id != self.accident_settings.EMERGENCY_DROP_OFF)


class FalseReportService:
    """Handles logic for false accident reports"""
    
    def __init__(self, context: SimulationContext, validator: ICollisionValidator, constraints: CollisionConstraints):
        self.context = context
        self.validator = validator
        self.constraints = constraints
        self._logger = loguru_logger.bind(context="false_report_service")

    def are_false_report_constraints_met(self, time: int) -> bool:
        return time != 0 and time % Settings.INTERVAL_OF_FALSE_ACCIDENTS == 0

    def find_false_reporter(self, simulation_event_manager: SimulationEventManager) -> Tuple[Optional['SendersEntity'], Optional[Vehicle]]:
        # Get devices and authentic accidents
        devices = self.context._device_registry
        vehicles = devices.get_devices_by_group(DeviceType.VEHICLE)
        smart_phones = devices.get_devices_by_group(DeviceType.SMART_PHONE)
        authentic_accidents = simulation_event_manager.get_authentic_events_by_type(EventType.COLLISION)
        
        # Filter malicious devices as candidates
        candidates = {
            **{k: v for k, v in vehicles.items() if v._device_behaviour == DeviceBehaviour.MALICIOUS},
            **{k: v for k, v in smart_phones.items() if v._device_behaviour == DeviceBehaviour.MALICIOUS}
        }
        
        if not candidates or not authentic_accidents:
            return None, None
        
        # Extract positions
        candidate_ids = list(candidates.keys())
        candidate_positions = np.array([candidates[cid]._position for cid in candidate_ids])  # Shape: (n, 2)
        accident_locations = np.array([accident.location for accident in authentic_accidents.values()])  # Shape: (m, 2)
        
        # Compute pairwise distances between candidates and accidents
        # Shape: (n, m)
        distances = np.linalg.norm(candidate_positions[:, np.newaxis] - accident_locations, axis=2)
        
        # Find candidates at least 80 meters from all accidents
        valid_candidates_mask = np.all(distances >= self.constraints.nearby_accident_distance, axis=1)  # Shape: (n,)
        valid_candidate_ids = [candidate_ids[i] for i in range(len(candidate_ids)) if valid_candidates_mask[i]]
        
        if not valid_candidate_ids:
            return None, None
        
        # Shuffle valid candidates to maintain randomness (mimicking original random.choice)
        random.shuffle(valid_candidate_ids)
        
        # Try each valid candidate
        for reporter_id in valid_candidate_ids:
            reporter = candidates[reporter_id]
            assert isinstance(reporter, (Vehicle, SmartPhone)), "Reporter must be a Vehicle instance"
            
            surrounding_vehicles = network.get_surrounding_vehicles(reporter_id, reporter, devices)
            vehicle = self._find_valid_false_vehicle(simulation_event_manager, vehicles, surrounding_vehicles)
            
            if vehicle:
                return SendersEntity(reporter, AuthenticityRole.UNAUTHENTIC, ScenarioParameters.TIME), vehicle
        
        return None, None

    def _find_valid_false_vehicle(self, simulation_event_manager: SimulationEventManager, 
                                vehicles: Dict[str, Vehicle], surrounding_vehicles: Dict) -> Optional[Vehicle]:
        for veh_id, vehicle_data in surrounding_vehicles.items():
            vehicle = vehicles.get(veh_id)
            if vehicle and self._is_valid_fake_collision_vehicle(simulation_event_manager, vehicle, veh_id, vehicle_data):
                return vehicle
        return None

    def _is_valid_fake_collision_vehicle(self, simulation_event_manager: SimulationEventManager, 
                                       vehicle: Vehicle, veh_id: str, vehicle_data: Dict) -> bool:
        return (not simulation_event_manager.has_event_for_vehicle(veh_id) and
                vehicle_data.get('type') in self.accident_settings.ALLOWED_VEHICLE_FAKE_COLLISION_TYPES and
                self.validator.is_on_valid_lane(vehicle._edge_id) and
                self.validator.is_valid_lane_position(vehicle, vehicle._edge_id) and
                self.validator.is_allowed_on_lane(vehicle, vehicle._edge_id) and
                self.validator.is_accident_routable_for_emergency_vehicle(vehicle, vehicle._edge_id, 20) and
                vehicle._edge_id != self.accident_settings.EMERGENCY_DROP_OFF and
                not veh_id.startswith('emergency_veh'))

    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        import math
        return math.dist(pos1, pos2)



class SimulationEventHandler:
    """Manages simulation events including collisions and false reports"""
    
    def __init__(self, context: SimulationContext, collision_selector: ICollisionSelector, 
                 validator: ICollisionValidator, false_report_service: FalseReportService):
        self.context = context
        self.collision_selector = collision_selector
        self.validator = validator
        self.false_report_service = false_report_service
        self._logger = loguru_logger.bind(context="simulation_events")
        self._stdout_handler_id = None

    def trigger_collision(self, simulation_events: SimulationEventManager) -> None:
        """Trigger a legitimate collision event if conditions are met"""
        from core.models.devices.common import DeviceType
        import utils.simulation as simulation_utils
        from utils import pathfinder
        import random
        
        vehicles = self.context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        
        if not self.validator.is_valid_time_constraints(vehicles):
            return
        
        is_feasible, vehicle_key, vehicle, edge, position = self.collision_selector.select_collision_vehicle(
            vehicles, simulation_events
        )
        
        if not is_feasible or not vehicle or not vehicle_key:
            return
        
        self._logger.info(
            f"{self.context._current_time} | VALID COLLISION | "
            f"Vehicle: {vehicle_key}, Edge: {edge} at Position: {position}"
        )
        
        simulation_utils.stop_vehicle(vehicle_key, edge, position)
        
        event = SimulationEvent(
            catalyst_id=vehicle_key,
            event_type=EventType.COLLISION,
            location=vehicle._position,
            time=ScenarioParameters.TIME,
            is_authentic=True,
            state=EventState.SCHEDULED
        )
        simulation_events.add_event(event)
        
        debug_path = pathfinder.get_accident_debug_path(
            Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX
        )
        logger.write_pickle(f"{debug_path}/accident_{event.id}_Catalyst_{event.catalyst_id}.pickle", event)

    def update_collisions(self, simulation_event_manager: SimulationEventManager) -> None:
        """Update collision events and trigger associated behaviors"""
        from core.models.devices.common import DeviceType
        
        stopping_vehicles = traci.simulation.getStopStartingVehiclesIDList()
        scheduled_collisions = simulation_event_manager.get_scheduled_events(EventType.COLLISION)
        vehicles = self.context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        
        for veh_id in stopping_vehicles:
            vehicle = vehicles.get(veh_id)
            if vehicle:
                new_events = simulation_event_manager.get_new_collision_events(veh_id, scheduled_collisions, vehicle)
                self._trigger_collision_behavior(new_events, vehicle)

    def report_false_accident(self, simulation_event_manager: SimulationEventManager, report_manager: ReportManager) -> None:
        """Generate a false accident report if conditions are met"""
        from core.models.devices.common import DeviceType
        
        if not self.false_report_service.are_false_report_constraints_met(ScenarioParameters.TIME):
            return
        
        reporter, vehicle = self.false_report_service.find_false_reporter(simulation_event_manager)
        if reporter and vehicle:
            event = simulation_event_manager.create_event(
                reporter.id, vehicle, EventType.COLLISION, authenticity=False, event_state=EventState.SCHEDULED
            )
            simulation_event_manager.add_event(event)
            
            emergency_center = self.context._device_registry.get_devices_by_group(DeviceType.EMERGENCY_CENTER)
            report = report_manager.create_report(
                {reporter.id: reporter}, event, vehicle, emergency_center, ReportType.EmergencyReport
            )
            report_manager.add(report)
            
            self._logger.info(
                f"{ScenarioParameters.TIME} | FAKE REPORT | "
                f"Vehicle: {report.object_of_interest.object_id}, Edge: {report.object_of_interest.edge_id} "
                f"at Position: {report.object_of_interest.lane_position}; Reporter: {list(report.sending_entities.keys())}"
            )

    def report_accidents(self, simulation_event_manager: SimulationEventManager, 
                        report_manager: ReportManager, devices) -> None:
        """Report legitimate accidents to the emergency center"""

        collisions = simulation_event_manager.get_events_by_type(EventType.COLLISION)
        
        for event_id, event in collisions.items():
            if not event.is_valid_accident():
                continue
            
            report = report_manager.get_report(event.catalyst_id)
            accident_vehicle = simulation_event_manager.get_catalyst_vehicle(event)
            
            if report is None and accident_vehicle:
                reporters = network.get_reporters(event, devices)
                filtered_reporters = get_suitable_reporters(reporters, collisions)
                
                if not filtered_reporters:
                    continue
                
                emergency_center = self.context._device_registry.get_devices_by_group(DeviceType.EMERGENCY_CENTER)
                report = report_manager.create_report(
                        filtered_reporters,
                        event,
                        accident_vehicle, 
                        emergency_center,
                        ReportType.EmergencyReport
                )
                report_manager.add(report)
                
                self._logger.info(
                    f"{ScenarioParameters.TIME} | REPORT COLLISION | "
                    f"Vehicle: {report.object_of_interest.object_id}, Edge: {report.object_of_interest.edge_id} "
                    f"at Position: {report.object_of_interest.lane_position}; Reporter: {list(report.sending_entities.keys())}"
                )
                assert isinstance(accident_vehicle._position, tuple) and len(accident_vehicle._position) == 2, "Accident vehicle position must be a tuple of (x, y)"
                
                event._update_state(EventRecord(
                    event_id=event.id, 
                    state=EventState.REPORTED, 
                    time=ScenarioParameters.TIME, 
                    location=accident_vehicle._position
                ))
            
            elif report:
                reporters = network.get_reporters(event, devices)
                filtered_reporters = get_suitable_reporters(reporters, collisions)
                if filtered_reporters:
                    new_reporters = get_new_reporters(filtered_reporters, report)
                    report.add_reporters(new_reporters)

    def request_fake_traffic_light_priority(self, report_manager: ReportManager, 
                                           simulation_event_manager: SimulationEventManager) -> None:
        """Request fake traffic light priority for malicious vehicles"""

        
        if not self._met_time_and_vehicles_preconditions():
            return
        
        vehicles = self.context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        selected_vehicles = {
            k: v for k, v in vehicles.items() 
            if v._device_behavior_profile._ground_truth == DeviceBehaviour.MALICIOUS
        }


        malicious_vehicles : Dict[str, Vehicle] = {k: v for k, v in selected_vehicles.items() if isinstance(v, Vehicle) and isinstance(k, str)}


        requestor_id = self._select_vehicle(malicious_vehicles)
        if requestor_id and requestor_id in malicious_vehicles:
            malicious_vehicles[requestor_id].request_fake_traffic_lights_on_route(
                report_manager, malicious_vehicles, simulation_event_manager, authenticity=False
            )

    def _trigger_collision_behavior(self, events: Dict[str, SimulationEvent], vehicle: Vehicle) -> None:
        """Trigger collision behavior for specified events"""
        
        assert isinstance(vehicle._position, tuple) and len(vehicle._position) == 2, "Vehicle position must be a tuple of (x, y)"
        
        
        for event_id, event in events.items():
            event_record = EventRecord(
                event_id=event.id, 
                state=EventState.TRIGGERED, 
                time=ScenarioParameters.TIME, 
                location=vehicle._position
            )
            event._update_state(event_record)
            enable_accident_behaviour(event)

    def _met_time_and_vehicles_preconditions(self) -> bool:
        """Check if time and vehicle preconditions are met"""
        from core.models.devices.common import DeviceType
        vehicles = self.context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        return (len(vehicles) > 0 and 
                ScenarioParameters.TIME != 0 and 
                ScenarioParameters.TIME % Settings.INTERVAL_OF_ACCIDENTS == 0)

    def _select_vehicle(self, vehicles: Dict[str, Vehicle]) -> Optional[str]:
        """Select a random vehicle from the available vehicles"""
        import random
        if not vehicles:
            return None
        return random.choice(list(vehicles.keys()))

    def toggle_logging_stdout(self, activate: bool = True) -> None:
        """Toggle stdout logging for simulation events"""
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = loguru_logger.add(
                sys.stdout, 
                filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "simulation_events"
            )
        elif not activate and self._stdout_handler_id is not None:
            loguru_logger.remove(self._stdout_handler_id)
            self._stdout_handler_id = None