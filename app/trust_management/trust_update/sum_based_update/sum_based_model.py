from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from data_models.report_management.report.report import SendingPacket
from trust_management.data_models.relationship.data_models.relationship import Relationship
from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust_management.situation_recognition_module.situation_recognition import SituationSettings

from trust_management.trust_update.trust_update_interface import ITrustUpdate




if TYPE_CHECKING:

    from data_models.iot_devices.genric_iot_device import GenericDevice






class AverageSumModel(ITrustUpdate):
    
    
    def trust_update(self, 
                    trustor : GenericDevice, 
                    trustee : GenericDevice,
                    trust_value : float,
                    request : SendingPacket = None,
                    transaction : AbstractTransaction = None,
                    situation_settings : SituationSettings = None) -> float:

        
        
        
        common_transactions = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_pairs(trustor._id, trustee._id)
        
        
        number_of_transactions = len(common_transactions)
        if number_of_transactions == 0:
            raise Exception("No common transactions between trustor and trustee")
            return 0.0

        sorted_transactions = dict(sorted(common_transactions.items(), key=lambda item: item[1].transaction_context.time, reverse=True))

        total_weighted_trust = sum(transaction.trust_value * trustor.trust_manager.relationship_controller.transaction_weights[transaction.type] for transaction in sorted_transactions.values())

        weighted_average_trust_value = total_weighted_trust / number_of_transactions

                
        return weighted_average_trust_value

        
