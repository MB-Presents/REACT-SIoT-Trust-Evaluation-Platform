from __future__ import annotations
from typing import TYPE_CHECKING

from trust.data_models.transaction.data_models.trust_transaction import Transaction
from trust.settings import TrustManagementSettings

from trust.trust_recommenders.graph_based_trust_model.temporal_graph_based_trust_model import TemporalGraphNetwork
from trust.trust_recommenders.trust_model import TrustComputationModel
from trust.trust_update.trust_update_interface import ITrustUpdate

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.uniform.components.report import SendingPacket
    from trust.data_models.relationship.relationship_controller import RelationshipController
    from trust.data_models.reputation.reputation_controller import ReputationController
    from trust.data_models.transaction.transaction_controller import TransactionController
    from trust.data_models.TrustVerifierRoles import TrustVerfierRoles

class TrustManager:
    """
    This class is responsible for managing the trust of the system.
    """

    def __init__(self, relationship_controller : RelationshipController, trust_transaction_controller : TransactionController, reputation_controller : ReputationController):
        
        self._temporal_graph_based_trust_model = None
        
        if TrustManagementSettings.TRUST_COMPUTATION_MODEL == TrustComputationModel.GRAPH_BASED_TRUST_MODEL.value:
            self._temporal_graph_based_trust_model = TemporalGraphNetwork()
        
        self.relationship_controller : RelationshipController = relationship_controller
        self.trust_transaction_controller : TransactionController = trust_transaction_controller
        self.reputation_controller : ReputationController= reputation_controller

        self.trust_transaction_controller.subscribe(self)
            
    def add_trust_transaction(self, trustor: GenericDevice, trustee : GenericDevice, trust_value : float, reporting_time : float = None, transaction_context : SendingPacket=None, role : TrustVerfierRoles = None):
        transaction = Transaction(trustor, trustee , trust_value, reporting_time, transaction_context, role=role)
        self.trust_transaction_controller.add_trust_transaction(transaction)

    def add_direct_trust_recommendation(self,  recommendee : GenericDevice, recommender : GenericDevice, trust_subject : GenericDevice,  transaction : Transaction, request : SendingPacket = None):
        self.trust_transaction_controller.add_direct_recommendation(transaction, recommender, recommendee, trust_subject=trust_subject)
            
    def add_indirect_trust_recommendation(self,  recommendee : GenericDevice, recommender : GenericDevice, trust_subject : GenericDevice,  transaction : Transaction, request : SendingPacket = None):
        self.trust_transaction_controller.add_indirect_recommendation(transaction, recommender, recommendee, trust_subject=trust_subject)

    def update(self,transaction : Transaction):
        relationship_update_model : ITrustUpdate = TrustManagementSettings.TRUST_MODEL_SCHEME.trust_update_model
        trust_value = relationship_update_model.trust_update(trustor=transaction.trustor, 
                                                             trustee=transaction.trustee,
                                                             trust_value=transaction.trust_value,
                                                             request=transaction.task_context,
                                                             transaction=transaction,
                                                             situation_settings=TrustManagementSettings.TRUST_SITUATION_SETTINGS)
        
        self.update_relationship(transaction, trust_value)
        self.reputation_controller.update(transaction)
    
    def update_request_status(self, request : SendingPacket):
        self.trust_transaction_controller.update(request)
    
    def update_relationship(self, transaction : Transaction, new_trust_value : float):
        
        if not self.relationship_controller.exists(transaction.trustor, transaction.trustee, transaction.task_context):
            self.relationship_controller.add(transaction, new_trust_value=new_trust_value)
            
        if self.relationship_controller.exists(trustor=transaction.trustor, trustee=transaction.trustee, transaction_context=transaction.task_context):
            self.relationship_controller.update_by_transaction(transaction=transaction, new_trust_value=new_trust_value)
            
        
        

    
    def get_trust_data(self) -> dict:
        """Extract trust-related data for serialization."""
        return {
            'trustworthy_devices': self.relationship_controller.relationship_manager.get_trustworthy_devices(),
            'untrustworthy_devices': self.relationship_controller.relationship_manager.get_untrustworthy_devices(),
            'num_untrustworthy_relationships': self.relationship_controller.relationship_manager.get_num_untrustworthy_relationships(),
            'num_trustworthy_relationships': self.relationship_controller.relationship_manager.get_num_trustworthy_relationships(),
            'num_related_devices': self.relationship_controller.relationship_manager.get_num_relationships(),
            'num_trust_transactions': self.trust_transaction_controller.transaction_manager.get_num_transactions(),
        }