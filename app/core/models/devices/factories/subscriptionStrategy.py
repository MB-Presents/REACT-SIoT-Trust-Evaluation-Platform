


from typing import Dict
from git import Optional
from pyparsing import ABC, abstractmethod
import traci

from core.models.devices.common import DeviceType
from core.simulation.adapter.subscription_adapter import SubscriptionAdapter
from scenarios.canberra_case_study.core.scenario_config import ScenarioDeviceConfiguration
from loguru import logger

class ISubscription(ABC):
    
    @abstractmethod
    def subscribe(self) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, device_id: str) -> None:
        pass


class SubscriptionManager:
    def __init__(self, traci_adapter: SubscriptionAdapter):
        self._strategies: Dict[DeviceType, ISubscription] = {}
        self.traci_adapter = traci_adapter
        self._register_strategies()

    def _register_strategies(self):
        self._strategies[DeviceType.VEHICLE] = VehicleSubscriptionStrategy(
            self.traci_adapter)
        self._strategies[DeviceType.SMART_PHONE] = SmartPhoneSubscriptionStrategy(
            self.traci_adapter)
        self._strategies[DeviceType.TRAFFIC_LIGHT] = TrafficLightSubscriptionStrategy(
            self.traci_adapter)

    def subscribe(self, device_type: DeviceType) -> None:
        strategy = self._strategies.get(device_type)
        if not strategy:
            raise ValueError(
                f"No subscription strategy for device type {device_type}")
        strategy.subscribe()

    def unsubscribe(self, device_type: DeviceType, device_id: str) -> None:
        strategy = self._strategies.get(device_type)
        if not strategy:
            raise ValueError(
                f"No subscription strategy for device type {device_type}")
        strategy.unsubscribe(device_id)





class VehicleSubscriptionStrategy(ISubscription):

    def __init__(self, traci_adapter: SubscriptionAdapter):
        self.traci_adapter = traci_adapter

    def subscribe(self, config: Optional[dict] = None) -> None:
        device_id: str
        for device_id in traci.simulation.getDepartedIDList():
            if device_id.startswith("ped") or device_id.startswith("bike"):
                continue  # Skip pedestrians and bikes
            features = ScenarioDeviceConfiguration.VEHICLE_FEATURES
        try:
            self.traci_adapter.subscribe_vehicle(device_id, features)
            logger.info(f"Subscribed vehicle: {device_id}")
        except Exception as e:
            logger.error(f"Failed to subscribe vehicle {device_id}: {str(e)}")
            raise

    def unsubscribe(self, device_id: str) -> None:
        try:
            self.traci_adapter.unsubscribe_vehicle(device_id)
            logger.info(f"Unsubscribed vehicle: {device_id}")
        except Exception as e:
            logger.error(
                f"Failed to unsubscribe vehicle {device_id}: {str(e)}")
            raise


class SmartPhoneSubscriptionStrategy(ISubscription):
    def __init__(self, traci_adapter: SubscriptionAdapter):
        self.traci_adapter = traci_adapter

    def subscribe(self ) -> None:
        try:
            
            for departed_person in traci.simulation.getDepartedPersonIDList():
                traci.person.subscribe(departed_person, ScenarioDeviceConfiguration.SMART_PHONE_FEATURES)
            
            device_id: str
            for device_id in traci.simulation.getDepartedIDList():
                if device_id.startswith("bike"):
                    self.traci_adapter.subscribe_vehicle(device_id, ScenarioDeviceConfiguration.VEHICLE_FEATURES)
                logger.info(f"Subscribed smartphone: {device_id}")
        except Exception as e:
            logger.error(
                f"Failed to subscribe smartphone {device_id}: {str(e)}")
            raise

    def unsubscribe(self, device_id: str) -> None:
        try:
            if device_id.startswith("bike"):
                self.traci_adapter.unsubscribe_vehicle(device_id)
            else:
                self.traci_adapter.unsubscribe_person(device_id)
            logger.info(f"Unsubscribed smartphone: {device_id}")
        except Exception as e:
            logger.error(
                f"Failed to unsubscribe smartphone {device_id}: {str(e)}")
            raise


class TrafficLightSubscriptionStrategy(ISubscription):
    def __init__(self, traci_adapter: SubscriptionAdapter):
        self.traci_adapter = traci_adapter

    def subscribe(self) -> None:
        
        try:
            for traffic_light_id in traci.trafficlight.getIDList():
                self.traci_adapter.subscribe_traffic_light(
                    traffic_light_id, ScenarioDeviceConfiguration.TRAFFIC_LIGHT_FEATURES)
                logger.info(f"Subscribed traffic light: {traffic_light_id}")
        except Exception as e:
            logger.error(
                f"Failed to subscribe traffic light {traffic_light_id}: {str(e)}")
            raise

    def unsubscribe(self, device_id: str) -> None:
        try:
            self.traci_adapter.unsubscribe_traffic_light(device_id)
            logger.info(f"Unsubscribed traffic light: {device_id}")
        except Exception as e:
            logger.error(
                f"Failed to unsubscribe traffic light {device_id}: {str(e)}")
            raise