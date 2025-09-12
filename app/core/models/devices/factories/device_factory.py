from __future__ import annotations
import itertools
from typing import Any, Dict, List, Optional, Union, Tuple, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import random

# Import your existing types (assumed structure based on your code)
from enum import Enum

from core.models import devices
from core.models.devices.common import DeviceBehaviour, DeviceType
from core.models.devices.factories.device_builder import DeviceBuilder
from core.models.devices.factories.device_creation_context import DeviceCreationContext
from core.models.devices.genric_iot_device import GenericDevice
from core.simulation.simulation_context import SimulationContext
from scenarios.canberra_case_study.core.devices import EMERGENCY_CENTER_SPECIFICATION, EMERGENCY_VEHS, INDUCTION_SENSOR_SPECIFICATION, TRAFFIC_CAMERA_SPECIFICATION

class DeviceFactory:
    """Main device factory using builder pattern"""
    
    def __init__(self, simulation_context: SimulationContext):
        self.simulation_context = simulation_context
        self._id_counters: Dict[DeviceType, itertools.count] = {
            device_type: itertools.count(0) for device_type in DeviceType
        }
        
        self.device_configs = {
            DeviceType.INDUCTION_LOOP: INDUCTION_SENSOR_SPECIFICATION,
            DeviceType.TRAFFIC_CAMERA: TRAFFIC_CAMERA_SPECIFICATION,
            DeviceType.EMERGENCY_CENTER: EMERGENCY_CENTER_SPECIFICATION,
            DeviceType.EMERGENCY_VEHICLE: EMERGENCY_VEHS
        }
    
    def _get_device_configuration(self, device_type: DeviceType) -> List[Dict[str, Any]]:
        """Load device-type specific configurations"""
        
        
        
        assert self.device_configs is not None, "Device configurations must be loaded"
        assert device_type in self.device_configs.keys(), f"Unsupported device type: {device_type}"  

        device_configuration = self.device_configs[device_type]

        assert device_configuration is not None, f"Configuration for {device_type} must not be None"

        return device_configuration
    


    def create_device(self, 
                     device_type: DeviceType, 
                     config: Dict[str, Any] = {},
                     device_id: str = "") -> GenericDevice:
        """Create a single device of the specified type"""
        
        if not device_id:
            device_id = f"{device_type.value}_{next(self._id_counters[device_type])}"
        
        # Create device creation context
        context = DeviceCreationContext(
            simulation_context=self.simulation_context,
            device_id=device_id,
            device_type=device_type,
            config=config or {},
            position=config.get('position') if config else None,
            color=config.get('color') if config else None,
            device_behaviour=config.get('device_behaviour', DeviceBehaviour.TRUSTWORTHY) if config else DeviceBehaviour.TRUSTWORTHY
        )
        
        # Use builder pattern to create device
        builder = DeviceBuilder(context)
        device = (builder
                 .create_base_device()
                 .initialize_dependencies()
                 .inject_services()
                 .build())
        
        return device
    
    def create_device_group(self, device_type: DeviceType) -> Dict[str, GenericDevice]:
        """Create a group of devices of the specified type"""
        devices = {}
        
        if device_type == DeviceType.INDUCTION_LOOP:
            devices = self._create_induction_loop_group()
        elif device_type == DeviceType.TRAFFIC_CAMERA:
            devices = self._create_traffic_camera_group()
        elif device_type == DeviceType.TRAFFIC_LIGHT:
            devices = self._create_traffic_light_group()
        elif device_type == DeviceType.EMERGENCY_CENTER:
            devices = self._create_emergency_center_group()
        elif device_type == DeviceType.EMERGENCY_VEHICLE:
            devices = self._create_emergency_vehicle_group()
        # VEHICLE and SMART_PHONE are created dynamically during simulation
        
        return devices
    
    def _create_induction_loop_group(self) -> Dict[str, GenericDevice]:
        """Create induction loop group from specifications"""
        devices = {}
        
        # This would use your INDUCTION_SENSOR_SPECIFICATION
        specifications = self._get_device_configuration(DeviceType.INDUCTION_LOOP)

        for spec in specifications:
            device = self.create_device(
                DeviceType.INDUCTION_LOOP,
                config=spec
            )
            devices[device.get_device_id()] = device
            
        return devices
    
    def _create_traffic_camera_group(self) -> Dict[str, GenericDevice]:
        """Create traffic camera group from specifications"""
        devices = {}

        specifications = self._get_device_configuration(DeviceType.TRAFFIC_CAMERA)

        for spec in specifications:
            device = self.create_device(
                DeviceType.TRAFFIC_CAMERA,
                config=spec
            )
            devices[device.get_device_id()] = device
            
        return devices
    
    def _create_traffic_light_group(self) -> Dict[str, GenericDevice]:
        """Create traffic light group from TraCI"""
        devices = {}
        
        # This would integrate with your TraCI calls
        traffic_light_ids = self._get_traffic_light_ids()
        
        for tl_id in traffic_light_ids:
            position = self._get_traffic_light_position(tl_id)
            device = self.create_device(
                DeviceType.TRAFFIC_LIGHT,
                config={'position': position},
                device_id=tl_id
            )
            devices[device.get_device_id()] = device
            
        return devices
    
    def _create_emergency_center_group(self) -> Dict[str, GenericDevice]:
        """Create emergency center group"""

        configs = self._get_device_configuration(DeviceType.EMERGENCY_CENTER)
        
        assert len(configs) == 1, "There should be exactly one emergency center configuration"
        
        devices = {}
        
        for config in configs:

            
            device = self.create_device(
                DeviceType.EMERGENCY_CENTER,
                config=config
            )
            devices[device.get_device_id()] = device

        return devices

    def _create_emergency_vehicle_group(self) -> Dict[str, GenericDevice]:
        """Create emergency vehicle group"""
        devices = {}
        
        # This would use your AccidentSettings.EMERGENCY_VEHS
        emergency_configs = self._get_device_configuration(DeviceType.EMERGENCY_VEHICLE)
        
        for config in emergency_configs:
            emergency_id = f"emergency_veh_{next(self._id_counters[DeviceType.EMERGENCY_VEHICLE])}"
            
            device = self.create_device(
                DeviceType.EMERGENCY_VEHICLE,
                config=config,
                device_id=emergency_id
            )
            devices[device.get_device_id()] = device
            
        return devices
    
