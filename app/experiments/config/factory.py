from typing import List
from .builder import ExperimentConfigurationBuilder
from .models import (
    ExperimentConfiguration,
    TrustConfiguration,
    ReputationConfiguration,
    AuthenticationConfiguration
)

from trust.trust_recommenders.trust_model import TrustComputationModel
from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod
from trust.trust_update.trust_update import TrustUpdateModel
from trust.transaction_exchange_scheme.trust_inference_engine import TransactionExchangeScheme


class ExperimentConfigurationFactory:
    """Factory for creating common experiment configurations."""
    
    @staticmethod
    def create_mutual_context_aware_experiment() -> ExperimentConfiguration:
        """Create configuration for mutual context-aware trust model experiment."""
        trust_config = TrustConfiguration(
            computation_model=TrustComputationModel.MUTUAL_CONTEXT_AWARE_TRUSTWORTHY_SERVICE_EVALUATION,
            decision_making_model=TrustDecisionMethod.THRESHOLD_BASED_TRUST_DECISION_MAKING,
            update_model=TrustUpdateModel.TRUST_COMPUTATION_VALUE,
            transaction_exchange_scheme=TransactionExchangeScheme.NO_TRANSACTION_EXCHANGE,
            adaptive_trust_model_selector=None,
            max_transaction_exchange_distance=0,
            use_relationship_context=True
        )
        
        return (ExperimentConfigurationBuilder("EXP003", "EXP_ACCURACY_TRUST_CONVERGENCE_PERFORMANCE")
                .with_trust_model("mctse_evaluation_model", "MutualContextAwareTrustworthyServiceEvaluationModel")
                .with_trust_configuration(trust_config)
                .build())
    
    @staticmethod
    def create_cbstm_iot_experiment() -> ExperimentConfiguration:
        """Create configuration for CBSTM IoT experiment."""
        trust_config = TrustConfiguration(
            computation_model=TrustComputationModel.CONTEXT_BASED_TRUST_MODEL_FOR_IOT,
            decision_making_model=TrustDecisionMethod.THRESHOLD_BASED_TRUST_DECISION_MAKING,
            update_model=TrustUpdateModel.TRUST_COMPUTATION_VALUE,
            transaction_exchange_scheme=TransactionExchangeScheme.ONLY_DIRECT_TRANSACTION_EXCHANGE,
            max_transaction_exchange_distance=30,
            use_relationship_context=True
        )
        
        return (ExperimentConfigurationBuilder("EXP003", "EXP_ACCURACY_TRUST_CONVERGENCE_PERFORMANCE")
                .with_trust_model("cbstm_iot", "CBSTM-IoT: Context-based Social Trust Model for The IoT")
                .with_trust_configuration(trust_config)
                .build())
    
    @staticmethod
    def create_ctms_siot_experiment() -> ExperimentConfiguration:
        """Create configuration for CTMS SIoT experiment."""
        trust_config = TrustConfiguration(
            computation_model=TrustComputationModel.CONTEXT_BASED_TRUST_MANAGEMENT_SYSTEM_FOR_IOT,
            decision_making_model=TrustDecisionMethod.THRESHOLD_BASED_TRUST_DECISION_MAKING,
            update_model=TrustUpdateModel.TRUST_UPDATE_ABDERRAHIM_2017,
            transaction_exchange_scheme=TransactionExchangeScheme.ONLY_DIRECT_TRANSACTION_EXCHANGE,
            max_transaction_exchange_distance=30,
            use_relationship_context=False
        )
        
        auth_config = AuthenticationConfiguration(
            verify_accident_authenticity=True,
            verify_traffic_light_authenticity=True
        )
        
        return (ExperimentConfigurationBuilder("EXP003", "EXP_ACCURACY_TRUST_CONVERGENCE_PERFORMANCE")
                .with_trust_model("ctms_siot", "CTMSD")
                .with_trust_configuration(trust_config)
                .with_authentication_configuration(auth_config)
                .build())