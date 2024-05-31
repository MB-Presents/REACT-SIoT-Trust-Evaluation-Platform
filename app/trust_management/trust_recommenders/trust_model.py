from enum import Enum
from trust_management.trust_recommenders.context_based_trust_models.cbstm_rafey_2016 import ContextBasedTrustModelIoT
from trust_management.trust_recommenders.context_based_trust_models.ctms_abderrahim_2017 import ContextBasedTrustManagementSystem
from trust_management.trust_recommenders.context_based_trust_models.mutual_context_aware_trustworthy_service_evaluation import MutualContextAwareTrustworthyServiceEvaluationModel
from trust_management.trust_recommenders.relationship_trust_model.relationship_based_trust_model import RelationshipTrustModel


class TrustComputationModel(Enum):
    
    
    RELATIONSHIP_BASED_TRUST_MODEL = RelationshipTrustModel()
    
    MUTUAL_CONTEXT_AWARE_TRUSTWORTHY_SERVICE_EVALUATION = MutualContextAwareTrustworthyServiceEvaluationModel()
    CONTEXT_BASED_TRUST_MODEL_FOR_IOT = ContextBasedTrustModelIoT()
    CONTEXT_BASED_TRUST_MANAGEMENT_SYSTEM_FOR_IOT = ContextBasedTrustManagementSystem()

    
    
    # MAG_SIOT = MAGSIoT()
    # CTMSD = CTMSD()
    # MFM_HTM_SIOT = MFMHTMSIoT()
    # MPTM_SIOT = MPTMSIoT()
    
    