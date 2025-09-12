
from typing import Optional

from core.models.devices.factories.behaviour_factory import DeviceBehaviourFactory
from core.models.devices.factories.computation_factory import ComputationCapabilityFactory
from core.models.devices.factories.device_profile_facade import DeviceProfileFactory
from core.models.devices.factories.service_factory import ServiceFactory
from core.models.events.simulation_events import SimulationEventManager
from core.models.interfaces.device_registry import IDeviceRegistry
from core.models.interfaces.report_provider import IReportProvider
from core.simulation.event_bus.event_bus import EventBus
from scenarios.canberra_case_study.apps.handler import ScenarioHandler


class SimulationContext:
    """Central context providing access to simulation services"""
    
    def __init__(self):
        self._event_bus = EventBus()
        self._device_registry: IDeviceRegistry
        self._service_factory: ServiceFactory 
        self._device_behaviour_factory: DeviceBehaviourFactory 
        self._device_profile_factory: DeviceProfileFactory 
        self._computation_capability_factory: ComputationCapabilityFactory 

        self._report_provider: IReportProvider 
        self._simulation_event_manager: SimulationEventManager 
        
        self._scenario_handler : ScenarioHandler
        
        self._current_time: float = 0.0 


    def register_report_provider(self, provider: IReportProvider) -> None:
        self._report_provider = provider
    
    def register_device_registry(self, registry: IDeviceRegistry) -> None:
        self._device_registry = registry
        
    def register_service_factory(self, factory: ServiceFactory) -> None:
        self._service_factory = factory
        
    def register_device_behaviour_factory(self, factory: DeviceBehaviourFactory) -> None:
        self._device_behaviour_factory = factory
        
    def register_device_profile_factory(self, factory: DeviceProfileFactory) -> None:
        self._device_profile_factory = factory
        
    def register_computation_capability_factory(self, factory: ComputationCapabilityFactory) -> None:
        self._computation_capability_factory = factory
        
    def register_simulation_event_manager(self, event_manager : SimulationEventManager) -> None:
        self._simulation_event_manager = event_manager
        
    def register_scenario_handler(self, handler : ScenarioHandler) -> None:
        self._scenario_handler = handler
            
    
        
        
    def get_device_registry(self) -> IDeviceRegistry:
        if not self._device_registry:
            raise RuntimeError("Device registry not registered")
        return self._device_registry
        
    def get_service_factory(self) -> ServiceFactory:
        if not self._service_factory:
            raise RuntimeError("Service factory not registered")
        return self._service_factory
        
    def get_device_behaviour_factory(self) -> DeviceBehaviourFactory:
        if not self._device_behaviour_factory:
            raise RuntimeError("Device behaviour factory not registered")
        return self._device_behaviour_factory
        
    def get_device_profile_factory(self) -> DeviceProfileFactory:
        if not self._device_profile_factory:
            raise RuntimeError("Device profile factory not registered")
        return self._device_profile_factory
        
    def get_computation_capability_factory(self) -> ComputationCapabilityFactory:
        if not self._computation_capability_factory:
            raise RuntimeError("Computation capability factory not registered")
        return self._computation_capability_factory
        
    def get_event_bus(self) -> EventBus:
        return self._event_bus