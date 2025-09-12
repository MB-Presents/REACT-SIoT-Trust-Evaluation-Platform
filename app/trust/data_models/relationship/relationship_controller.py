from __future__ import annotations
from typing import TYPE_CHECKING
from typing import List

# from typing import TYPE_CHECKING
from trust.data_models.relationship.data_models.relationship_manager import RelationshipManager
from trust.data_models.transaction.type import TransactionType


if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.uniform.components.report import SendingPacket
    from trust.data_models.relationship.data_models.relationship import Relationship
    from trust.data_models.transaction.data_models.trust_transaction import Transaction


    


class RelationshipController():
    def __init__(self):
       
        self.relationship_manager : RelationshipManager = RelationshipManager()
        self.transaction_weights = {
            TransactionType.DIRECT_TRANSACTION: 1.0,
            TransactionType.DIRECT_RECOMMENDATION: 0.7,
            TransactionType.INDIRECT_RECOMMENDATION: 0.5
        }
    
    def add(self, transaction: Transaction, new_trust_value: float):
        self.relationship_manager.add(transaction, new_trust_value)
    
    def update_by_relationship(self, relationship: Relationship, new_trust_value: float):
        self.relationship_manager.update_by_relationship(relationship, new_trust_value)
        
    def update_by_transaction(self, transaction: Transaction, new_trust_value: float):
        self.relationship_manager.update_by_transaction(transaction, new_trust_value)
        
        
    def exists(self, trustor : GenericDevice, trustee : GenericDevice, transaction_context : SendingPacket) -> bool:
        return self.relationship_manager.exists_relationship_by_subjects(trustor=trustor, trustee=trustee, transaction_context=transaction_context)
    
    def get(self, trustor : GenericDevice, trustee : GenericDevice, report : SendingPacket=None) -> Relationship:
        return self.relationship_manager.get_relationship(trustor, trustee, report)
        
    
    def get_degree_common_friends(self, trustee : GenericDevice) -> List[str]:
        
        common_friends = self.relationship_manager.get_num_common_friends(trustee)
        total_friends = self.relationship_manager.get_num_total_friends(trustee)
        
        if total_friends == 0:
            return 0
        
        degree_of_common_friendship = common_friends / total_friends
        
        return degree_of_common_friendship