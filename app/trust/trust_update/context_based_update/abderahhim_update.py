

from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING

from core.models.events.simulation_events import VerificationState
from core.models.uniform.components.report import SendingPacket
from trust.data_models.relationship.data_models.relationship import Relationship
from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust.situation_recognition_module.situation_recognition import SituationSettings
from trust.trust_recommenders.common.social_relationships import SocialRelationships
from trust.trust_update.trust_update_interface import ITrustUpdate


if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice



class TRUST_UPDATE_ABDERRAHIM_2017(ITrustUpdate):



    def __init__(self):
        
        self.social_relationships = SocialRelationships(
            value_object_owner_relationship=0.9,
            value_co_location=0.7,
            value_social_object_relationship=0.5,
            value_parental_object_relationship=0.5            
        )
        
    
    def trust_update(self, 
                    trustor : GenericDevice, 
                    trustee : GenericDevice,
                    trust_value : float,
                    request : SendingPacket = None,
                    transaction : AbstractTransaction = None,
                    situation_settings : SituationSettings = None) -> float:

        
        # relationship : Relationship = trustor.trust_manager.relationship_controller.get(trustor, trustee)
        # relationship : Relationship = trustor.trust_manager.relationship_controller.relationship_manager.get_relationship(trustor, trustee)
        
        
        EQ = self.evaluate_transaction(trustor, trustee, trust_value, request, situation_settings)
        
        contextual_trust = self.compute_contextual_trust(trustor, trustee, trust_value, report=request, situation_settings=situation_settings)


        # Update
        
        # TODO UPdate contextual trust 
        # trustor.trust_manager.relationship_controller.relationship_manager.update(trustor, trustee, relationship.context.task, contextual_trust)
        
        # TODO: THIS needs to be fiexed
        # trustor.trust_manager.reputation_controller.reputation_mana.update(trustor, trustee, relationship.context.task, contextual_trust)
        # trustor.trust_manager.reputation_controller.reputation_manager.update(trustor, trustee, relationship.context.task, contextual_trust)

        return contextual_trust

    def evaluate_transaction(self, trustor : GenericDevice, trustee : GenericDevice, trust_value : float, report : SendingPacket, situation_settings ):
        """
        Evaluate a transaction at the node level.

        Parameters:
        idA (str): ID of the requester node.
        idB (str): ID of the service provider node.
        cx (str): Context of the transaction.
        CB (str): Capacity of the evaluated object.
        S (str): Evaluated service.
        OR (str): Object-relationship.
        transaction_outcome (str): Outcome of the transaction ('success', 'fail', or 'uncertain').
        detected_malicious_behavior (bool): Indicates if malicious behavior was detected.

        Returns:
        tuple: An evaluation query (EQ) containing the transaction details and feedback.
        """


        
        feedback = None
        
        if report.trustworthiness == VerificationState.AUTHENTIC:
            feedback = 1
        if report.trustworthiness == VerificationState.NOT_AUTHENTIC:
            feedback = 2
        if report.trustworthiness == VerificationState.NOT_VERIFIEDABLE:
            feedback = 0.5
            
        
        object_relationship = self.social_relationships.get_social_relationship_value(trustor, trustee)
        
        EQ = (trustor._id, trustee._id, report.request_type.value, trustee._computation_capability_class, report.trust_score, object_relationship, feedback)
            
        return EQ


    def compute_contextual_trust(self,trustor : GenericDevice, trustee : GenericDevice, trust_value : float, report : SendingPacket, situation_settings ):
        """
        Compute the contextual trust T_cx_j for an object in a given context.

        Parameters:
        alpha_cx (list): List of alpha values for each transaction, representing successful transactions.
        beta_cx (list): List of beta values for each transaction, representing uncertain transactions.
        lambda_cx (list): List of lambda values for each transaction, representing failed transactions.
        Wl_cx (list): Weights of each transaction.
        N_cx (int): Total number of transactions in context cx.

        Returns:
        float: The contextual trust value T_cx_j.
        """

        # Applying the forgetting factor
        
        contextual_transactions = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_verified_transactions_by_trustee_and_task_context(trustee._id, report.request_type.value)
        
        alpha_cx = []
        beta_cx = []
        lambda_cx = []
        
        for transaction in contextual_transactions:
            if transaction.trust_value == 1:
                alpha_cx.append(transaction.trust_value)
            elif transaction.trust_value == 0.5:
                beta_cx.append(transaction.trust_value)
            elif transaction.trust_value == 0:
                lambda_cx.append(transaction.trust_value)
                
        Wl_cx = [1 for i in range(len(contextual_transactions))]
        N_cx = len(contextual_transactions)
        
        
        forgetting_factors = [lambda_cx ** (N_cx - l) for l in range(N_cx)]
        
        
        # Update alpha, beta, and lambda values with the forgetting factor
        updated_alpha = sum(alpha * w * ff for alpha, w, ff in zip(alpha_cx, Wl_cx, forgetting_factors))
        updated_beta = sum(beta * w * ff for beta, w, ff in zip(beta_cx, Wl_cx, forgetting_factors))
        updated_lambda = sum(lambda_ * w * ff for lambda_, w, ff in zip(lambda_cx, Wl_cx, forgetting_factors))

        # Compute contextual trust T_cx_j
        T_cx_j = updated_alpha + updated_beta + updated_lambda 
        
        return T_cx_j


# Example usage
# alpha_cx = [0.5, 0.7, 0.8]  # Success feedback values for each transaction
# beta_cx = [0.3, 0.2, 0.1]   # Uncertain feedback values for each transaction
# lambda_cx = [0.2, 0.1, 0.1] # Failure feedback values for each transaction
# Wl_cx = [1, 0.9, 0.8]       # Weights for each transaction
# N_cx = 3                    # Total number of transactions

# T_cx_j = compute_contextual_trust(alpha_cx, beta_cx, lambda_cx, Wl_cx, N_cx)



    def compute_reputation(self,trustor : GenericDevice, trustee : GenericDevice, trust_value : float, report : SendingPacket, situation_settings):
        """
        Compute the reputation R_j of an object based on contextual trusts and context weights.

        Parameters:
        T_cx_j_list (list): List of contextual trust values T_cx_j for each context.
        W_cx_list (list): List of weights for each context.
        NR_cx (int): Total number of recommendations received across all contexts.

        Returns:
        float: The computed reputation R_j of the object.
        """

        


        # Calculate the sum of all contextual trusts multiplied by the context weights
        weighted_sum = sum(T_cx_j * W_cx for T_cx_j, W_cx in zip(T_cx_j_list, W_cx_list))

        # Compute the reputation R_j
        R_j = weighted_sum / NR_cx
        return R_j


# # Example values
# T_cx_j_list = [0.7, 0.8, 0.6]  # Contextual trust values for each context
# W_cx_list = [1.2, 1.0, 0.8]    # Weights for each context
# NR_cx = 30                     # Total number of recommendations received

# # Compute the reputation
# R_j = compute_reputation(T_cx_j_list, W_cx_list, NR_cx)
