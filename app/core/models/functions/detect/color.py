from __future__ import annotations
from typing import TYPE_CHECKING, Dict


from typing import Union
from core.models.interfaces.function import IFunction

if TYPE_CHECKING:
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.vehicle import Vehicle

class ColorDetectionFunction(IFunction):
    def execute(self, device: Union[SmartPhone, Vehicle]):
        pass