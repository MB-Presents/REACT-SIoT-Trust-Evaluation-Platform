from __future__ import annotations

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING
from typing import List

from core.models.uniform.components.report import SendingPacket





if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice




class ReputationContext:
    
    def __init__(self, trustor : GenericDevice, trustee : GenericDevice, time : float = None, absolute_position : List[float] = None, report : SendingPacket = None, function = None, service=None, request=None):
        self.trustor : GenericDevice = trustor
        self.trustee : GenericDevice = trustee
        self.time : float = time
        self.position : List[float]= absolute_position
        self.task  = report
        self.function = function
        self.service = service
        self.request = request