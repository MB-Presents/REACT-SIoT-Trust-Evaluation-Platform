from __future__ import annotations
import itertools
from typing import TYPE_CHECKING, Any, Dict, List, Union, Tuple, Protocol
import numpy as np
from traci import edge, lane, vehicle, vehicletype, exceptions
from traci.constants import VAR_SPEED, VAR_POSITION, VAR_ROAD_ID, VAR_LANE_ID, VAR_LANEPOSITION, VAR_LANE_INDEX, VAR_COLOR, VAR_SIGNALS

from core.data_alteration.alterations.device_data_alteration import modify_device_data
from core.models.devices.common import DeviceBehaviour, DeviceType
from core.models.uniform.sensed_record import SensedDeviceRecord
from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import TrafficLightApplicationSettings
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.devices.device_handler import DevicesGroupHandler
    from models.devices.induction_loop import InductionLoop
    from models.devices.traffic_camera import TrafficCamera
    from models.devices.vehicle import Vehicle
    from models.devices.smart_phone import SmartPhone


class IDeviceDataService(Protocol):
    """Protocol for device data services."""
    
    def get_vehicle_dimensions(self, veh_id: str) -> Dict[str, float]:
        """Get vehicle dimensions."""
        ...
    
    def get_vehicle_color(self, veh_id: str) -> Tuple[float, ...]:
        """Get vehicle color."""
        ...
    
    def get_object_position(self, veh_id: str) -> Tuple[float, float, float]:
        """Get vehicle position."""
        ...


class ITrafficDataService(Protocol):
    """Protocol for traffic data services."""
    
    def get_vehicle_count(self, identifier: str, is_edge: bool = True) -> int:
        """Get vehicle count on edge or lane."""
        ...
    
    def get_vehicle_ids(self, identifier: str, is_edge: bool = True) -> List[str]:
        """Get vehicle IDs on edge or lane."""
        ...


class DeviceDataService:
    """Service for handling device-specific data operations."""
    
    def __init__(self, devices_handler: DevicesGroupHandler):
        self._devices_handler = devices_handler
    
    def get_vehicle_dimensions(self, veh_id: str) -> Dict[str, float]:
        """Return the dimensions of a vehicle, or NaN if not found."""
        vehicles: Dict[str, Vehicle] = self._devices_handler.get_devices_by_group(DeviceType.VEHICLE)
        
        if veh_id not in vehicles:
            return {'width': np.nan, 'length': np.nan, 'height': np.nan}
        
        vehicle = vehicles[veh_id]
        return {
            'width': vehicle._width,
            'length': vehicle._length,
            'height': vehicle._height
        }
    
    def get_vehicle_color(self, veh_id: str) -> Tuple[float, ...]:
        """Return the color of a vehicle based on its type."""
        vehicle_type = vehicle.getTypeID(veh_id)
        return vehicletype.getColor(vehicle_type)
    
    def get_object_position(self, veh_id: str) -> Tuple[float, float, float]:
        """Return the 3D position of a vehicle."""
        return vehicle.getPosition3D(veh_id)
    
    def get_vehicle_class(self, veh_id: str) -> str:
        """Return the vehicle class for a given vehicle ID."""
        try:
            vehicle_type = vehicle.getTypeID(veh_id)
            if vehicle_type == 'veh_passenger':
                return vehicletype.getVehicleClass(vehicle_type)
            return vehicle_type
        except exceptions.TraCIException as e:
            raise exceptions.TraCIException(f"Failed to get vehicle class for {veh_id}: {str(e)}")
    
    def get_vehicle_license_plate(self, veh_id: str) -> str:
        """Return the license plate of a vehicle (same as vehicle ID)."""
        return str(veh_id)


class TrafficDataService:
    """Service for handling traffic-related data operations."""
    
    def get_vehicle_count(self, identifier: str, is_edge: bool = True) -> int:
        """Return the number of vehicles on an edge or lane."""
        return (edge.getLastStepVehicleNumber(identifier) if is_edge 
                else lane.getLastStepVehicleNumber(identifier))
    
    def get_vehicle_ids(self, identifier: str, is_edge: bool = True) -> List[str]:
        """Return the IDs of vehicles on an edge or lane."""
        return (edge.getLastStepVehicleIDs(identifier) if is_edge 
                else lane.getLastStepVehicleIDs(identifier))


class VehicleStatusService:
    """Service for updating vehicle status and position data."""
    
    def update_vehicle_status(self, vehicle: Vehicle, vehicle_data: Dict) -> None:
        """Update a vehicle's attributes based on provided data."""
        vehicle._speed = vehicle_data[VAR_SPEED]
        vehicle._position = vehicle_data[VAR_POSITION]
        vehicle._edge_id = vehicle_data[VAR_ROAD_ID]
        vehicle._lane_id = vehicle_data[VAR_LANE_ID]
        vehicle._lane_position = vehicle_data[VAR_LANEPOSITION]
        vehicle._lane_index = vehicle_data[VAR_LANE_INDEX]
        vehicle._color = vehicle_data[VAR_COLOR]
        vehicle._signal = vehicle_data.get(VAR_SIGNALS, 0)
    
    def update_mobile_device_position(self, device: Union[SmartPhone, Vehicle], device_data: Dict) -> None:
        """Update position-related attributes for a mobile device."""
        device._speed = device_data[VAR_SPEED]
        device._position = device_data[VAR_POSITION]
        device._edge_id = device_data[VAR_ROAD_ID]
        device._lane_id = device_data[VAR_LANE_ID]
        device._lane_position = device_data[VAR_LANEPOSITION]
        
        if device._type == DeviceType.VEHICLE:
            device._lane_index = device_data[VAR_LANE_INDEX]


