from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC

from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction


if TYPE_CHECKING:
    from data_models.report_management.report.report import SendingPacket
    from data_models.iot_devices.genric_iot_device import GenericDevice
    from trust_management.situation_recognition_module.situation_recognition import SituationSettings


class ITrustUpdate(ABC):
    

    
    def trust_update(self, 
                    trustor : GenericDevice, 
                    trustee : GenericDevice,
                    trust_value : float,
                    request : SendingPacket = None,
                    transaction : AbstractTransaction = None,
                    situation_settings : SituationSettings = None) -> float:
        pass
    
    