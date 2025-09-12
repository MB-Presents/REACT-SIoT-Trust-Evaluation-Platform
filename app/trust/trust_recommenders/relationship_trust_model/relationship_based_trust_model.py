

from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from core.models.uniform.components.report import SendingPacket
from trust.trust_recommenders.common.social_relationships import SocialRelationships


from trust.trust_recommenders.interface_trust_model import ITrustComputationModel


if TYPE_CHECKING:
    from trust.situation_recognition_module.situation_recognition import SituationSettings
    
    from core.models.devices.genric_iot_device import GenericDevice

class RelationshipTrustModel(ITrustComputationModel):
    

    def computate_trust_value(self, trustor : GenericDevice, 
                                trustee : GenericDevice,
                                request : SendingPacket = None,
                                sensory_parameters : dict = None,
                                situation_settings : SituationSettings = None) -> float:
        
        if trustor.trust_manager.relationship_controller.relationship_manager.exists_relationship_by_subjects(trustor, trustee, request):
            return trustor.trust_manager.relationship_controller.get(trustor, trustee, request).trust_value
      
        elif not trustor.trust_manager.relationship_controller.relationship_manager.exists_relationship_by_subjects(trustor, trustee, request):
            
            # social_relationships = SocialRelationships()
            return 0.5
            
          

        raise ValueError("Relationship does not exist") 


    def preprocess_trust_evaluation(self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> float:
        pass
    
    
    def check_compliance(           self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> bool:
        pass
    

    def postprocessing_trust_evaluation(self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> float:
        pass
    