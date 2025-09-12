from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from core.models.uniform.components.report import SendingPacket
from trust.data_models.relationship.data_models.relationship import Relationship


from trust.trust_update.trust_update_interface import ITrustUpdate




if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.devices.genric_iot_device import GenericDevice
    
    from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
    from trust.situation_recognition_module.situation_recognition import SituationSettings







class TrustComputationValue(ITrustUpdate):
    
    
    def trust_update(self, 
                    trustor : GenericDevice, 
                    trustee : GenericDevice,
                    trust_value : float,
                    request : SendingPacket = None,
                    transaction : AbstractTransaction = None,
                    situation_settings : SituationSettings = None) -> float:
        
        
        return trust_value