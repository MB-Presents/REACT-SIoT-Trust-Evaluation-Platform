from __future__ import annotations
from typing import TYPE_CHECKING
from data_models.report_management.report.report_models import ReportType



import trust_management.data_aquisition_scheme.data_aquisition_scheme as data_aquisition_scheme
from trust_management.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust_management.decision_making_module.trust_decision_making_interface import ITrustDecisionMaking
from trust_management.settings import TrustManagementSettings


import trust_management.situation_recognition_module.situation_recognition as situation_recognition
from trust_management.trust_recommenders.interface_trust_model import ITrustComputationModel

from data_models.events.simulation_events import VerificationState

from trust_management.trust_update.trust_update_interface import ITrustUpdate

if TYPE_CHECKING:
    from data_models.report_management.report.report import SendingPacket
    from data_models.iot_devices.genric_iot_device import GenericDevice



def send_trust_request(trustor : GenericDevice, request : SendingPacket) -> VerificationState :
  
    sensory_parameters = data_aquisition_scheme.get_sensory_parameters(request)
    situation_settings = situation_recognition.get_situation_settings(request)
    
    TrustManagementSettings.TRUST_SITUATION_SETTINGS = situation_settings
    
    
    #   request informatio of the trust assessment and erisk governance engine
    #   request the trust data acquisistion scheme  
    # Requst the trust assessment profile from the risk government engine based the current request, settings, and the trustor's profile
    # Returns the settings and twhresholds as well as trust indicators
    # trust_assessment_profiel = 
    
    trust_computation_model : ITrustComputationModel = TrustManagementSettings.TRUST_MODEL_SCHEME.trust_computation_model
    trust_decision_model : ITrustDecisionMaking = TrustManagementSettings.TRUST_MODEL_SCHEME.trust_decision_making_model
    trust_update_model : ITrustUpdate = TrustManagementSettings.TRUST_MODEL_SCHEME.trust_update_model
    

    if TrustManagementSettings.USES_ADAPTIVE_TRUST_MODEL_SELECTION:
        trust_computation_model =  TrustManagementSettings.ADAPTIVE_TRUST_MODEL_SELECTOR.select_trust_computation_model(trustor, request, sensory_parameters, situation_settings)
        trust_decision_model =  TrustManagementSettings.ADAPTIVE_TRUST_MODEL_SELECTOR.select_trust_decision_making_model(trustor, request, sensory_parameters, situation_settings)
        trust_update_model = TrustManagementSettings.ADAPTIVE_TRUST_MODEL_SELECTOR.select_trust_update_model(trustor, request, sensory_parameters, situation_settings)
    
    TrustManagementSettings.TRUST_MODEL_SCHEME.trust_update_model = trust_update_model
    TrustManagementSettings.TRUST_MODEL_SCHEME.trust_decision_making_model = trust_decision_model
    TrustManagementSettings.TRUST_MODEL_SCHEME.trust_computation_model = trust_computation_model
    
    
    trust_computation_model.preprocess_trust_evaluation(trustor=trustor, request=request, sensory_parameters=sensory_parameters, situation_settings=situation_settings)
    trust_computation_model.check_compliance(trustor=trustor, request=request, sensory_parameters=sensory_parameters, situation_settings=situation_settings)
    
    
    for trustee_id, reporter in request.sending_entities.items():
        trustee = reporter.device
    
        request.trust_score = trust_computation_model.computate_trust_value(trustor=trustor, trustee=trustee,  request=request, sensory_parameters=sensory_parameters, situation_settings=situation_settings)
        trust_decision = trust_decision_model.make_trust_decision(trustor=trustor, trustee=trustee, trust_value=request.trust_score, request=request, situation_settings=situation_settings)
        
        if trust_decision != VerificationState.UNVERIFIED:    
            
            if request.request_type == ReportType.TraffiCPriorityRequest:
                pass
                
            trustor.trust_manager.add_trust_transaction(trustor=trustor, trustee=trustee, reporting_time=reporter.reporting_time, trust_value=request.trust_score, transaction_context=request, role=TrustVerfierRoles.REPORTER)
        
    #Update supporting entities
    if trust_decision != VerificationState.UNVERIFIED:  
        trust_computation_model.postprocessing_trust_evaluation(trustor=trustor, request=request, situation_settings=situation_settings)
            
            
    return trust_decision
