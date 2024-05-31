from __future__ import annotations
from collections import defaultdict
from copy import copy

from typing import TYPE_CHECKING, List, Tuple, Dict, Union

from uuid import UUID

from trust_management.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust_management.data_models.transaction.data_models.direct_recommendation import DirectRecommendation
from trust_management.data_models.transaction.data_models.indirect_recommendation import IndirectRecommendation


from trust_management.data_models.transaction.status import TransactionStatus
from data.simulation.scenario_constants import Constants as sc

if TYPE_CHECKING:
    False
    # from trust_management.data_models.transaction.data_models.trust_transaction import Transaction


class TransactionManager:
    def __init__(self):
        
        
        

        # Mixed Use unverified und update the transaciton once it is verified.
        self.trust_transactions : Dict[UUID,AbstractTransaction] = defaultdict(list)
        self.trust_transactions_pairs : Dict[Tuple[str,str],List[AbstractTransaction]] = defaultdict(list)
        self.transactions_by_trustee_id: Dict[str, List[AbstractTransaction]] = defaultdict(list)
        self.transactions_by_report_id: Dict[UUID, List[AbstractTransaction]] = defaultdict(list)
        
        self.recommendation_transactions : Dict[UUID,List[AbstractTransaction]] = defaultdict(list)
        self.transactions_by_recommender_id: Dict[str, List[AbstractTransaction]] = defaultdict(list)
        self.recommendations_of_trust_subject : Dict[Tuple[str,str],List[AbstractTransaction]] = defaultdict(list)
        self.recommendations_of_trust_subject_transaction_context : Dict[Tuple[str,str],List[AbstractTransaction]] = defaultdict(list)
        
        
        self.transactions_by_recommender_transaction_context: Dict[Tuple[str,str], List[AbstractTransaction]] = defaultdict(list)
        self.transactions_by_transaction_context: Dict[str, List[AbstractTransaction]] = defaultdict(list)
        self.transactions_by_trustee_and_transaction_context: Dict[Tuple[str,str], List[AbstractTransaction]] = defaultdict(list)
        


        # Unverified
        self.unverified_trust_transactions : Dict[UUID,List[AbstractTransaction]] = defaultdict(list)
        self.unverified_trust_transactions_pairs : Dict[Tuple[str,str],List[AbstractTransaction]] = defaultdict(list)
        self.unverified_trust_transactions_by_trustee : Dict[str,List[AbstractTransaction]] = defaultdict(list)
        self.unverified_trust_transactions_by_report_id : Dict[UUID,List[AbstractTransaction]] = defaultdict(list)
        
        self.unverified_recommendation_transactions : Dict[UUID,List[AbstractTransaction]] = defaultdict(list)
        self.unverified_trust_transactions_by_recommender_id : Dict[str,List[AbstractTransaction]] = defaultdict(list)
        self.unverified_recommendations_of_trust_subject : Dict[str,List[AbstractTransaction]] = defaultdict(list)
        self.unverified_recommendations_of_trust_subject_transaction_context : Dict[str,List[AbstractTransaction]] = defaultdict(list)    
        
        self.unverified_trust_transactions_by_transaction_context: Dict[str, List[AbstractTransaction]] = defaultdict(list)
        self.unverified_trust_transactions_by_trustee_and_transaction_context: Dict[Tuple[str,str], List[AbstractTransaction]] = defaultdict(list)
        self.unverified_trust_transactions_by_recommender_transaction_context: Dict[Tuple[str,str], List[AbstractTransaction]] = defaultdict(list)
        
        # Verified: Generel, direct trust transactions, recommendations, context-based list
        self.verified_trust_transactions : Dict[UUID,List[AbstractTransaction]] = defaultdict(list)
        self.verified_trust_transactions_pairs : Dict[Tuple[str,str],List[AbstractTransaction]] = defaultdict(list)
        self.verified_trust_transactions_by_trustee : Dict[str,List[AbstractTransaction]] = defaultdict(list)
        self.verified_trust_transactions_by_report_id : Dict[UUID,List[AbstractTransaction]] = defaultdict(list)
        
        self.verified_recommendation_transactions : Dict[UUID,List[AbstractTransaction]] = defaultdict(list)
        self.verified_trust_transactions_by_recommender_id : Dict[str,List[AbstractTransaction]] = defaultdict(list)
        self.verified_recommendations_of_trust_subject_transaction_context : Dict[str,List[AbstractTransaction]] = defaultdict(list)    
        self.verified_recommendations_of_trust_subject : Dict[str,List[AbstractTransaction]] = defaultdict(list)
        
        self.verified_trust_transactions_by_transaction_context: Dict[str, List[AbstractTransaction]] = defaultdict(list)
        self.verified_trust_transactions_by_trustee_and_transaction_context: Dict[Tuple[str,str], List[AbstractTransaction]] = defaultdict(list)
        self.verified_trust_transactions_by_recommender_transaction_context: Dict[Tuple[str,str], List[AbstractTransaction]] = defaultdict(list)
        
         
        self.transaction_frequency : Dict[Tuple[str,str],int] = {}
        self.recommended_transactions_ids : Dict[UUID,UUID] = defaultdict(list)
        self.trust_transactions_excluding_indirect_recommendations : Dict[UUID,AbstractTransaction] = defaultdict(list)
            
            
            
    def add_transaction(self, transaction: AbstractTransaction):
        # Common identifiers
        
        if transaction._id in self.trust_transactions.keys():
            raise Exception(f"Transaction with id {transaction._id} already exists.")
        
        trustor_id = transaction.trustor._id
        trustee_id = transaction.trustee._id
        transaction_id = transaction._id
        transaction_context = transaction.task_context.request_type.name
        
        request_id = transaction.task_context.report_id

        # Add to general and pair lists
        self.trust_transactions[transaction_id] = transaction
        self.trust_transactions_pairs[(trustor_id, trustee_id)].append(transaction)
        self.transactions_by_report_id[transaction.task_context.report_id].append(transaction)
        self.transactions_by_trustee_id[trustee_id].append(transaction)
        
        ### Generatl
        self.transactions_by_transaction_context[transaction_context]
        self.transactions_by_trustee_and_transaction_context[(trustee_id, transaction_context)].append(transaction)
        
        
        # Unverified
        self.unverified_trust_transactions[transaction_id].append(transaction)
        self.unverified_trust_transactions_pairs[(trustor_id, trustee_id)].append(transaction)
        self.unverified_trust_transactions_by_trustee[trustee_id].append(transaction)
        self.unverified_trust_transactions_by_report_id[request_id].append(transaction)
        
        self.unverified_trust_transactions_by_transaction_context[transaction_context].append(transaction)
        self.unverified_trust_transactions_by_trustee_and_transaction_context[(trustee_id, transaction_context)].append(transaction)
        
        self.recommended_transactions_ids[transaction._id] = transaction._id
        
        
        # Sharable
        self.trust_transactions_excluding_indirect_recommendations[transaction_id] = transaction
        
        self._update_transaction_frequency(trustor_id, trustee_id)
        

    def add_direct_recommendation(self, recommendation: DirectRecommendation):
        
        
        if recommendation._id in self.trust_transactions.keys():
            raise Exception(f"Transaction with id {recommendation._id} already exists.")
        
        if not isinstance(recommendation, DirectRecommendation):
            raise Exception(f"Transaction with id {recommendation._id} already exists.")
        
        # Common identifiers
        trustor_id = recommendation.trustor._id
        trustee_id = recommendation.trustee._id
        transaction_id = recommendation._id
        transaction_context = recommendation.task_context.request_type.name
        request_id = recommendation.task_context.report_id


                
        
        if  recommendation._id in self.recommended_transactions_ids.keys() or \
            recommendation.parent_transaction._id in self.recommended_transactions_ids.keys():
                
            raise Exception(f"Transaction with id {recommendation._id} already exists.")
        
        
        if recommendation.parent_transaction._id not in self.trust_transactions.keys():
            self.recommended_transactions_ids[recommendation._id] = recommendation._id
        
        if recommendation.parent_transaction._id not in self.trust_transactions.keys():
            self.recommended_transactions_ids[recommendation.parent_transaction._id] = recommendation.parent_transaction._id


        # Add to general and pair lists

        self.trust_transactions_excluding_indirect_recommendations[transaction_id] = recommendation

        # Add to general and pair lists
        self._add_recommendation(recommendation, trustor_id, trustee_id, transaction_id, transaction_context, request_id)

    def add_indirect_recommendation(self, indirect_recommendation: IndirectRecommendation):
        
        if indirect_recommendation._id in self.trust_transactions.keys():
            raise Exception(f"Transaction with id {indirect_recommendation._id} already exists.")
        
        if not isinstance(indirect_recommendation, IndirectRecommendation):
            raise Exception(f"Transaction with id {indirect_recommendation._id} already exists.")
        
        # Common identifiers
        trustor_id = indirect_recommendation.trustor._id
        trustee_id = indirect_recommendation.trustee._id
        transaction_id = indirect_recommendation._id
        transaction_context = indirect_recommendation.task_context.request_type.name
        request_id = indirect_recommendation.task_context.report_id

        
        # if indirect_recommendation._id in self.recommended_transactions_ids.keys() or indirect_recommendation.parent_transaction._id in self.recommended_transactions_ids.keys() or indirect_recommendation.parent_transaction.parent_transaction._id in self.recommended_transactions_ids.keys():
        #     raise Exception(f"Transaction with id {indirect_recommendation._id} already exists.")
        
        
        if indirect_recommendation.parent_transaction._id not in self.trust_transactions.keys():
        
            self.recommended_transactions_ids[indirect_recommendation._id] = indirect_recommendation._id
        
        if indirect_recommendation.parent_transaction._id not in self.trust_transactions.keys():
        
            self.recommended_transactions_ids[indirect_recommendation.parent_transaction._id] = indirect_recommendation.parent_transaction._id


        # Add to general and pair lists
        self._add_recommendation(indirect_recommendation, trustor_id, trustee_id, transaction_id, transaction_context, request_id)



    def _add_recommendation(self, recommendation : Union[IndirectRecommendation, DirectRecommendation], trustor_id, trustee_id, transaction_id, transaction_context, request_id):
        self.trust_transactions[transaction_id]= recommendation
        self.trust_transactions_pairs[(trustor_id, trustee_id)].append(recommendation)
        self.transactions_by_report_id[request_id].append(recommendation)

        
        
        self.recommendation_transactions[transaction_id].append(recommendation)
        self.transactions_by_recommender_id[trustor_id].append(recommendation)
        self.recommendations_of_trust_subject[trustee_id].append(recommendation)
        self.recommendations_of_trust_subject_transaction_context[(trustee_id, transaction_context)].append(recommendation)
        
        
        
        self.transactions_by_recommender_transaction_context[(trustor_id, transaction_context)].append(recommendation)
        self.transactions_by_transaction_context[transaction_context].append(recommendation)
        self.transactions_by_trustee_and_transaction_context[(trustee_id, transaction_context)].append(recommendation)


        
        self.unverified_recommendation_transactions[transaction_id].append(recommendation)
        self.unverified_recommendations_of_trust_subject[trustee_id].append(recommendation)
        self.unverified_trust_transactions_by_recommender_id[trustor_id].append(recommendation)
        self.unverified_recommendations_of_trust_subject_transaction_context[(trustee_id, transaction_context)].append(recommendation)
        


        self.unverified_trust_transactions_by_recommender_transaction_context[(trustor_id, transaction_context)].append(recommendation)
        self.unverified_trust_transactions_by_transaction_context[transaction_context].append(recommendation)
        self.unverified_trust_transactions_by_trustee_and_transaction_context[(trustee_id, transaction_context)].append(recommendation)
        
        
        
        
        
        
        
        # self.recommended_transactions_ids[recommendation.parent_transaction._id] = recommendation.parent_transaction._id


    def get_recommended_transactions_ids(self) -> Dict[UUID,UUID]:
        return self.recommended_transactions_ids


    def update_transaction(self, transaction: AbstractTransaction, new_value: float):
        transaction.trust_value = new_value
        transaction.status = TransactionStatus.VERIFIED
        transaction.verification_time = copy(sc.TIME)
        
        self._move_to_verified_transactions(transaction, transaction._id)

    def update_recommendation(self, transaction: DirectRecommendation, new_value: float):
        transaction.trust_value = new_value
        transaction.status = TransactionStatus.VERIFIED
        transaction.transaction_context.creation_time = copy(sc.TIME)
        
        self._move_to_verified_recommendations(transaction, transaction._id)


    def _move_to_verified_transactions(self, transaction: AbstractTransaction, transaction_id: UUID):
        # Common identifiers
        trustor_id = transaction.trustor._id
        trustee_id = transaction.trustee._id
        transaction_context = transaction.task_context.request_type.name
        request_id = transaction.task_context.report_id

        self.trust_transactions[transaction_id] = transaction

        self._update_verified_transaction_lists(transaction, transaction_id, trustor_id, trustee_id, transaction_context)

        self._remove_from_unverified_transaction_lists(transaction, transaction_id, trustor_id, trustee_id, request_id, transaction_context)
        

    

    def _update_verified_transaction_lists(self, transaction : AbstractTransaction, transaction_id, trustor_id : str, trustee_id : str, transaction_context):
        
        self.verified_trust_transactions[transaction_id] = transaction
        self._append_to_list(self.verified_trust_transactions_pairs, (trustor_id, trustee_id), transaction)
        self._append_to_list(self.verified_trust_transactions_by_trustee, trustee_id, transaction)
        self._append_to_list(self.verified_trust_transactions_by_report_id, transaction.task_context.report_id, transaction)
        self._append_to_list(self.verified_trust_transactions_by_transaction_context, transaction_context, transaction)
        self._append_to_list(self.verified_trust_transactions_by_trustee_and_transaction_context, (trustee_id, transaction_context), transaction)

    def _remove_from_unverified_transaction_lists(self, transaction, transaction_id, trustor_id, trustee_id, request_id, transaction_context):
        self._remove_transaction(self.unverified_trust_transactions, transaction_id, transaction)
        self._remove_transaction(self.unverified_trust_transactions_pairs, (trustor_id, trustee_id), transaction)
        self._remove_transaction(self.unverified_trust_transactions_by_trustee, trustee_id, transaction)
        self._remove_transaction(self.unverified_trust_transactions_by_report_id, request_id, transaction)
        self._remove_transaction(self.unverified_trust_transactions_by_transaction_context, transaction_context, transaction)
        self._remove_transaction(self.unverified_trust_transactions_by_trustee_and_transaction_context, (trustee_id, transaction_context), transaction)
            
            
    def _append_to_list(self, dictionary, key, transaction):
        if key not in dictionary:
            dictionary[key] = []
        dictionary[key].append(transaction)

    def _remove_transaction(self, dictionary, key, transaction):
        if key in dictionary:
            if transaction in dictionary[key]:
                dictionary[key].remove(transaction)
            if len(dictionary[key]) == 0:
                del dictionary[key]
            

    def _move_to_verified_recommendations(self, transaction: DirectRecommendation, transaction_id: UUID):
        # Common identifiers
        trustor_id = transaction.trustor._id
        trustee_id = transaction.trustee._id
        transaction_context = transaction.task_context.request_type.name
        
        # Update all trust transactions through copy by reference
        self.trust_transactions[transaction_id] = transaction

        
        self.verified_trust_transactions[transaction_id].append(transaction)
        self.verified_trust_transactions_pairs[(trustor_id, trustee_id)].append(transaction)


        self.verified_recommendation_transactions[transaction_id].append(transaction)
        self.verified_trust_transactions_by_recommender_id[trustor_id].append(transaction)
        self.verified_recommendations_of_trust_subject[trustee_id].append(transaction)
        
        self.verified_recommendations_of_trust_subject_transaction_context[(trustee_id, transaction_context)].append(transaction)
        self.verified_trust_transactions_by_recommender_transaction_context[(trustor_id, transaction_context)].append(transaction)
        self.verified_trust_transactions_by_transaction_context[transaction_context].append(transaction)
        self.verified_trust_transactions_by_trustee_and_transaction_context[(trustee_id, transaction_context)].append(transaction)
        

        # Remove from unverified lists
        self.unverified_recommendation_transactions[transaction_id].remove(transaction)
        self.unverified_trust_transactions_by_recommender_id[trustor_id].remove(transaction)
        self.unverified_recommendations_of_trust_subject[trustee_id].remove(transaction)

        # Remove from context-specific lists
        self.unverified_trust_transactions_by_recommender_transaction_context[(trustor_id, transaction_context)].remove(transaction)
        self.unverified_recommendations_of_trust_subject_transaction_context[(trustee_id, transaction_context)].remove(transaction)
        self.unverified_trust_transactions_by_transaction_context[transaction_context].remove(transaction)
        self.unverified_trust_transactions_by_trustee_and_transaction_context[(trustee_id, transaction_context)].remove(transaction)

    def get_transactions(self) -> Dict[UUID, AbstractTransaction]:
        return self.trust_transactions.items()
    
    def get_transactions_by_pairs(self, trustor_id : str, trustee_id : str) -> List[AbstractTransaction]:
        return self.trust_transactions_pairs.get((trustor_id, trustee_id), [])
        
    def get_transactions_by_report_id(self, report_id: UUID) -> List[AbstractTransaction]:
        return self.transactions_by_report_id.get(report_id, [])

    def get_transactions_by_trustee_id(self, trustee_id: str) -> List[AbstractTransaction]:
        return self.transactions_by_trustee_id.get(trustee_id, [])

    def get_transactions_by_recommender_id(self, recommender_id: str) -> List[AbstractTransaction]:
        return self.transactions_by_recommender_id.get(recommender_id, [])
    
    def get_transactions_by_task_context(self, task_context: str) -> List[AbstractTransaction]:
        return self.transactions_by_transaction_context.get(task_context, [])
    
    def get_transactions_by_trustee_and_task_context(self, trustee_id: str, task_context: str) -> List[AbstractTransaction]:
        return self.transactions_by_trustee_and_transaction_context.get((trustee_id, task_context), [])
    
    def get_transactions_by_recommender_and_task_context(self, recommender_id: str, task_context: str) -> List[AbstractTransaction]:
        return self.transactions_by_recommender_transaction_context.get((recommender_id, task_context), [])
    
    
    
    def get_unverified_transactions(self) -> Dict[UUID, List[AbstractTransaction]]:
        return self.unverified_trust_transactions
    
    def get_unverified_transactions_by_pairs(self, trustor_id : str, trustee_id : str) -> List[AbstractTransaction]:
        return self.unverified_trust_transactions_pairs.get((trustor_id, trustee_id), [])
    
    def get_unverified_transactions_by_trustee_id(self, trustee_id: str) -> List[AbstractTransaction]:
        return self.unverified_trust_transactions_by_trustee.get(trustee_id, [])
    
    def get_unverified_transactions_by_report_id(self, report_id: UUID) -> List[AbstractTransaction]:
        return self.unverified_trust_transactions_by_report_id.get(report_id, [])
    
    def get_unverified_transactions_by_recommender_id(self, recommender_id: str) -> List[AbstractTransaction]:
        return self.unverified_trust_transactions_by_recommender_id.get(recommender_id, [])
    
    def get_unverified_transactions_by_task_context(self, task_context: str) -> List[AbstractTransaction]:
        return self.unverified_trust_transactions_by_transaction_context.get(task_context, [])
    
    def get_unverified_transactions_by_trustee_and_task_context(self, trustee_id: str, task_context: str) -> List[AbstractTransaction]:
        return self.unverified_trust_transactions_by_trustee_and_transaction_context.get((trustee_id, task_context), [])
    
    def get_unverified_transactions_by_recommender_and_task_context(self, recommender_id: str, task_context: str) -> List[AbstractTransaction]:
        return self.unverified_trust_transactions_by_recommender_transaction_context.get((recommender_id, task_context), [])
    
    
    
    def get_verified_transactions(self) -> Dict[UUID, List[AbstractTransaction]]:
        return self.verified_trust_transactions
    
    def get_verified_transactions_by_pairs(self, trustor_id : str, trustee_id : str) -> List[AbstractTransaction]:
        return self.verified_trust_transactions_pairs.get((trustor_id, trustee_id), [])
    
    def get_verified_transactions_by_trustee_id(self, trustee_id: str) -> List[AbstractTransaction]:
        return self.verified_trust_transactions_by_trustee.get(trustee_id, [])
    
    def get_verified_transactions_by_report_id(self, report_id: UUID) -> List[AbstractTransaction]:
        return self.verified_trust_transactions_by_report_id.get(report_id, [])
    
    def get_verified_transactions_by_recommender_id(self, recommender_id: str) -> List[AbstractTransaction]:
        return self.verified_trust_transactions_by_recommender_id.get(recommender_id, [])
    
    def get_verified_transactions_by_task_context(self, task_context: str) -> List[AbstractTransaction]:
        return self.verified_trust_transactions_by_transaction_context.get(task_context, [])
    
    def get_verified_transactions_by_trustee_and_task_context(self, trustee_id: str, task_context: str) -> List[AbstractTransaction]:
        return self.verified_trust_transactions_by_trustee_and_transaction_context.get((trustee_id, task_context), [])
    
    def get_verified_transactions_by_recommender_and_task_context(self, recommender_id: str, task_context: str) -> List[AbstractTransaction]:
        return self.verified_trust_transactions_by_recommender_transaction_context.get((recommender_id, task_context), [])
    
    def get_recommendations_of_trust_subject(self, trust_subject_id: str) -> List[AbstractTransaction]:
        return self.recommendations_of_trust_subject.get(trust_subject_id, [])
    
    def get_recommendations_of_trust_subject_by_task_context(self, trust_subject_id: str, task_context: str) -> List[AbstractTransaction]:
        return self.recommendations_of_trust_subject.get((trust_subject_id, task_context), [])
    
    
    
    def _update_transaction_frequency(self, trustor_id: str, trustee_id: str):
        # Increment the count of transactions between the trustor and trustee
        
        pair = (trustor_id, trustee_id)
        
        if pair not in self.transaction_frequency.keys():
            self.transaction_frequency[pair] = 0
        
        
        self.transaction_frequency[pair] += 1

    def get_transaction_frequency(self, trustor_id: str, trustee_id: str) -> int:
        
        pair = (trustor_id, trustee_id)
        
        if pair in self.transaction_frequency.keys():
        
            return self.transaction_frequency[pair]

        self.transaction_frequency[pair] = 0
        return self.transaction_frequency[pair]
    

        # self.transaction_frequency[pair] = 0
        raise Exception(f"Transaction frequency between trustor {trustor_id} and trustee {trustee_id} does not exist.")

    def get_num_transactions(self) -> int:
        
        if len(self.trust_transactions.keys()) == 0:
            return 0
        
        elif len(self.trust_transactions.keys()) > 0:
            return len(self.trust_transactions.keys())
        
        


    def get_num_trustee_transactions(self, trustee_id: str) -> int:
        
        if len(self.transactions_by_trustee_id[trustee_id]) == 0:
            return 0
        
        
        return len(self.transactions_by_trustee_id[trustee_id])
    
