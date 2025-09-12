from __future__ import annotations
from typing import TYPE_CHECKING

import sys
import os
from core.models.uniform.components.report import SendingPacket
from trust.data_models.transaction.status import TransactionStatus
from trust.data_models.transaction.type import TransactionType

project_root = os.getenv("RESEARCH_PROJECT_ROOT", default="/app")
sys.path.insert(0, project_root)

from trust.trust_update.trust_update_interface import ITrustUpdate


if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice
    
    from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
    from trust.situation_recognition_module.situation_recognition import SituationSettings


class TrustInferenceModel(ITrustUpdate):
    
        
    def trust_update(self, 
                    trustor : GenericDevice, 
                    trustee : GenericDevice,
                    trust_value : float,
                    request : SendingPacket = None,
                    transaction : AbstractTransaction = None,
                    situation_settings : SituationSettings = None) -> float:
        
        if trustor._id == 'bike1':
            pass
        
        
        if transaction.status == TransactionStatus.PENDING:
            return trust_value
        
        elif transaction.status == TransactionStatus.VERIFIED:
            
            if transaction.type == TransactionType.DIRECT_RECOMMENDATION:
                pass
            
            prediction =  trustor.trust_manager._temporal_graph_based_trust_model.trust_update(trustor, trustee, transaction.trust_value, request, transaction, situation_settings)
            return prediction
        
        raise NotImplementedError("The transaction status is not supported")
        
        
        