from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from trust_management.data_models.relationship.data_models.relationship import Relationship


from trust_management.trust_update.trust_update_interface import ITrustUpdate




if TYPE_CHECKING:

    from data_models.iot_devices.genric_iot_device import GenericDevice
    from data_models.iot_devices.genric_iot_device import GenericDevice
    from data_models.report_management.report.report import SendingPacket
    from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
    from trust_management.situation_recognition_module.situation_recognition import SituationSettings







class TrustComputationValue(ITrustUpdate):
    
    
    def trust_update(self, 
                    trustor : GenericDevice, 
                    trustee : GenericDevice,
                    trust_value : float,
                    request : SendingPacket = None,
                    transaction : AbstractTransaction = None,
                    situation_settings : SituationSettings = None) -> float:
        
        
        return trust_value