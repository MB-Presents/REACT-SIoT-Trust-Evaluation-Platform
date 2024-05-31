from __future__ import annotations
from ast import Dict

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Tuple, Union

from data_models.report_management.report.report import SendingPacket
from data_models.report_management.report.report_models import ReportType
from trust_management.data_models.ITransactionUpdate import ITransactionUpdate
from trust_management.data_models.reputation.reputation import ReputationComputationStrategy, ReputationContextSettings, ReputationScope
from trust_management.data_models.transaction.data_models.direct_recommendation import DirectRecommendation
from trust_management.data_models.transaction.data_models.trust_transaction import Transaction



from trust_management.settings import TrustManagementSettings

if TYPE_CHECKING:
    from trust_management.data_models.transaction.transaction_controller import TransactionController
    from data_models.iot_devices.genric_iot_device import GenericDevice





class ReputationController(ITransactionUpdate):
    
    
    def __init__(self, transaction_controller: TransactionController, reputation_context : ReputationContextSettings, reputation_scope : ReputationScope, reputation_strategy : ReputationComputationStrategy) -> None:
        
        self.reputation_context : ReputationContextSettings = reputation_context
        self.transaction_controller : TransactionController = transaction_controller
        self.reputation_scope : ReputationScope = reputation_scope
        self.reputation_computation_strategy : ReputationComputationStrategy = reputation_strategy
        self.reputations : Dict[Tuple[str,str,ReportType],float] = {}
        
    def update(self, transaction : Union[Transaction,DirectRecommendation]= None):
        
        trustor = transaction.trustor
        trustee = transaction.trustee
        report = transaction.task_context
        
        
        reputation_context = self.get_reputation_context(transaction.task_context) 
        
        if not self.exists_reputation(trustor, trustee, reputation_context):
            self.add_reputation(trustor, trustee, reputation_context)
            
        elif self.exists_reputation(trustor, trustee, reputation_context):
            
        
        
            if self.reputation_scope == ReputationScope.LOCAL:
                reputation_score = self.get_local_reputation(transaction)
                self.reputations[(trustor._id, trustee._id, reputation_context)] = reputation_score    
                    

    
    def get_local_reputation(self, transaction : Union[Transaction,DirectRecommendation]):    
        
        reputation_score = None
        
        if self.reputation_computation_strategy == ReputationComputationStrategy.AVERAEG_OF_LAST_N_TRANSACTIONS:
            reputation_score = self.update_local_reputation_average_of_last_n_transactions(transaction)
        
        return reputation_score
    
            
    def update_local_reputation_average_of_last_n_transactions(self, current_transaction : Union[Transaction,DirectRecommendation]):
        
        reputation_scores_for_object = []
        
        transactions_with_trustee = self.transaction_controller.transaction_manager.get_by_trustee(current_transaction.trustee._id)
        
        for uuid, transaction in transactions_with_trustee.items():
        
            reputation_context = self.get_reputation_context(transaction.task_context)
            
            
            reputation_scores_for_object.append(transaction.trust_value)
        
        return sum(reputation_scores_for_object) / len(reputation_scores_for_object)        
            
    
    def get_reputation_context(self, report : SendingPacket) -> ReputationContextSettings:
        
        
        if self.reputation_context == ReputationContextSettings.TASK_CONTEXT:
            return report.request_type.value
        
        elif self.reputation_context == ReputationContextSettings.NO_CONTEXT:
            return ReputationContextSettings.NO_CONTEXT
        
        raise ValueError("Reputation context is not defined")
    
    
    def get_reputation_key(self, trustor : GenericDevice, trustee : GenericDevice, report : SendingPacket):
            
        trustor_key = trustor._id
        trustee_key = trustee._id
        
        reputation_context = self.get_reputation_context(report)
        
        return (trustor_key, trustee_key, reputation_context)
    
    def exists_reputation(self, trustor : GenericDevice, trustee : GenericDevice, task_context : int) -> bool:
        
        trustor_key = trustor._id
        trustee_key = trustee._id
        
        return (trustor_key, trustee_key, task_context) in self.reputations.keys()
    
    def add_reputation(self, trustor : GenericDevice, trustee : GenericDevice, request_context : ReportType):
        
        trustor_key = trustor._id
        trustee_key = trustee._id
        
        task_context = None
        reputation_context = ReputationContextSettings.NO_CONTEXT
        
        if TrustManagementSettings.USE_RELATIONSHIP_CONTEXT:

            reputation_context = request_context.value
            # reputation_context = ReputationContext(trustor=trustor, trustee=trustee, task_context=reputation_context)
        
        
        self.reputations[(trustor_key, trustee_key, task_context)] = reputation_context
