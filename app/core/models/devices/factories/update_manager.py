from __future__ import annotations
from ast import Tuple
from typing import Any, Dict, Union, TYPE_CHECKING


from abc import ABC, abstractmethod
import random
from typing import Dict, Optional
from core.data_alteration.behaviour.device_behaviour_determinator import determine_device_behavior
from core.data_alteration.profiles.device_profile_generator import generate_device_profiles
from core.models.devices.common import DeviceBehaviour, DeviceType, Function, Service
from core.models.devices.genric_iot_device import GenericDevice
import traci
import traci.constants as tc

from core.models.devices.smart_phone import SmartPhone
from core.models.devices.traffic_light import TrafficLightSystem
from core.models.devices.vehicle import Vehicle
from core.models.functions.measure import lane_position
from core.simulation.adapter.manager_adapter import TraciAdapter
from core.utils.debug.typing import TSmartDevices
from trust.trust_recommenders.ontology_based.mappings import speed
import utils.logging as logger

if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler


class IUpdateStrategy(ABC):
    @abstractmethod
    def update(self, devices: Dict[str, TSmartDevices]) -> None:
        """Update the state of a group of devices."""
        pass


class VehicleUpdateStrategy(IUpdateStrategy):
    def update(self, devices: Dict[str, Vehicle]) -> None:
        vehicle_in_simulation = TraciAdapter().subscription.get_vehicle_subscription_result()
        
        # traci.vehicle.getAllSubscriptionResults()
        existing_vehicles = {veh_id: vehicle for veh_id, vehicle in vehicle_in_simulation.items() if vehicle[tc.VAR_VEHICLECLASS] != 'bicycle'}

        for veh_id, vehicle_data in devices.items():
            if veh_id not in existing_vehicles:
                del devices[veh_id]
                
        for veh_id, vehicle_data in existing_vehicles.items():
            if veh_id not in devices:
                device = DevicesGroupHandler().create_device(device_type=DeviceType.VEHICLE, config=vehicle_data, _id=veh_id)
                assert device is not None, f"Failed to create device for {veh_id}"
            devices[veh_id].update(vehicle_data)

    def _remove_non_present_vehicles(self, devices: Dict[str, Vehicle], vehicle_in_simulation: dict) -> dict:
        vehicle_ids_in_simulation = list(vehicle_in_simulation.keys())
        current_vehicle_ids = list(devices.keys())
        nonexistent_vehicle_ids = [
            veh_id for veh_id in current_vehicle_ids
            if veh_id not in vehicle_ids_in_simulation or devices[veh_id]._vehicle_type in ['bike_bicycle', 'ped_pedestrian']
        ]
        for veh_id in nonexistent_vehicle_ids:
            del devices[veh_id]
        return {
            veh_id: vehicle for veh_id, vehicle in vehicle_in_simulation.items()
            if vehicle[tc.VAR_VEHICLECLASS] not in ['bicycle', 'ped_pedestrian']
        }

    # def _create_vehicle(self, veh_id: str, veh_object: dict) -> 'Vehicle':
    #     speed = veh_object[tc.VAR_SPEED]
    #     position = veh_object[tc.VAR_POSITION]
    #     edge_id = veh_object[tc.VAR_ROAD_ID]
    #     lane_id = veh_object[tc.VAR_LANE_ID]
    #     lane_position = veh_object[tc.VAR_LANEPOSITION]
    #     lane_index = veh_object[tc.VAR_LANE_INDEX]
    #     color = veh_object[tc.VAR_COLOR]
    #     signal = veh_object[tc.VAR_SIGNALS]
    #     vehicle_type = veh_object[tc.VAR_TYPE]
    #     length = veh_object[tc.VAR_LENGTH]
    #     width = veh_object[tc.VAR_WIDTH]
    #     height = veh_object[tc.VAR_HEIGHT]
    #     vehicle_class = veh_object[tc.VAR_VEHICLECLASS]

    #     device_behaviour = DeviceBehaviour.TRUSTWORTHY
    #     if not veh_id.startswith("emergency_veh"):
    #         device_behaviour = determine_device_behavior()

    #     trustworthy_vehicle_profiles, untrustworthy_vehicle_profiles = generate_device_profiles('vehicle', 20, 20)
    #     profile = random.choice(trustworthy_vehicle_profiles if device_behaviour == DeviceBehaviour.TRUSTWORTHY else untrustworthy_vehicle_profiles)

    #     return Vehicle(
    #         veh_id=veh_id,
    #         speed=speed,
    #         position=position,
    #         signal=signal,
    #         edge_id=edge_id,
    #         lane_id=lane_id,
    #         color=color,
    #         lane_position=lane_position,
    #         vehicle_type=vehicle_type,
    #         width=width,
    #         height=height,
    #         length=length,
    #         lane_index=lane_index,
    #         vehicle_class=vehicle_class,
    #         # manufacturer=profile['manufacturer'],
    #         # model=profile['model'],
    #         # firmware_version=profile['firmware_version'],
    #         # hardware_version=profile['hardware_version'],
    #         # serial_number=profile['serial_number'],
    #         # date_of_manufacture=profile['manufacture_date'],
    #         # last_maintenance_date=profile['last_maintenance_date'],
    #         # next_maintenance_date=profile['next_maintenance_date'],
    #         device_behaviour=device_behaviour
    #     )


