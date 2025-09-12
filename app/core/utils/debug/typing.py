from __future__ import annotations
from typing import Union, TypeAlias

TSmartDevices: TypeAlias = Union[
    "SmartPhone",
    "Vehicle",
    "EmergencyVehicle",
    "InductionLoop",
    "TrafficCamera",
    "TrafficLightSystem",
    "EmergencyResponseCenter"
]

TVehicle: TypeAlias = Union[
    "Vehicle",
    "EmergencyVehicle"
]

TDynamicDevices: TypeAlias = Union[
    "SmartPhone",
    "Vehicle",
    "EmergencyVehicle"
]

TStaticDevices: TypeAlias = Union[
    "TrafficLightSystem",
    "EmergencyResponseCenter",
    "InductionLoop",
    "TrafficCamera",
]
