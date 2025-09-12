from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import weakref
from collections import defaultdict
import uuid

from core.models.interfaces.device_registry import IDeviceRegistry
from core.models.interfaces.report_provider import IReportProvider
from core.simulation.event_bus.event_bus import EventBus


class ISimulationContext(Protocol):
    """Interface for simulation-wide services"""
    def get_device_registry(self) -> IDeviceRegistry: ...
    def get_report_provider(self) -> IReportProvider: ...
    def get_event_bus(self) -> EventBus: ...