class TrafficLightUpdateStrategy(IUpdateStrategy):
    def update(self, devices: Dict[str, TrafficLightSystem]) -> None:
        trafficlights = traci.trafficlight.getIDList()
        for traffic_light_id in trafficlights:
            traffic_light = traci.trafficlight.getSubscriptionResults(
                traffic_light_id)
            
            
            controlled_lanes = traffic_light[tc.TL_CONTROLLED_LANES]
            controlled_links = traffic_light[tc.TL_CONTROLLED_LINKS]
            current_program = traffic_light[tc.TL_CURRENT_PROGRAM]
            current_phase = traffic_light[tc.TL_CURRENT_PHASE]
            next_switch = traffic_light[tc.TL_NEXT_SWITCH]
            phase_duration = traffic_light[tc.TL_PHASE_DURATION]
            ryg_state = traffic_light[tc.TL_RED_YELLOW_GREEN_STATE]
            devices[traffic_light_id].update(controlled_lanes, controlled_links, current_program, current_phase, next_switch, phase_duration, ryg_state)


class SmartPhoneUpdateStrategy(IUpdateStrategy):
    def update(self, smart_phones: Dict[str, SmartPhone]) -> None:

        pedestrians = TraciAdapter().subscription.get_pedestrian_subscriptition_result()
        bicyclists = TraciAdapter().subscription.get_bicyclist_subscription_result()

        current_entities = {**pedestrians, **bicyclists}

        for smart_phone_id, smart_phone in smart_phones.items():
            if smart_phone_id not in pedestrians and smart_phone_id not in bicyclists:
                del smart_phones[smart_phone_id]

        for smart_phone_id, smart_phone_state in current_entities.items():
            if smart_phone_id in current_entities:
                smart_phones[smart_phone_id]._speed = smart_phone_state[tc.VAR_SPEED]
                smart_phones[smart_phone_id]._position = smart_phone_state[tc.VAR_POSITION]
                smart_phones[smart_phone_id]._edge_id = smart_phone_state[tc.VAR_ROAD_ID]
                smart_phones[smart_phone_id]._lane_id = smart_phone_state[tc.VAR_LANE_ID]
                smart_phones[smart_phone_id]._lane_position = smart_phone_state[tc.VAR_LANEPOSITION]

            elif smart_phone_id not in smart_phones:
                DevicesGroupHandler()._device_factory.create(device_type=DeviceType.SMART_PHONE, config=smart_phone_state, _id=smart_phone_id)
                
                



class TrafficCameraUpdateStrategy(IUpdateStrategy):
    def update(self, devices: Dict[str, GenericDevice]) -> None:
        for traffic_camera_id, traffic_camera in devices.items():
            traffic_camera._services[Service.Vehicle_Detection_Service]._function[Function.GET_DETECTED_VEHICLES](
                traffic_camera)


class InductionLoopUpdateStrategy(IUpdateStrategy):
    def update(self, devices: Dict[str, GenericDevice]) -> None:
        for induction_id, induction_loop in devices.items():
            induction_loop._services[Service.Inductive_Vehicle_Detection_Service]._function[Function.GET_INDUCTIVE_OBJECT_COUNT](
                induction_loop)


class UpdateManager:
    def __init__(self):
        self._strategies: Dict[DeviceType, IUpdateStrategy] = {}
        self._register_strategies()

    def _register_strategies(self):
        self._strategies[DeviceType.VEHICLE] = VehicleUpdateStrategy()
        self._strategies[DeviceType.TRAFFIC_LIGHT] = TrafficLightUpdateStrategy()
        self._strategies[DeviceType.SMART_PHONE] = SmartPhoneUpdateStrategy()
        self._strategies[DeviceType.TRAFFIC_CAMERA] = TrafficCameraUpdateStrategy()
        self._strategies[DeviceType.INDUCTION_LOOP] = InductionLoopUpdateStrategy()
        # No strategy for EMERGENCY_CENTER as it has no update method

    def update(self, device_type: DeviceType) -> None:
        strategy = self._strategies.get(device_type)
        if not strategy:
            logger.error(device_type.name, f"No update strategy for device type {device_type}")
            return

        device_group = DevicesGroupHandler().get_devices_by_group(device_type)
        strategy.update(device_group)
