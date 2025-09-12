from abc import ABC, abstractmethod
from typing import Dict, Union
from core.models.devices.common import DeviceType
from core.models.devices.genric_iot_device import GenericDevice
from core.models.devices.induction_loop import InductionLoop
from core.models.devices.induction_loop import InductionLoop
from core.models.devices.smart_phone import SmartPhone
from core.models.devices.traffic_camera import TrafficCamera
from core.models.devices.traffic_light import TrafficLightSystem
from core.models.devices.vehicle import Vehicle
from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
import utils.logging as logger


class ILoggingStrategy(ABC):
    @abstractmethod
    def log(self, devices: Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, EmergencyVehicle, TrafficLightSystem]]) -> None:
        """Log the status and relevant data for a group of devices."""
        pass


class VehicleLoggingStrategy(ILoggingStrategy):

    def log(self, devices: Dict[str, Vehicle]) -> None:
        for device_id, vehicle in devices.items():
            try:
                message = vehicle.to_dict()
                
                
                logger.info(object_type=str(vehicle._type.name), message = message, log_object= logger.LoggingBehaviour.STATUS)
            except Exception as e:
                logger.error(DeviceType.VEHICLE.name, str(e))


class TrafficLightLoggingStrategy(ILoggingStrategy):
    def log(self, devices: Dict[str, TrafficLightSystem]) -> None:
        for device_id, traffic_light in devices.items():
            try:
                message = traffic_light.get_dict()  # Note: TrafficLightSystem uses get_dict()
                logger.info(DeviceType.TRAFFIC_LIGHT.name, message,
                            logger.LoggingBehaviour.STATUS)
            except Exception as e:
                logger.error(DeviceType.TRAFFIC_LIGHT.name, str(e))


class SmartPhoneLoggingStrategy(ILoggingStrategy):
    def log(self, devices: Dict[str, SmartPhone]) -> None:
        for device_id, smart_phone in devices.items():
            try:
                message = smart_phone.to_dict()
                logger.info(DeviceType.SMART_PHONE.name, message,
                            logger.LoggingBehaviour.STATUS)
            except Exception as e:
                logger.error(DeviceType.SMART_PHONE.name, str(e))


class TrafficCameraLoggingStrategy(ILoggingStrategy):
    def log(self, devices: Dict[str, TrafficCamera]) -> None:
        for device_id, traffic_camera in devices.items():
            try:
                message = traffic_camera.to_dict()
                logger.info(DeviceType.TRAFFIC_CAMERA.name, message,
                            logger.LoggingBehaviour.STATUS)
                for captured_vehicle_id, captured_vehicle in traffic_camera._captured_vehicles.items():
                    message = traffic_camera.sensed_objects_to_dict(
                        captured_vehicle_id, captured_vehicle)
                    logger.info(DeviceType.TRAFFIC_CAMERA.name, message,
                                logger.LoggingBehaviour.SENSING)
            except Exception as e:
                logger.error(DeviceType.TRAFFIC_CAMERA.name, str(e.__dict__))


class InductionLoopLoggingStrategy(ILoggingStrategy):
    def log(self, devices: Dict[str, InductionLoop]) -> None:
        for device_id, induction_loop in devices.items():
            try:
                message = induction_loop.to_dict()
                logger.info(DeviceType.INDUCTION_LOOP.name, message,
                            logger.LoggingBehaviour.STATUS)
                for captured_vehicle_id, captured_vehicle in induction_loop._captured_vehicles_features.items():
                    message = induction_loop.sensed_objects_to_dict(
                        captured_vehicle_id, captured_vehicle)
                    logger.info(DeviceType.INDUCTION_LOOP.name, message,
                                logger.LoggingBehaviour.SENSING)
            except Exception as e:
                logger.error(DeviceType.INDUCTION_LOOP.name, str(e))


class EmergencyResponseCenterLoggingStrategy(ILoggingStrategy):
    def log(self, devices: Dict[str, EmergencyResponseCenter]) -> None:
        for device_id, center in devices.items():
            try:
                message = center.to_dict()
                logger.info(DeviceType.EMERGENCY_CENTER.name, message,
                            logger.LoggingBehaviour.STATUS)
            except Exception as e:
                logger.error(DeviceType.EMERGENCY_CENTER.name, str(e))


class EmergencyVehicleLoggingStrategy(ILoggingStrategy):

    def log(self, devices: Dict[str, EmergencyVehicle]) -> None:
        for device_id, emergency_vehicle in devices.items():
            try:
                message = emergency_vehicle.to_dict()
                logger.info(DeviceType.EMERGENCY_VEHICLE.name, message,
                            logger.LoggingBehaviour.STATUS)
            except Exception as e:
                logger.error(DeviceType.EMERGENCY_VEHICLE.name, str(e))


class LoggingManager:
    def __init__(self):
        self._strategies: Dict[DeviceType, ILoggingStrategy] = {}
        self._register_strategies()

    def _register_strategies(self):
        self._strategies[DeviceType.VEHICLE] = VehicleLoggingStrategy()
        self._strategies[DeviceType.TRAFFIC_LIGHT] = TrafficLightLoggingStrategy()
        self._strategies[DeviceType.SMART_PHONE] = SmartPhoneLoggingStrategy()
        self._strategies[DeviceType.TRAFFIC_CAMERA] = TrafficCameraLoggingStrategy()
        self._strategies[DeviceType.INDUCTION_LOOP] = InductionLoopLoggingStrategy()
        self._strategies[DeviceType.EMERGENCY_CENTER] = EmergencyResponseCenterLoggingStrategy()
        self._strategies[DeviceType.EMERGENCY_VEHICLE] = EmergencyVehicleLoggingStrategy()  

    def log(self, device_type: DeviceType, devices: Dict[str, Union[TrafficCamera, Vehicle, InductionLoop, SmartPhone, EmergencyResponseCenter, EmergencyVehicle, TrafficLightSystem]]) -> None:

        assert device_type in self._strategies, f"No logging strategy for device type {device_type}"

        
        strategy = self._strategies.get(device_type)
        if not strategy:
            logger.error(object_type=device_type.name, message=f"No logging strategy for device type {device_type}")
            return
        strategy.log(devices)