class VehicleDetectionService:
    """Service for vehicle detection operations."""
    
    def __init__(self, devices_handler: DevicesGroupHandler, device_data_service: DeviceDataService):
        self._devices_handler = devices_handler
        self._device_data_service = device_data_service
    
    def get_inductive_object_count(self, induction_loop: InductionLoop) -> Dict[str, Dict]:
        """Retrieve vehicles detected by an induction loop with their attributes."""
        vehicles: Dict[str, Vehicle] = self._devices_handler.get_devices_by_group(DeviceType.VEHICLE)
        vehicle_ids = edge.getLastStepVehicleIDs(induction_loop._observed_street)
        
        captured_vehicles = {
            veh_id: {
                'device_id': veh_id,
                'dimension': self._device_data_service.get_vehicle_dimensions(veh_id),
                'speed': vehicles[veh_id]._speed,
                'lanePosition': vehicles[veh_id]._lane_position,
                'laneIndex': vehicles[veh_id]._lane_index,
                'laneID': vehicles[veh_id]._lane_id,
                'edgeID': vehicles[veh_id]._edge_id
            }
            for veh_id in vehicle_ids if veh_id in vehicles
        }
        
        induction_loop._captured_vehicles_features = captured_vehicles
        return captured_vehicles
    
    def get_detected_vehicles(self, traffic_camera: TrafficCamera) -> Dict[str, Vehicle]:
        """Retrieve vehicles detected by a traffic camera across observed streets."""
        traffic_camera._captured_vehicles = {}
        vehicles = self._devices_handler.get_devices_by_group(DeviceType.VEHICLE)

        for observed_edge in traffic_camera._observed_streets:
            for veh_id in edge.getLastStepVehicleIDs(observed_edge):
                if veh_id.startswith("ped") or veh_id.startswith("bike"):
                    continue
                if veh_id in vehicles:
                    traffic_camera._captured_vehicles[veh_id] = vehicles[veh_id]
        
        return traffic_camera._captured_vehicles


class ProximityDetectionService:
    """Service for proximity-based vehicle detection."""
    
    def __init__(self, devices_handler: DevicesGroupHandler):
        self._devices_handler = devices_handler
    
    def get_surrounding_vehicles(self, device: Union[SmartPhone, Vehicle]) -> Dict[str, Vehicle]:
        """Retrieve vehicles within the sensing range of a device."""
        vehicles: Dict[str, Vehicle] = self._devices_handler.get_devices_by_group(DeviceType.VEHICLE)
        
        if not vehicles:
            return {}
        
        vehicle_positions = np.array([veh._position for veh in vehicles.values()])
        device_position = np.array(device._position)
        distances = np.linalg.norm(vehicle_positions - device_position, axis=1)
        distance_threshold = TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING
        
        return {
            veh_id: vehicles[veh_id]
            for veh_id, dist in zip(vehicles.keys(), distances)
            if dist <= distance_threshold
        }


class SensingService:
    """Service for handling device sensing operations."""
    
    def __init__(self, devices_handler: DevicesGroupHandler, proximity_service: ProximityDetectionService):
        self._devices_handler = devices_handler
        self._proximity_service = proximity_service
    
    def get_detected_objects(self, device: Union[SmartPhone, Vehicle]) -> None:
        """Update the sensed vehicles for a device, applying data modification if malicious."""
        sensed_vehicles = self._proximity_service.get_surrounding_vehicles(device)
        sensed_records = {}
        id_counter = itertools.count()

        vehicles: Dict[str, Vehicle] = self._devices_handler.get_devices_by_group(DeviceType.VEHICLE)

        for veh_id, vehicle in sensed_vehicles.items():
            if veh_id not in vehicles:
                continue
            sensed_device = modify_device_data(vehicle) if device._behaviour == DeviceBehaviour.MALICIOUS else vehicle
            self._add_sensed_device_record(sensed_records, id_counter, device, sensed_device)
        
        device._sensed_devices = sensed_records
    
    def _add_sensed_device_record(self, record_table: Dict, id_counter: itertools.count, 
                                 provider: Union[SmartPhone, Vehicle], device: GenericDevice) -> None:
        """Add a sensed device record to the provided table."""
        record = SensedDeviceRecord(provider, device)
        key = (ScenarioParameters.TIME, provider._id, device._id)
        record_table[key] = record.__dict__


class DeviceFunctionsFacade:
    """Facade class that provides a unified interface to all device functions."""
    
    def __init__(self, devices_handler: DevicesGroupHandler):
        self._device_data_service = DeviceDataService(devices_handler)
        self._traffic_data_service = TrafficDataService()
        self._vehicle_status_service = VehicleStatusService()
        self._vehicle_detection_service = VehicleDetectionService(devices_handler, self._device_data_service)
        self._proximity_service = ProximityDetectionService(devices_handler)
        self._sensing_service = SensingService(devices_handler, self._proximity_service)
    
    @property
    def device_data(self) -> DeviceDataService:
        return self._device_data_service
    
    @property
    def traffic_data(self) -> TrafficDataService:
        return self._traffic_data_service
    
    @property
    def vehicle_status(self) -> VehicleStatusService:
        return self._vehicle_status_service
    
    @property
    def vehicle_detection(self) -> VehicleDetectionService:
        return self._vehicle_detection_service
    
    @property
    def proximity(self) -> ProximityDetectionService:
        return self._proximity_service
    
    @property
    def sensing(self) -> SensingService:
        return self._sensing_service