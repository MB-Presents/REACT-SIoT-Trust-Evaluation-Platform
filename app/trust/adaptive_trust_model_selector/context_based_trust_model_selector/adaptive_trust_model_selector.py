from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple, Union
from core.models.devices.genric_iot_device import GenericDevice
from core.models.uniform.components.report import SendingPacket
from core.models.uniform.components.reporter import SendersEntity
from trust.adaptive_trust_model_selector.ITrustModelSelectionModel import ITrustModelSelectionModel
from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod

from trust.settings import TrustManagementSettings
from trust.situation_recognition_module.situation_recognition import SituationSettings

from trust.trust_recommenders.trust_model import TrustComputationModel
from trust.trust_update.trust_update import TrustUpdateModel


if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler
    from core.models.uniform.components.report import SendingPacket
    from core.models.devices.genric_iot_device import GenericDevice
    from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod
    
    from trust.situation_recognition_module.situation_recognition import SituationSettings
    from core.models.events.simulation_events import SimulationEventManager
    from trust.data_models.relationship.data_models.relationship import Relationship
    from core.models.uniform.components.report_models import ReportType
    from trust.trust_recommenders.context_based_trust_models.cbstm_rafey_2016 import ContextBasedTrustModelIoT
    from trust.trust_recommenders.context_based_trust_models.mutual_context_aware_trustworthy_service_evaluation import MutualContextAwareTrustworthyServiceEvaluationModel
    from trust.trust_recommenders.ontology_based.ontology_based_trust_model import OntologyBasedTrustModel
    from trust.trust_recommenders.relationship_trust_model.relationship_based_trust_model import RelationshipTrustModel


class AdaptiveTrustModelSelector(ITrustModelSelectionModel):

    def __init__(self):
        self.selected_trust_computation_model : Union[RelationshipTrustModel,MutualContextAwareTrustworthyServiceEvaluationModel,ContextBasedTrustModelIoT,OntologyBasedTrustModel] = None
        self.selected_trust_decision_making_model : TrustDecisionMethod = None
        self.selected_trust_update_model : TrustUpdateModel = None
      
    def select_trust_computation_model(self, trustor : GenericDevice, report : SendingPacket, sensory_parameters : dict = None, situation_settings : SituationSettings = None):
                # Select the trust computation strategy 

        


        
        reporters : List[SendersEntity] = list(report.sending_entities.values())
        
        trustor_key = trustor._id
        
        relationships : Dict[Tuple[str,str,ReportType],Relationship] = {}
        
        
        
        # Learn the memory of the trustor and provide trust updates
        for reporter_id, reporter in report.sending_entities.items():
            predictions = trustor.trust_manager._temporal_graph_based_trust_model.trust_update(trustor, reporter.device, request=report, situation_settings=situation_settings)
            
            
        # Get relationships of all requestors
        for reporter in reporters:
            trustor_reporter_relationship = trustor.trust_manager.relationship_controller.get(trustor, reporter.device, report)
            if trustor.trust_manager.relationship_controller.exists(trustor=trustor, trustee=reporter.device, transaction_context=report):
                relationships[(trustor_key, reporter.device._id, report.request_type.value)] = trustor_reporter_relationship
        
        
        # Check if two or more of the relationships are greate than the threshold
        # If so, no need to compute the trust
        num_trustworthy_relationships = self._get_number_of_trustworthy_devices(relationships)
        
        if num_trustworthy_relationships >= TrustManagementSettings.THRESHOLD_FOR_NUM_OF_TRUSTWORTHY_RELATIONSHIPS:
            self.selected_trust_computation_model = TrustComputationModel.RELATIONSHIP_BASED_TRUST_MODEL.value
            return self.selected_trust_computation_model 
        
        # check if sufficient sensing devices for ontology are available?
        # sensory_parameters are already involved into the report
        # Select Ontology-based Model if sufficient sensing devices are available
        
        if len(report.service_providers) >= situation_settings.trust_model_settings.MIN_SERVICE_PROVIDER:
            self.selected_trust_computation_model = TrustComputationModel.ONTOLOGY_BASED_TRUST_MODEL.value
            return self.selected_trust_computation_model
            
            
        if situation_settings.trust_model_settings.TIME_SENSITIVITY_REACHED:
            
            situation_settings.trust_model_settings.MIN_SERVICE_PROVIDER = 1
            
            if len(report.service_providers) >= (situation_settings.trust_model_settings.MIN_SERVICE_PROVIDER):
                return TrustComputationModel.ONTOLOGY_BASED_TRUST_MODEL.value
            return TrustComputationModel.ONTOLOGY_BASED_TRUST_MODEL.value
            
            
            
            
            
            # Use probabilistic model if time sensitivity is reached
            # TODO: Impelement probabilistic model

            # Use attribute-based model if time sensitivity is not reached     
            # TODO: Implement attribute-based model
            # self.selected_trust_computation_model = TrustComputationModel.GRAPH_BASED_TRUST_MODEL.value
    
            # return self.selected_trust_computation_model
        
        self.selected_trust_computation_model = TrustComputationModel.ONTOLOGY_BASED_TRUST_MODEL.value
        
        return self.selected_trust_computation_model
    
        raise NotImplementedError("Adaptive Trust Model Selection is not implemented yet")
        
        
    def select_trust_decision_making_model(self, trustor : GenericDevice, report : SendingPacket, sensory_parameters : dict = None, situation_settings : SituationSettings = None):
        return TrustManagementSettings.TRUST_DECISION_MAKING_MODEL
    
    def select_trust_update_model(self, trustor: GenericDevice, report: SendingPacket, sensory_parameters: dict = None, situation_settings: SituationSettings = None):
        return TrustManagementSettings.TRUST_UPDATE_MODEL
        
    def get_trust_computation_model(self) -> TrustComputationModel:
        return self.selected_trust_computation_model
    
    def get_trust_decision_making_model(self) -> TrustDecisionMethod:
        return self.selected_trust_decision_making_model
    
    def get_trust_update_model(self) -> TrustUpdateModel:
        return self.selected_trust_update_model
    
    def _get_number_of_trustworthy_devices(self,relationships):
        num_trustworthy_relationships = 0
        
        for (trustor_key, trustee_key, task_context),relationship in relationships.items():    
            if relationship.trust_value >= TrustManagementSettings.TRUSTWORTHY_THRESHOLD_OF_RELATIONSHIPS:
                num_trustworthy_relationships += 1
        return num_trustworthy_relationships
    
    
    
