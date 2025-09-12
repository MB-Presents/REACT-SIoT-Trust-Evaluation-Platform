# experiments/design/settings.py
from typing import List
from trust.trust_recommenders.trust_model import TrustComputationModel
from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod
from trust.trust_update.trust_update import TrustUpdateModel
from trust.transaction_exchange_scheme.trust_inference_engine import TransactionExchangeScheme
from trust.adaptive_trust_model_selector import TrustModelSelector
from trust.data_models.reputation.reputation import ReputationScope, ReputationContextSettings, ReputationComputationStrategy

class ExperimentSettings:
    def __init__(self,
                 experiment_id: str,
                 experiment_name: str,
                 verify_authenticity_accident: bool,
                 verify_authenticity_traffic_light: bool,
                 trust_model_name: str,
                 trust_model_description: str,
                 use_relationship_context: bool,
                 trust_computation_model: TrustComputationModel,
                 trust_decision_making_model: TrustDecisionMethod,
                 trust_update_model: TrustUpdateModel,
                 transaction_exchange_scheme: TransactionExchangeScheme,
                 max_transaction_exchange_distance: int,
                 adaptive_trust_model_selector: TrustModelSelector = None,
                 reputation_scope: ReputationScope = ReputationScope.LOCAL,
                 reputation_context: ReputationContextSettings = ReputationContextSettings.NO_CONTEXT,
                 reputation_computation_strategy: ReputationComputationStrategy = ReputationComputationStrategy.AVERAGE_OF_LAST_N_TRANSACTIONS,
                 trustworthy_threshold_for_trustee: float = 0.7,
                 threshold_for_required_trustworthy_relationships: int = 2,
                 trust_threshold: float = 0.5):
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        self.verify_authenticity_accident = verify_authenticity_accident
        self.verify_authenticity_traffic_light = verify_authenticity_traffic_light
        self.trust_model = trust_model_name
        self.trust_model_description = trust_model_description
        self.use_relationship_context = use_relationship_context
        self.trust_computation_model = trust_computation_model
        self.trust_decision_making_model = trust_decision_making_model
        self.trust_update_strategy = trust_update_model
        self.transaction_exchange_scheme = transaction_exchange_scheme
        self.max_transaction_exchange_distance = max_transaction_exchange_distance
        self.adaptive_trust_model_selector = adaptive_trust_model_selector
        self.reputation_scope = reputation_scope
        self.reputation_context = reputation_context
        self.reputation_computation_strategy = reputation_computation_strategy
        self.trustworthy_threshold_for_trustee = trustworthy_threshold_for_trustee
        self.threshold_for_required_trustworthy_relationships = threshold_for_required_trustworthy_relationships
        self.trust_threshold = trust_threshold
