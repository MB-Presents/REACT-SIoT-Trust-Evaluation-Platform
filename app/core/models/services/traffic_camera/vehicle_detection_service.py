
from __future__ import annotations
from typing import TYPE_CHECKING, Dict


from typing import Dict


from core.models.devices.common import DeviceType
from core.models.devices.device_handler import DevicesGroupHandler
from core.models.interfaces.function import IFunction
from core.models.interfaces.service import IService
import traci

from core.models.services.base_service import BaseService

if TYPE_CHECKING:
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.vehicle import Vehicle


class VehicleDetectionService(BaseService):
    
    def __init__(self):
        self._functions : Dict[str, IFunction]


    def get(self, device : TrafficCamera) -> Dict[str, Vehicle]:
        """Retrieve vehicles detected by a traffic camera across observed streets."""
        device._captured_vehicles = {}

        assert self.simulation_context._device_registry, "Device registry is not initialized in the simulation context."
        vehicles = self.simulation_context._device_registry.get_devices_by_group(DeviceType.VEHICLE)
        assert vehicles is not None, "No vehicles found in the device registry."
        assert all(isinstance(v, Vehicle) for v in vehicles.values()), "All registered vehicles must be of type Vehicle."
        
        # DevicesGroupHandler().get_devices_by_group(DeviceType.VEHICLE)


        for observed_edge in device._observed_streets:
            # veh_id : str
            for veh_id in traci.edge.getLastStepVehicleIDs(observed_edge):
                
                assert isinstance(veh_id, str), f"Expected veh_id to be a string, got {type(veh_id)}"
                
                vehicle  = vehicles[veh_id]
                
                assert isinstance(vehicle, Vehicle), f"Expected identified_vehicle to be of type Vehicle, got {type(vehicle)}"
                assert vehicle._id == veh_id, f"Identified Vehicle ID mismatch: expected {veh_id}, got {vehicle._id}"

                device._captured_vehicles[veh_id] = vehicle
                
        return device._captured_vehicles
        
        
        
        
    
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

