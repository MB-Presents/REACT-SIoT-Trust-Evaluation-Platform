from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Union
from uuid import UUID




from core.simulation.logging import ObjectType
from trust.data_models import TrustVerifierRoles


from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust.data_models.transaction.data_models.direct_recommendation import DirectRecommendation
from trust.data_models.transaction.data_models.indirect_recommendation import IndirectRecommendation
from trust.data_models.transaction.data_models.trust_transaction import Transaction
from trust.data_models.transaction.transaction_manager import TransactionManager
from trust.data_models.transaction.type import TransactionType
from trust.settings import TrustManagementSettings

import utils.logging as logger

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from trust.data_models.relationship.relationship_controller import RelationshipController
    from core.models.uniform.components.report import SendingPacket
    from trust.data_models.reputation.reputation_controller import ReputationController


class TransactionController:
    def __init__(self):
        
        self.transaction_manager : TransactionManager = TransactionManager()
        self.subscribers : List[Union[RelationshipController, ReputationController]] = []
        self.trust_threshold : float = TrustManagementSettings.TRUST_TRANSACTION_THRESHOLD


    def subscribe(self, subscriber : Union[RelationshipController, ReputationController]):
        self.subscribers.append(subscriber)
        
    def notify_subscribers(self, transaction : Transaction):
        for subscriber in self.subscribers:
            subscriber.update(transaction)

    def add_trust_transaction(self, transaction : Transaction):
        
        self.transaction_manager.add_transaction(transaction)
        self.notify_subscribers(transaction)
        self.log_transaction(transaction)


    def _get_transaction_type(self, original_transaction):
        recommendation_type = None
        
        if isinstance(original_transaction,Transaction):
            recommendation_type = TransactionType.DIRECT_RECOMMENDATION
        
        elif isinstance(original_transaction,DirectRecommendation):
            recommendation_type = TransactionType.INDIRECT_RECOMMENDATION
            
        return recommendation_type   
        
        
    def add_direct_recommendation(self, original_transaction: Transaction, recommender : GenericDevice, recommended_requestor: GenericDevice, trust_subject : GenericDevice):
        
        recommendation = DirectRecommendation(recommender=recommended_requestor, 
                                        recommendee=trust_subject, 
                                        recommended_trust_value=original_transaction.trust_value,
                                        reporting_time=original_transaction.reporting_time,
                                        original_transaction_id = original_transaction._id,
                                        transaction_type= TransactionType.DIRECT_RECOMMENDATION,
                                        transaction_status=original_transaction.status,
                                        task_context=original_transaction.task_context,
                                        parent_transaction=original_transaction,
                                        verification_time=original_transaction.verification_time)
        
        self.transaction_manager.add_direct_recommendation(recommendation)
        self.notify_subscribers(recommendation)
        self.log_transaction(recommendation)
        
    def add_indirect_recommendation(self, original_transaction: DirectRecommendation, recommendee : GenericDevice, recommender: GenericDevice, trust_subject : GenericDevice):
        
        if isinstance(original_transaction, Transaction):
            raise Exception("Only direct recommendations can be used to create indirect recommendations.")
        
        recommendation = IndirectRecommendation(recommender=recommender, 
                                        recommended_trust_subject=trust_subject, 
                                        recommended_trust_value=original_transaction.trust_value,
                                        reporting_time=original_transaction.parent_transaction.reporting_time,
                                        original_transaction_id = original_transaction._id,
                                        transaction_type= TransactionType.INDIRECT_RECOMMENDATION,
                                        transaction_status=original_transaction.status,
                                        task_context=original_transaction.task_context,
                                        parent_transaction=original_transaction,
                                        verification_time=original_transaction.verification_time)
        
        
        self.transaction_manager.add_indirect_recommendation(recommendation)
        self.notify_subscribers(recommendation)
        self.log_transaction(recommendation)
    
    def update(self, request : SendingPacket):

        ground_truth = request.simulation_event.is_authentic
        transactions = self.transaction_manager.get_transactions_by_report_id(request._id)
        
        for index, transaction in enumerate(transactions):
        
            verified_trust_value = None
        
            if not isinstance(transaction, Transaction):
                raise Exception("Only transactions can be verified.")
            
            
            if transaction.role == TrustVerifierRoles.TrustVerfierRoles.REPORTER:
                verified_trust_value = 1 if request.simulation_event.is_authentic else 0
            
            elif transaction.role == TrustVerifierRoles.TrustVerfierRoles.SERVICE_PROVIDER:
                verified_trust_value = self.evaluate_trust(ground_truth, request)
            
            self.transaction_manager.update_transaction(transaction, verified_trust_value)
            self.notify_subscribers(transaction)
            self.log_transaction(transaction)
            

    def evaluate_trust(self, is_claim_true : bool, request : SendingPacket):
        
        verified_trust_value = None
        
        if request.trust_score >= self.trust_threshold and is_claim_true:
            verified_trust_value = 1
        elif request.trust_score < self.trust_threshold and not is_claim_true:
            verified_trust_value = 1
        elif request.trust_score >= self.trust_threshold and not is_claim_true:
            verified_trust_value = 0
        elif request.trust_score < self.trust_threshold and is_claim_true:
            verified_trust_value = 0
        else:
            raise Exception("A combintation does not work correctly.")
        
        
        return verified_trust_value
            

        
    def exists_transaction(self, transaction_id):
        
        if transaction_id not in self.transaction_manager.trust_transactions.keys():
            return False        
        return True


    def log_transaction(self, transaction : AbstractTransaction):
        
                
        # previous_transactions = self.transaction_manager.get_transactions_by_trustee_id(transaction.trustee._id)    
        last_transaction_id, last_trust_value = self.get_last_transaction_of_trustee(transaction.trustee._id)
        last_verified_transaction_id, last_verified_transaction_trust_value = self.get_last_verified_transaction(transaction.trustee._id)
        interaction_frequency = self.transaction_manager.get_transaction_frequency(transaction.trustor._id, transaction.trustee._id)
        parent_transaction_id = transaction.original_transaction_id if isinstance(transaction, DirectRecommendation) else None
        degree_of_trustworthiness = self.get_friendship_similarity_by_transaction(transaction)

        

        try:
        #     transaction_dict = {
        #         'transaction_id' : transaction._id,
        #         'transaction_type' : transaction.type.name,
        #         'trustor' : transaction.trustor._id,
        #         'trustee' : transaction.trustee._id,
        #         'time': transaction.transaction_context.time,
        #         'trustor_location' : transaction.transaction_context.trustor_location,
        #         'trustee_location' : transaction.transaction_context.trustee_location,
        #         'trust_value' : transaction.trust_value,
        #         'status' : transaction.status.name,
        #         'task_context': transaction.task_context.request_type.name,
        #         'trustworthiness' : transaction.trustee._behaviour.name,
        #         'role' : transaction.role.name,
        #         'last_trust_value' : last_trust_value,
        #         'last_verified_transaction_trust_value' : last_verified_transaction_trust_value,
        #         'last_verified_transaction_id' : last_verified_transaction_id,
        #         'last_transaction_id' : last_transaction_id,
        #         'parent_transaction_id' : parent_transaction_id,
        #         'interaction_frequency' : interaction_frequency,
        #         'degree_of_common_friendship' : degree_of_trustworthiness,
        #         'reporting_time' : transaction.reporting_time,
        #         'verification_time' : transaction.verification_time,
        #         'report_trustworthiness' : transaction.task_context.simulation_event.is_authentic,
        #     }
            
            transaction_dict = transaction.to_dict(last_trust_value=last_trust_value,
                                                   last_verified_transaction_trust_value=last_verified_transaction_trust_value,
                                                   last_verified_transaction_id=last_verified_transaction_id,
                                                   last_transaction_id=last_transaction_id,
                                                   parent_transaction_id=parent_transaction_id,
                                                   interaction_frequency=interaction_frequency,
                                                   degree_of_trustworthiness=degree_of_trustworthiness)
            
            
            logger.info(ObjectType.TRUST_TRANSACTION,transaction_dict)
            
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)
            logger.error(e)


    def get_last_transaction_of_trustee(self, trustee_id : str):
        
        
        transactions = self.transaction_manager.get_transactions_by_trustee_id(trustee_id) 
        
        if len(transactions) == 0:
            return None,None
        
        last_transaction : Transaction = transactions[-1] 
        
        last_trust_value = None
        if last_transaction != None:
            last_trust_value = last_transaction.trust_value
        return last_transaction._id,last_trust_value

    def get_last_verified_transaction(self, trustee_id : str):
        
        transactions = self.transaction_manager.get_verified_transactions_by_trustee_id(trustee_id)
        
        if len(transactions) == 0:
            return None,None
    
        return transactions[-1]._id, transactions[-1].trust_value
        
        # last_verified_transaction_id = None
        # transactions = None
        # last_verified_transaction_trust_value = None
        
        # for transaction_id, transaction in previous_transactions.items():
        #     if transaction.status == TransactionStatus.VERIFIED:
        #         transactions = transaction
        #         last_verified_transaction_id = transaction._id
        # if transactions != None:
        #     last_verified_transaction_trust_value = transactions.trust_value
        # return last_verified_transaction_id,last_verified_transaction_trust_value

    def get_friendship_similarity_by_device_pair(self, trustor : GenericDevice , trustee : GenericDevice):
        
        trustworthy_devices_trustor = trustor.trust_manager.relationship_controller.relationship_manager.trustworthy_devices
        trustworthy_devices_trustee = trustee.trust_manager.relationship_controller.relationship_manager.trustworthy_devices
        
        common_trustworhty_devices = set(trustworthy_devices_trustor).intersection(set(trustworthy_devices_trustee)) 
        all_trustworthy_devices = set(trustworthy_devices_trustor).union(set(trustworthy_devices_trustee))

        degree_of_trustworthiness = 0.0
            
        if len(common_trustworhty_devices) != 0: 
            degree_of_trustworthiness = len(common_trustworhty_devices) / len(all_trustworthy_devices)
        return degree_of_trustworthiness

    def get_friendship_similarity_by_transaction(self, transaction : Transaction):
        
        trustworthy_devices_trustor = transaction.trustor.trust_manager.relationship_controller.relationship_manager.trustworthy_devices
        trustworthy_devices_trustee = transaction.trustee.trust_manager.relationship_controller.relationship_manager.trustworthy_devices
        
        common_trustworhty_devices = set(trustworthy_devices_trustor).intersection(set(trustworthy_devices_trustee)) 
        all_trustworthy_devices = set(trustworthy_devices_trustor).union(set(trustworthy_devices_trustee))

        degree_of_trustworthiness = 0.0
            
        if len(common_trustworhty_devices) != 0: 
            degree_of_trustworthiness = len(common_trustworhty_devices) / len(all_trustworthy_devices)
        return degree_of_trustworthiness
    
    def exists_in_recommendations(self, transaciton_id : UUID) -> Dict[UUID,UUID]:
        
        if transaciton_id not in self.transaction_manager.get_recommended_transactions_ids().keys():
            return False
        return True
        