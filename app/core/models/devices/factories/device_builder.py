from __future__ import annotations
import itertools
from typing import Any, Dict, List, Optional, Union, Tuple, Protocol, TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import random

# Import your existing types (assumed structure based on your code)
from enum import Enum

from core.models.devices.common import DeviceType
from core.models.devices.factories.device_creation_context import DeviceCreationContext
from core.models.devices.induction_loop import InductionLoop
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.traffic_camera import TrafficCamera
from core.models.devices.traffic_light import TrafficLightSystem
from core.models.devices.vehicle import Vehicle
from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice


class DeviceBuilder:
    """Builder pattern for creating devices with all dependencies"""
    
    def __init__(self, context: DeviceCreationContext):
        self.context = context
        self._device: Optional[GenericDevice] = None
        
    def create_base_device(self) -> DeviceBuilder:
        """Create the base device based on type"""
        config = self.context.config
        
        if self.context.device_type == DeviceType.VEHICLE:
            self._device = Vehicle(
                veh_id=self.context.device_id,
                speed=config.get('speed', 0.0),
                position=config.get('position', [0.0, 0.0]),
                signal=config.get('signal'),
                edge_id=config.get('edge_id', ''),
                lane_id=config.get('lane_id', ''),
                color=self.context.color or (0.0, 0.0, 0.0),
                lane_position=config.get('lane_position', 0.0),
                vehicle_type=config.get('vehicle_type', ''),
                width=config.get('width', 0.0),
                height=config.get('height', 0.0),
                length=config.get('length', 0.0),
                lane_index=config.get('lane_index', 0),
                vehicle_class=config.get('vehicle_class', ''),
                device_behaviour=self.context.device_behaviour,
                simulation_context=self.context.simulation_context
            )
            
        elif self.context.device_type == DeviceType.SMART_PHONE:
            self._device = SmartPhone(
                smart_phone_id=self.context.device_id,
                position=config.get('position', [0.0, 0.0]),
                speed=config.get('speed', 0.0),
                lane_position=config.get('lane_position', 0.0),
                edge_id=config.get('edge_id', ''),
                lane_id=config.get('lane_id', ''),
                device_behaviour=self.context.device_behaviour,
                simulation_context=self.context.simulation_context
            )
            
        elif self.context.device_type == DeviceType.INDUCTION_LOOP:
            self._device = InductionLoop(
                induction_loop_id=self.context.device_id,
                observedStreet=config.get('edgeID', ''),
                position=config.get('position', [0.0, 0.0]),
                color=self.context.color or (255, 0, 0),
                profile_config=config,
                simulation_context=self.context.simulation_context
            )
            
        elif self.context.device_type == DeviceType.TRAFFIC_CAMERA:
            self._device = TrafficCamera(
                camera_id=self.context.device_id,
                observedStreets=config.get('edgeID', []),
                position=config.get('position', [0.0, 0.0]),
                color=self.context.color or (0, 255, 0),
                simulation_context=self.context.simulation_context
            )
            
        elif self.context.device_type == DeviceType.TRAFFIC_LIGHT:
            self._device = TrafficLightSystem(
                traffic_light_id=self.context.device_id,
                position=self.context.position or (0.0, 0.0),
                profile=config.get('profile', {}),
                simulation_context=self.context.simulation_context
            )
            
        elif self.context.device_type == DeviceType.EMERGENCY_VEHICLE:
            self._device = EmergencyVehicle(
                emergency_id=self.context.device_id,
                emergency_vehicle_configuration=config,
                simulation_context=self.context.simulation_context
            )
            
        elif self.context.device_type == DeviceType.EMERGENCY_CENTER:
            self._device = EmergencyResponseCenter(
                device_id=self.context.device_id,
                device_type=self.context.device_type,
                color=self.context.color or (0, 0, 0),
                config=config,
                simulation_context=self.context.simulation_context
            )
        else:
         
            
            raise ValueError(f"Unsupported device type: {self.context.device_type}")   
            # self._device = GenericDevice(
            #     device_id=self.context.device_id,
            #     device_type=self.context.device_type,
            #     color=self.context.color,
            #     device_behaviour=self.context.device_behaviour,
            #     simulation_context=self.context.simulation_context
            # )
            
        return self
    
    def initialize_dependencies(self) -> DeviceBuilder:
        """Initialize device dependencies through context"""
        if self._device:
            self._device.initialize_dependencies()
        return self
    
    def configure_device_specifics(self) -> 'DeviceBuilder':
        """Apply device-type specific configuration"""
        if self.context.device_type == DeviceType.INDUCTION_LOOP:
            self._configure_induction_loop()
        elif self.context.device_type == DeviceType.TRAFFIC_CAMERA:
            self._configure_traffic_camera()
        elif self.context.device_type == DeviceType.SMART_PHONE:
            self._configure_smart_phone()
        elif self.context.device_type == DeviceType.VEHICLE:
            self._configure_vehicle()
        elif self.context.device_type == DeviceType.EMERGENCY_VEHICLE:
            self._configure_emergency_vehicle()
        elif self.context.device_type == DeviceType.TRAFFIC_LIGHT:
            self._configure_traffic_light()
        elif self.context.device_type == DeviceType.EMERGENCY_CENTER:
            self._configure_emergency_center()
            
        return self
    
    def inject_services(self) -> DeviceBuilder:
        """Inject services using the simulation context"""
        if self._device:
            try:
                service_factory = self.context.simulation_context.get_service_factory()
                services = service_factory.create_services_for_device(self._device)
                self._device.with_services(services)
            except Exception as e:
                print(f"Warning: Could not inject services for {self._device.get_device_id()}: {e}")
        return self
    
    def build(self) -> GenericDevice:
        """Return the built device"""
        if not self._device:
            raise ValueError("Device not created. Call create_base_device() first.")
        return self._device
    
    def _configure_induction_loop(self):
        """Configure induction loop specific properties"""
        config = self.context.config
        observed_street = config.get('edgeID', '')
        
        # Set device-specific properties
        self._device.set_property('observed_street', observed_street)
        self._device.set_property('captured_vehicles', [])
        
        # Add to simulation if position is available
        if self._device._position and hasattr(self.context.simulation_context, 'add_poi'):
            self.context.simulation_context.add_poi(
                self._device._id,
                self._device._position[0],
                self._device._position[1],
                self._device._color,
                poi_type=self._device._type.name
            )
    
    def _configure_traffic_camera(self):
        """Configure traffic camera specific properties"""
        config = self.context.config
        observed_streets = config.get('edgeID', [])
        
        self._device.set_property('observed_streets', observed_streets)
        self._device.set_property('captured_vehicles', [])
    
    def _configure_smart_phone(self):
        """Configure smartphone specific properties"""
        config = self.context.config
        
        # TraCI-specific properties for smartphones
        self._device.set_property('speed', config.get('speed', 0.0))
        self._device.set_property('edge_id', config.get('edge_id', ''))
        self._device.set_property('lane_id', config.get('lane_id', ''))
        self._device.set_property('lane_position', config.get('lane_position', 0.0))
    
    def _configure_vehicle(self):
        """Configure vehicle specific properties"""
        config = self.context.config
        
        # Vehicle-specific properties from TraCI
        properties = {
            'speed': config.get('speed', 0.0),
            'edge_id': config.get('edge_id', ''),
            'lane_id': config.get('lane_id', ''),
            'lane_position': config.get('lane_position', 0.0),
            'lane_index': config.get('lane_index', 0),
            'signal': config.get('signal', 0),
            'vehicle_type': config.get('type', ''),
            'length': config.get('length', 0.0),
            'width': config.get('width', 0.0),
            'height': config.get('height', 0.0),
            'vehicle_class': config.get('vehicle_class', '')
        }
        
        for key, value in properties.items():
            self._device.set_property(key, value)
    
    def _configure_emergency_vehicle(self):
        """Configure emergency vehicle (extends vehicle configuration)"""
        self._configure_vehicle()
        self._device.set_property('is_emergency', True)
        self._device.set_property('emergency_signals', True)
    
    def _configure_traffic_light(self):
        """Configure traffic light specific properties"""
        config = self.context.config
        self._device.set_property('controlled_lanes', config.get('controlled_lanes', []))
        self._device.set_property('current_phase', config.get('current_phase', 0))
    
    def _configure_emergency_center(self):
        """Configure emergency response center"""
        config = self.context.config
        self._device.set_property('coverage_area', config.get('coverage_area', []))
        self._device.set_property('response_capabilities', config.get('capabilities', []))
