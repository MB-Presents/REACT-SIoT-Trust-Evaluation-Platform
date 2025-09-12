
from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from typing import Union
from core.models.interfaces.function import IFunction

if TYPE_CHECKING:
    from core.models.devices.vehicle import Vehicle
    from core.models.devices.smart_phone import SmartPhone


class StreetDetectionFunction(IFunction):
    def execute(self, device: Union[SmartPhone, Vehicle]):
        return device._edge_id