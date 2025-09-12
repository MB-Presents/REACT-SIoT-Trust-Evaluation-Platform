from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from abc import ABC, abstractmethod
from typing import Union

if TYPE_CHECKING:
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.vehicle import Vehicle


class IFunction(ABC):

    @abstractmethod
    def execute(self, device : Union[SmartPhone, Vehicle, str]):
        pass