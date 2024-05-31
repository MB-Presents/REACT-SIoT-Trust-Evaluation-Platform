from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List
from data_models.iot_devices.common import Service
from trust_management.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust_management.data_models.transaction.data_models.trust_transaction import Transaction
from trust_management.decision_making_module.trust_decision_maker import TrustDecisionMethod
from trust_management.settings import TrustManagementSettings


from trust_management.trust_recommenders.common.social_relationships import SocialRelationships


from numpy import dot
from numpy.linalg import norm
import numpy as np

import trust_management.trust_recommenders.common.social_network_analysis as social_network_analysis 
from trust_management.trust_recommenders.interface_trust_model import ITrustComputationModel
from trust_management.trust_update.trust_update import TrustUpdateModel


if TYPE_CHECKING:

    from trust_management.situation_recognition_module.situation_recognition import SituationSettings
    from data_models.report_management.report.report import SendingPacket
    from data_models.iot_devices.genric_iot_device import GenericDevice


class MutualContextAwareTrustworthyServiceEvaluationModel(ITrustComputationModel):
    
    
    def __init__(self) -> None:
        super().__init__()
        
        self.trust_decision_model : TrustDecisionMethod  = TrustManagementSettings.TRUST_DECISION_MAKING_MODEL
        self.trust_update_model : TrustUpdateModel = None
        
        self.social_relationships = SocialRelationships(
            value_co_location = 1,
            value_co_work = 0.9,
            value_object_owner_relationship = 0.8,
            value_social_object_relationship = 0.7,
            value_parental_object_relationship = 0.5,
            co_location_distance = 10.0,
            default_trust_value = 0
        )
        
        
        # self.sdissimilarity = 0.5  # Example social dissimilarity value
        self.w_friendship = 0.33   # Weight for friendship
        self.w_community = 0.33    # Weight for community
        self.w_relation = 0.33     # Weight for relation
        
        self.delta = 0.5  # Example weight factor
        self.num_n_latest_transactions = 5  # Number of latest transactions to consider
        
        
    def check_compliance(   self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> bool:
        pass
        

    def preprocess_trust_evaluation(self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> float:
        
        
        pass
    
    def postprocessing_trust_evaluation(self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None, 
                                    situation_settings : SituationSettings = None) -> float:
        pass
    
    
    
    def computate_trust_value(self, trustor : GenericDevice, 
                                    trustee : GenericDevice,
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> float:
        
        
        
        advertised_services = [service.name for service_id, service in trustee._services.items()]
        expected_service = [service.name for service in Service]
        
        
        advertisted_resources_values = trustee._computation_capability_class.value
        expected_service_values = 2
        
        
        qos_trust = self.calculate_cqosstrust(advertisted_resources_values, expected_service_values)
        
        # Compute social score
        social_similarity_friendship = social_network_analysis.get_friendship_similarity_by_context(trustor, trustee, request)
        social_similarity_community = social_network_analysis.get_social_similar_community(trustor, trustee)
        social_relationship = self.calculate_ssimr(trustor, trustee, request)
        
        css_trust = self.calculate_csstrust(social_similarity_friendship, social_similarity_community, social_relationship)
        
        
        # Compute feedback score
        context_trust_feedback = self.calculate_cft(trustor, trustee,self.num_n_latest_transactions)
        variance_trust_feedback = self.calculate_variance_cft(trustor, trustee, self.num_n_latest_transactions)
        

        # Aggregate the trust scores
        trust_value = self.aggreate_trust_scores(qos_trust, css_trust, variance_trust_feedback, context_trust_feedback)
        
        
        return trust_value
        
        
    def calculate_ssimr(self, trustor : GenericDevice, trustee : GenericDevice, report : SendingPacket) -> float:
        """
        Calculate the Social Similarity Relation (SSimR) metric.

        :param relations_sci: List of social relations for the service-consuming device.
        :param relations_spj: List of social relations for the service-providing device.
        :param task_type_sci: Task type of the service-consuming device.
        :param task_type_spj: Task type of the service-providing device.
        :param relation_weights: Dictionary of weights for different relation and task type combinations.
        :return: SSimR metric value.
        """
        
        
        relationship_value  = self.social_relationships.get_social_relationship_value(trustor, trustee)
        
        # self.task_context = report.report_type
        # They provide the same task type
        
        return relationship_value
        

    def calculate_trust_variance(self, trustor : GenericDevice, trustee : GenericDevice, k):
        """
        Calculate the adjusted trust variance for service-consuming and service-providing devices.

        :param feedback_sci_to_spj: List of historical feedback from SCi to SPj.
        :param feedback_spj_to_sci: List of historical feedback from SPj to SCi.
        :param k: Number of latest transactions to consider.
        :return: Adjusted trust variance for both SCi to SPj and SPj to SCi.
        """
        # Calculate variance in the latest K transactions
        
        
        transactions_trustor : List[Transaction] = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_trust_transaction_pairs(trustor._id, trustee._id).values()
        # transactions_trustee : List[Transaction] = trustee.transaction_controller.transaction_manager.get_trust_transaction_pairs(trustee._id, trustor._id).values()
        
        
        
        transactions_values_trustor = [transaction.trust_value for transaction in transactions_trustor]
        # transactions_values_trustee = [transaction.trust_value for transaction in transactions_trustee]
        
        
        
        
        variance_trustor_to_trustee = np.var(transactions_values_trustor[-k:]) if len(transactions_values_trustor) >= k else 0
        # variance_trustee_to_trustor = np.var(transactions_values_trustee[-k:]) if len(transactions_values_trustee) >= k else 0

        # Apply exponential decay to the variance
        adjusted_variance_sci_to_spj = np.exp(-variance_trustor_to_trustee)
        # adjusted_variance_spj_to_sci = np.exp(-variance_trustee_to_trustor)

        return adjusted_variance_sci_to_spj
        # return adjusted_variance_sci_to_spj, adjusted_variance_spj_to_sci


    def calculate_cqosstrust(self, ex_qos_sci : List[str], ad_qos_spj : List[str]):
        """
        Calculate the Context-aware QoS Similarity based Trust (CQoSSTrust).

        :param ex_qos_sci: Vector of expected QoS by the service-consuming device (SCi).
        :param ad_qos_spj: Vector of advertised QoS by the service-providing device (SPj).
        :return: CQoSSTrust value.
        """
        # Calculate cosine similarity between the two QoS vectors
        cos_sim = dot(ex_qos_sci, ad_qos_spj) / (norm(ex_qos_sci) * norm(ad_qos_spj)) if norm(ex_qos_sci) != 0 and norm(ad_qos_spj) != 0 else 0
        return cos_sim


    def calculate_csstrust(self, ssim_friendship, ssim_community, ssim_relation):
        """
        Calculate the Context-aware Social Similarity based Trust (CSSTrust).

        :param sdissimilarity: Social Dissimilarity between SCi and SPj in the task type context.
        :param w_friendship: Weight for the importance of social similarity friendship.
        :param w_community: Weight for the importance of social similarity community.
        :param w_relation: Weight for the importance of social similarity relation.
        :param ssim_friendship: Social Similarity Friendship value.
        :param ssim_community: Social Similarity Community value.
        :param ssim_relation: Social Similarity Relation value.
        :return: CSSTrust value.
        """
        # Calculate weighted social similarity
        weighted_social_similarity = self.w_friendship * ssim_friendship + self.w_community * ssim_community + self.w_relation * ssim_relation
        
        sdissimilarity = 1 - weighted_social_similarity
        
        # Calculate CSSTrust
        csstrust = np.exp(-sdissimilarity)

        return csstrust


    def calculate_variance_cft(self, trustor : GenericDevice, trustee : GenericDevice, k):
        
        transactions_trustor : List[Transaction] = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_trustee_id(trustee._id)
        # transactions_trustee : List[Transaction] = trustee.transaction_controller.transaction_manager.get_trust_transaction_pairs(trustee._id, trustor._id).values()
        
        cft_values = [transaction.trust_value for transaction in transactions_trustor]
        
        
        n = len(cft_values)
        if k > n:
            return 0.5
            raise ValueError("k should be less than or equal to the number of transactions")
        
        latest_cft_values = cft_values[n-k:]
        mean_cft = np.mean(latest_cft_values)
        variance = sum((x - mean_cft) ** 2 for x in latest_cft_values) / (k - 1)
        return variance


    def calculate_cft(self, trustor : GenericDevice, trustee : GenericDevice, k):
        
        transactions_trustor : List[Transaction] = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transactions_by_trustee_id(trustee._id)
        # transactions_trustee : List[Transaction] = trustee.transaction_controller.transaction_manager.get_trust_transaction_pairs(trustee._id, trustor._id).values()
        
        cft_values = [transaction.trust_value for transaction in transactions_trustor]
        
        
        n = len(cft_values)
        if k > n:
            return 0.5
            raise ValueError("k should be less than or equal to the number of transactions")
        
        latest_cft_values = cft_values[n-k:]
        return sum(latest_cft_values) / k


    def aggreate_trust_scores(self,cqosstrust, csstrust, variance_sci_to_spj, cft_sci_to_spj):
        """
        Calculate MCTSE from Service-Consuming Device (SCi) to Service-Providing Device (SPj).

        :param delta: Weight factor to balance the importance of components.
        :param cqosstrust: CQoSSTrust value between SCi and SPj.
        :param csstrust: CSSTrust value between SCi and SPj.
        :param variance_sci_to_spj: Variance in the latest transactions from SCi to SPj.
        :param cft_sci_to_spj: Contextual Feedback of Trust from SCi to SPj.
        :return: MCTSE value from SCi to SPj.
        """
        return self.delta  * cqosstrust * csstrust + (1 - self.delta) * np.exp(-variance_sci_to_spj) * cft_sci_to_spj



