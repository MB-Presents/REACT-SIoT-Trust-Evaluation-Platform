
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List
from data_models.report_management.report.report import SendingPacket
from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust_management.situation_recognition_module.situation_recognition import SituationSettings
from trust_management.trust_recommenders.common.social_relationships import SocialRelationships

from trust_management.trust_recommenders.interface_trust_model import ITrustComputationModel

if TYPE_CHECKING:

    from trust_management.situation_recognition_module.situation_recognition import SituationSettings
    from data_models.report_management.report.report import SendingPacket
    from data_models.iot_devices.genric_iot_device import GenericDevice

class ContextBasedTrustModelIoT(ITrustComputationModel):
    
    
    def __init__(self):
        super().__init__()
        
        # self.trust_decision_model = 
        
        self.w_direct_and_indirect_trust = 0.25
        
        
        
        # self.w_owner_trust = 0.25, is not possible since there is no OSN data linked from owenr to device
        self.w_owner_trust = 0.0
        
        self.w_computation_power = 0.25
        self.w_relationship_factor = 0.25
        
        # self.w_centrality = 0.5; is not possible to compute centrality in IoT networks
        self.w_centrality = 0
        self.w_common_friends = 0.5
        
        self.fb_max = 10
        self.max_change_trust_value = 0.1
        
        self.w_feedback_fb = 0.5
        
        # Not further specificed in the paper but we used the relationship factores used in (Nitti, 2012)
        self.social_relationships = SocialRelationships(
            default_trust_value=0.5)
    
        
        self.context = True
    
        
    def check_compliance(   self, 
                    trustor : GenericDevice, 
                    request : SendingPacket = None,
                    sensory_parameters : dict = None,
                    situation_settings : SituationSettings = None) -> bool:
    
        return super().check_compliance(trustor, request, sensory_parameters, situation_settings)
    
    
    def preprocess_trust_evaluation(self, trustor: GenericDevice, request: SendingPacket = None, sensory_parameters: dict = None, situation_settings: SituationSettings = None):
        return super().preprocess_trust_evaluation(trustor, request, sensory_parameters, situation_settings)
    
    def computate_trust_value(self, trustor: GenericDevice, trustee: GenericDevice, request: SendingPacket = None, sensory_parameters: dict = None, situation_settings: SituationSettings = None) -> float:
        
        degree_of_common_friends = trustor.trust_manager.relationship_controller.get_degree_common_friends(trustee)
        
        
        indirect_trust_value = 0
        direct_trust_value = 0
        
        task_context = request.request_type.value 
        
        
        direct_trust_transactions = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_trustee_id(trustee._id)
        direct_trust_transactions_context_filter = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_trustee_and_task_context(trustee._id,task_context=task_context)
        
        indirect_trust_transactions_context_filter = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_recommendations_of_trust_subject_by_task_context(trustee._id,task_context=task_context)
        direct_trust_value = self.compute_direct_trust(trustor, trustee, direct_trust_transactions, direct_trust_transactions_context_filter)
        
        
        recommenders = self.get_recommender_context(trustor, task_context, indirect_trust_transactions_context_filter)
        indirect_trust_value = self.compute_indirect_trust_value(trustor, recommenders, task_context)
        
        
        # Compute weight
        if (direct_trust_value + indirect_trust_value) > 0 and (direct_trust_value + indirect_trust_value) <= 1:
            self.w_direct_and_indirect_trust = direct_trust_value  / (direct_trust_value + indirect_trust_value)
        elif (direct_trust_value + indirect_trust_value) == 0:
            self.w_direct_and_indirect_trust = 0.0
        
        
        
        # Aggegate trust features
        trust_value = self.w_direct_and_indirect_trust * direct_trust_value + (1 - self.w_direct_and_indirect_trust) * indirect_trust_value
        
        
        return trust_value

    def get_recommender_context(self, trustor : GenericDevice, task_context : SendingPacket, indirect_trust_transactions_context_filter : List[AbstractTransaction]):
        recommenders = {}
        
        transaction : AbstractTransaction
        for transaction in indirect_trust_transactions_context_filter:
            recommenders[transaction.trustor._id] = transaction
            recommenders[transaction.trustor._id]['recommender'] = transaction.trustor
            recommenders[transaction.trustor._id]['trust_subject'] = transaction.trustee
            recommenders[transaction.trustor._id]['recommendations_context'] = transaction.trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_trustee_and_task_context(transaction.trustee._id, task_context=task_context)
            recommenders[transaction.trustor._id]['recommendations'] = transaction.trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_trustee_id(transaction.trustee._id)
            recommenders[transaction.trustor._id]['trust_value'] = transaction.trust_value
            recommenders[transaction.trustor._id]['confidence'] = trustor.trust_manager.relationship_controller.get(trustor=trustor, trustee=transaction.trustor).trust_value
        return recommenders

    def compute_direct_trust(self, trustor : GenericDevice, trustee : GenericDevice, direct_trust_transactions : List[AbstractTransaction], direct_trust_transactions_context_filter : List[AbstractTransaction]):
        
        direct_trust_value = 0.0
        
        if len(direct_trust_transactions) == 0:
            direct_trust_value = self.social_relationships.get_social_relationship_value(trustor, trustee)
            
        if len(direct_trust_transactions) > 0:
            total_transactions = len(direct_trust_transactions)
            
            
            for context_name, transaction in  trustor.trust_manager.trust_transaction_controller.transaction_manager.transactions_by_transaction_context.items():
                
                transaction_in_context = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_task_context(context_name)
                new_trust_value_of_context = 0
                
                for transaction in transaction_in_context:
                
                    if transaction.trustee._id == trustee._id:
                        
                        change_effect = self.fb_max / self.max_change_trust_value
                        previous_trust_value = trustor.trust_manager.relationship_controller.relationship_manager.get_relationship(trustor=trustor, trustee=transaction.trustee, report=transaction.task_context).trust_value

                        change_of_rate = transaction.trust_value / change_effect
                        
                        new_trust_value_of_context = previous_trust_value + change_of_rate
                
                
                
                context_weight = len(transaction_in_context) / total_transactions
                context_trust_value = new_trust_value_of_context * context_weight
                
                direct_trust_value += context_trust_value 
            
            direct_trust_value = direct_trust_value / total_transactions
        return direct_trust_value
    
    def postprocessing_trust_evaluation(self, 
                                        trustor: GenericDevice, 
                                        request: SendingPacket = None, 
                                        sensory_parameters: dict = None, 
                                        situation_settings: SituationSettings = None) -> float:
        return super().postprocessing_trust_evaluation(trustor, request, sensory_parameters, situation_settings)
    
    
    def compute_indirect_trust_value(self, trustor : GenericDevice, recommenders : dict, task_context : int):
        """
        Compute the indirect trust value based on recommendations from other nodes.

        :param trustor: The node that is trying to assess the trust value.
        :param recommenders: A dictionary of recommenders with their respective trust values and confidence.
        :param task_context: The specific context for which the trust is being evaluated.
        :return: The computed indirect trust value.
        """
        
        recommendations = [transaction for recommender_id, data in recommenders.items() for transaction in data['recommendations']]
        num_recommendations = len(recommendations)
        
        
        num_recommenders = len(recommenders)
        
        sum_weighted_trust = 0

        
        indirect_trust_value = 0
        
        for recommender_id, data in recommenders.items():

            
            confidence_recommeder = 0 
            recommended_trust = 0
            indirect_trust_per_recommender = 0
            
            
            common_friends = trustor.trust_manager.relationship_controller.get_degree_common_friends(data['recommender'])
            centrality = 0 # No inofmraiton about the centrality of the device is available
            owener_trust = 0 # No inofmraiton about the owener trust of the device is available due it's not a OSN
            
            recommended_trust = 0
            
            if len(data['recommendations_context']) == 0:
                average_trust_value_of_recommendations = sum([transaction.trust_value for transaction in data['recommendations']]) / len(data['recommendations'])
                recommended_trust = average_trust_value_of_recommendations
                
            elif len(data['recommendations_context']) > 0:
                
                rate_of_feedback_change = self.fb_max / self.max_change_trust_value

                recommendation : AbstractTransaction
                
                for recommendation in data['recommendations_context']:
                    recommendation_confidence = recommendation.trust_value / rate_of_feedback_change
                    if recommendation_confidence >= 0.5:
                        recommended_trust += recommendation_confidence 
                    elif recommendation_confidence < 0.5:
                        recommended_trust -= recommendation_confidence
                
                
            
            # Not applicable
            owener_trust = self.w_common_friends * common_friends # + self.w_common_friends * common_friends
            computation_value = 1
            
            relationship_factor = self.social_relationships.get_social_relationship_value(trustor, data['recommender'])
            
            confidence_recommeder = self.w_direct_and_indirect_trust * recommended_trust + self.w_owner_trust * owener_trust + self.w_computation_power * computation_value + self.w_relationship_factor * relationship_factor
            
            
            indirect_trust_per_recommender = recommended_trust * confidence_recommeder 
            
            
            # Add the weighted trust value to the sum
            sum_weighted_trust += indirect_trust_per_recommender
            
        
        # Is not in paper described
        if num_recommenders == 0:
            return 0

        indirect_trust_value  = sum_weighted_trust / num_recommenders
        
        return indirect_trust_value


    
    
    
    
    
    def _calculate_weight(self, transaction_amount, total_transactions):
        """
        Calculate the weight of a transaction in the context of all transactions.
        """
        return transaction_amount / total_transactions if total_transactions > 0 else 0