from __future__ import annotations
from collections import defaultdict

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Dict, List, Tuple, Type

from core.models.uniform.components.report import SendingPacket
from core.models.uniform.components.report_models import ReportType


from trust.data_models.relationship.context import RelationshipContext
from trust.data_models.relationship.data_models.relationship import Relationship
from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust.settings import TrustManagementSettings



if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice

class RelationshipManager:
    def __init__(self):
        
        self.relationships: Dict[Tuple(str,str,RelationshipContext), Relationship] = defaultdict(dict)
        self.interacted_devices: Dict[str, int] = defaultdict(int)
        
        # Initialize the new attributes
        self.total_friends: Dict[str,List[str]] = defaultdict(list)
        self.num_total_friends: Dict[str,int] = defaultdict(int)
        self.common_friends: Dict[str,List[str]] = defaultdict(list)
        self.num_common_friends: Dict[str,int] = defaultdict(int)
        
        
        self.num_trustworthy_relationships : Dict[str,int]= defaultdict(int)
        self.num_untrustworthy_relationships : Dict[str,int]= defaultdict(int)
        
        self.trustworthy_devices : Dict[str,str] = defaultdict(list)
        self.untrustworthy_devices : Dict[str,str] = defaultdict(list)
        
    
    def add(self, transaction: AbstractTransaction, new_trust_value: float ):
        
        
        relationship_context = self._get_relationship_context(transaction.task_context)
        
        relationship_key = (transaction.trustor._id, transaction.trustee._id, relationship_context)
        
        self._update_interacted_devices(transaction.trustor._id, transaction.trustee._id)
        
        
        if relationship_key not in self.relationships.keys():
            
            self.relationships[relationship_key] = Relationship(transaction.trustor, transaction.trustee, relationship_context)
            self.relationships[relationship_key].trust_value = new_trust_value
            
            self._update_metadata(transaction.trustor, transaction.trustee, transaction.task_context)
    
    def _update_interacted_devices(self, trustor_id: str, trustee_id: str):
        
        if trustor_id not in self.interacted_devices.keys():
            self.interacted_devices[trustor_id] = 0
        
        elif trustee_id not in self.interacted_devices.keys():
            self.interacted_devices[trustee_id] = len(self.interacted_devices.keys())
        
        
        
        
    def update_by_relationship(self, relationship : Relationship, new_value: float):
        
        relationship_context = self._get_relationship_context(relationship.context)
        relationship_key = (relationship.trustor._id, relationship.trustee._id, relationship_context)
        
        if relationship_key not in self.relationships.keys():
            self.relationships[relationship_key].trust_value = new_value

        self._update_metadata(relationship.trustor, relationship.trustee)
        
    def update_by_transaction(self, transaction : AbstractTransaction, new_value: float):
            
        relationship_context = self._get_relationship_context(transaction.task_context)
        relationship_key = (transaction.trustor._id, transaction.trustee._id, relationship_context)
        
        if relationship_key not in self.relationships.keys():
            self.relationships[relationship_key].trust_value = new_value

        self._update_metadata(transaction.trustor, transaction.trustee, task_context=transaction.task_context)    
    
        
        
    def _update_metadata(self, trustor: GenericDevice, trustee: GenericDevice, task_context : SendingPacket):
        
        relationship_context = self._get_relationship_context(task_context)
        
        relationship_key = (trustor._id, trustee._id, relationship_context)
        
        relationship = self.relationships[relationship_key]
        trust_value = relationship.trust_value
        
        self.total_friends[trustee._id] = list(set(trustee.trust_manager.relationship_controller.relationship_manager.trustworthy_devices) | set(trustor.trust_manager.relationship_controller.relationship_manager.trustworthy_devices))
        self.num_total_friends[trustee._id] = len(self.total_friends[trustee._id])
        self.common_friends[trustee._id] = list(set(trustee.trust_manager.relationship_controller.relationship_manager.trustworthy_devices) & set(trustor.trust_manager.relationship_controller.relationship_manager.trustworthy_devices))
        self.num_common_friends[trustee._id] = len(self.common_friends[trustee._id])
        
        trustee_key = trustee._id

        if trust_value >= TrustManagementSettings.TRUST_THRESHOLD_RELATIONSHIP:
            if trustee_key not in self.trustworthy_devices:
                self.trustworthy_devices[trustee_key] = trustee_key
            if trustee_key in self.untrustworthy_devices:
                self.untrustworthy_devices[trustee_key] = trustee_key
        elif trust_value < TrustManagementSettings.TRUST_THRESHOLD_RELATIONSHIP:
            if trustee_key not in self.untrustworthy_devices:
                self.untrustworthy_devices[trustee_key]= trustee_key
            if trustee_key in self.trustworthy_devices:
                self.trustworthy_devices[trustee_key] = trustee_key

        self.num_trustworthy_relationships = len(self.trustworthy_devices)
        self.num_untrustworthy_relationships = len(self.untrustworthy_devices)


    def exists_relationship_by_subjects(self, trustor : GenericDevice, trustee : GenericDevice, transaction_context : SendingPacket) -> bool:
        
        relationship_context = self._get_relationship_context(transaction_context)
        relationships_key = (trustor._id, trustee._id, relationship_context)
        
        if relationships_key not in self.relationships.keys():
            return False
        return True
        
    
    def exists_relationship_by_relationship(self, relationship : Relationship) -> bool:
        
        if relationship is None:
            return False    
        
        relationships_key = (relationship.trustor._id, relationship.trustee._id, relationship.context)
        
        if relationships_key not in self.relationships.keys():
            return False
        return True
    
    
    def get_relationship(self, trustor: GenericDevice, trustee: GenericDevice, report: SendingPacket =None) -> Relationship:
        trustor_key = trustor._id
        trustee_key = trustee._id
        
        relationship_context =  None
        if report is not None:
            relationship_context = self._get_relationship_context(report)
        
        relationship_key = (trustor_key, trustee_key, relationship_context)
        
        if relationship_key not in self.relationships.keys():
            return None

        return self.relationships[relationship_key]
                    
    def _get_relationship_context(self, report: SendingPacket) -> RelationshipContext:
        if TrustManagementSettings.USE_RELATIONSHIP_CONTEXT:
            return report
        return None  
      
    def get_relationships_by_context(self, trustor : GenericDevice, trustee : GenericDevice, task_context : SendingPacket) -> Dict[Tuple[str,str,ReportType],Relationship]:
        
        trustor_key = trustor._id
        filtered_relationships = {}
        
        trustee_key = trustee._id
        relationship_context = self._get_relationship_context(task_context)
    
        relationship_key = (trustor_key, trustee_key, relationship_context)
    
        if self.exists_relationship_by_subjects(trustor, trustee, relationship_context):
            filtered_relationships[relationship_key] = self.relationships[relationship_key]
        
        return filtered_relationships
    
    
    
    def get_trustworthy_devices(self) -> List[str]:
        
        if len(self.trustworthy_devices) == 0:
            return []
        
        return list(self.trustworthy_devices.values())
        
    def get_num_common_friends(self, trustee : GenericDevice) -> int:
        
        
        if trustee._id not in self.num_common_friends.keys():
            return 0
        
        return self.num_common_friends[trustee._id]
    
    def get_num_total_friends(self, trustee : GenericDevice) -> int:
        
        if trustee._id not in self.num_total_friends.keys():
            return 0
        
        return self.num_total_friends[trustee._id]
    
    def get_num_trustworthy_relationships_of_trustee(self, trustee : GenericDevice) -> int:
        return self.num_trustworthy_relationships[trustee._id]
    
    def get_num_untrustworthy_relationships_of_trustee(self, trustee : GenericDevice) -> int:
        return self.num_untrustworthy_relationships[trustee._id]
    
    def get_num_trustworthy_relationships(self) -> int:
        return len(self.trustworthy_devices.keys())
    
    def get_num_untrustworthy_relationships(self) -> int:
        return len(self.untrustworthy_devices.keys())
    
    
    def get_total_friends(self, trustee : GenericDevice) -> List[str]:
        return self.total_friends[trustee._id]
    

    def get_num_relationships(self) -> int:
        
        if len(self.relationships) == 0:
            return 0
        
        return len(self.relationships.keys())
    
    def get_untrustworthy_devices(self) -> List[str]:
        
        if len(self.untrustworthy_devices) == 0:
            return []
        return list(self.untrustworthy_devices.values())