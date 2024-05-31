from __future__ import annotations

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING
from typing import List





if TYPE_CHECKING:
    from data_models.iot_devices.genric_iot_device import GenericDevice
    from data_models.report_management.report.report_models import ReportType
    from data_models.report_management.report.report import SendingPacket



class RelationshipContext:
    
    def __init__(self, time : float = None,
                 absolute_position : List[float] = None,
                 report : SendingPacket = None,
                 function = None,
                 service=None,
                 request=None):
        
        self.time : float = time
        self.position : List[float]= absolute_position
        self.task  = report
        self.function = function
        self.service = service
        self.request = request