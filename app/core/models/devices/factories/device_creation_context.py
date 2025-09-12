from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
from core.models.devices.common import DeviceBehaviour, DeviceType
from core.simulation.simulation_context import SimulationContext


@dataclass
class DeviceCreationContext:
    """Context object containing all dependencies needed for device creation"""
    simulation_context: SimulationContext
    device_id: str
    device_type: DeviceType
    config: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Tuple[float, float]] = None
    color: Optional[Tuple[float, float, float]] = None
    device_behaviour: DeviceBehaviour = DeviceBehaviour.TRUSTWORTHY