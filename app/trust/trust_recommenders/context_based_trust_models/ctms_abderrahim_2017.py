
from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

from core.models.uniform.components.report import SendingPacket
from trust.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust.situation_recognition_module.situation_recognition import SituationSettings
from trust.trust_recommenders.common.social_relationships import SocialRelationships

import trust.trust_recommenders.common.social_network_analysis as social_network_analysis



from trust.trust_recommenders.interface_trust_model import ITrustComputationModel


if TYPE_CHECKING:
    from trust.data_models.relationship.relationship_controller import RelationshipController
    from trust.situation_recognition_module.situation_recognition import SituationSettings
    from core.models.uniform.components.report import SendingPacket
    from core.models.devices.genric_iot_device import GenericDevice

class ContextBasedTrustManagementSystem(ITrustComputationModel):
    
    
    def __init__(self):
        
        
        self.social_relationships = SocialRelationships(
            value_object_owner_relationship=0.9,
            value_co_location=0.7,
            value_social_object_relationship=0.5,
            value_parental_object_relationship=0.5            
        )
        
        self.w_social_friendship = 0.5
        self.w_social_community_of_interest = 0.5
        self.w_social_object_similarity = 0.5
    
        self.w_reputation_social_similarity = 0.5
    
    
    def preprocess_trust_evaluation(self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> float:
        
        
        selected_service_provider : GenericDevice = None
    

        if len(request.service_providers) > 1:
            
            # Apply decision tree to select the best service provider
            pass
        
        elif request.service_providers == 1:
        
            request.service_providers = {}
            request.service_providers[selected_service_provider._id] = selected_service_provider
        
        return selected_service_provider
    
    
    def computate_trust_value(self, 
                            trustor : GenericDevice, 
                            trustee : GenericDevice,
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> float:
        
        credibility = np.nan
        
        # trustee = next(iter(request.service_providers.values()))
        
        if trustee == None:
            return credibility
        
        
        if trustor.trust_manager.relationship_controller.relationship_manager.exists_relationship_by_subjects(trustor, trustee, request):
            credibility = trustor.trust_manager.relationship_controller.get(trustor, trustee, request).trust_value
        
        elif not trustor.trust_manager.relationship_controller.relationship_manager.exists_relationship_by_subjects(trustee, trustor, request):
            # trust_value = TODO compute_trust_value
            
            # Train decision tree on some data:

    
            # Compute trust value
            friendship_similarity = social_network_analysis.get_friendship_similarity(trustor, trustee)
            community_of_interest_similarity = social_network_analysis.get_social_similar_community(trustor, trustee)
            object_similarity = social_network_analysis.get_object_profile_similarity(trustor, trustee)
            
            reputation = 0
            
            if trustee._id in trustor.trust_manager.reputation_controller.reputations.keys():
                reputation = trustor.trust_manager.reputation_controller.reputations[trustee._id]
            
        
        
            social_similarity = self.w_social_friendship * friendship_similarity + self.w_social_community_of_interest * community_of_interest_similarity + self.w_social_object_similarity * object_similarity
            credibility = self.w_reputation_social_similarity * reputation + (1 - self.w_reputation_social_similarity * (social_similarity))                        
        
        return credibility
    

    def postprocessing_trust_evaluation(self, trustor: GenericDevice, request: SendingPacket = None, sensory_parameters: dict = None, situation_settings: SituationSettings = None) -> float:
        
        for service_provider_id, service_provider in request.service_providers.items():    
            trustor.trust_manager.add_trust_transaction(trustor, service_provider, request.trust_score, reporting_time=None, transaction_context=request, role=TrustVerfierRoles.SERVICE_PROVIDER)


    def check_compliance(   self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> bool:
    
        return super().check_compliance(trustor, request, sensory_parameters, situation_settings)