
from __future__ import annotations

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Union








if TYPE_CHECKING:

    from trust.data_models.TrasactionExchangeScheme import TransactionExchangeScheme
    from trust.data_models.reputation.reputation import ReputationComputationStrategy, ReputationContextSettings, ReputationScope

    from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod


    from trust.trust_recommenders.trust_model import TrustComputationModel
    from trust.trust_update.trust_update import TrustUpdateModel
    from trust.adaptive_trust_model_selector.ITrustModelSelectionModel import ITrustModelSelectionModel

class TrustManagementSettings:

    USE_RELATIONSHIP_CONTEXT : bool = False
    
    MAX_TRANSACTION_EXCHANGE_DISTANCE = 30
    TRANSACTION_EXCHANGE_SCHEME : TransactionExchangeScheme = None
    
    REPUTATION_SCOPE : ReputationScope = None
    REPUTATION_CONTEXT : ReputationContextSettings = None
    REPUTATION_COMPUTATION_STRATEGY : ReputationComputationStrategy = None
    
    # THis describeds the required threshold to avoid trust computation and rely on relationship value
    TRUSTWORTHY_THRESHOLD_OF_RELATIONSHIPS : float = 0.7
    THRESHOLD_FOR_NUM_OF_TRUSTWORTHY_RELATIONSHIPS : float = 3
    
    USES_ADAPTIVE_TRUST_MODEL_SELECTION = False
    ADAPTIVE_TRUST_MODEL_SELECTOR : ITrustModelSelectionModel = None
    
    TRUST_COMPUTATION_MODEL : TrustComputationModel = None
    TRUST_DECISION_MAKING_MODEL : TrustDecisionMethod = None
    TRUST_UPDATE_MODEL : TrustUpdateModel = None   
    
    TRUST_TRANSACTION_THRESHOLD : float = 0.5
    TRUST_THRESHOLD_RELATIONSHIP : float = 0.5
    
    TRUST_MODEL_SCHEME : TrustModelScheme = None
    
    TRUST_SITUATION_SETTINGS = None
    
    
class TrustModelScheme():
    
    def __init__(self, 
                 trust_computation_model : TrustComputationModel, 
                 trust_decision_making_model : TrustDecisionMethod, 
                 trust_update_model : TrustUpdateModel = None
                 ):
        
        self.trust_computation_model = trust_computation_model
        self.trust_decision_making_model = trust_decision_making_model
        self.trust_update_model = trust_update_model
