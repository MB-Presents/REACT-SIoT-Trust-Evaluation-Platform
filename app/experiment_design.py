# Experiment Settings


from enum import Enum
from typing import List
from trust_management.adaptive_trust_model_selector.TrustModelSelector import TrustModelSelector
from trust_management.decision_making_module.trust_decision_maker import TrustDecisionMethod

from trust_management.transaction_exchange_scheme.trust_inference_engine import TransactionExchangeScheme
from trust_management.trust_recommenders.trust_model import TrustComputationModel
from trust_management.data_models.reputation.reputation import ReputationComputationStrategy, ReputationContextSettings, ReputationScope
from trust_management.trust_update.trust_update import TrustUpdateModel


class ExperimentModelsDescription(Enum):
    MUTUAL_CONTEXT_AWARE_TRUSTWORTHY_SERVICE_EVALUATION = 'MutualContextAwareTrustworthyServiceEvaluationModel'
    CONTEXT_BASED_TRUST_MODEL_FOR_IOT = 'ContextBasedTrustModelIoT'
    CBSTM_IOT = 'CBSTM-IoT: Context-based Social Trust Model for The IoT'
    ONTOLOGY_BASED_TRUST_MODEL = 'OntologyBasedTrustModel'
    MAG_SIOT = 'MAGSIoT'
    CTMS = 'CTMSD'
    MFM_HTM_SIOT = 'MFMHTMSIoT'
    MPTM_SIOT = 'MPTMSIoT'
    ADAPTIVE_TRUST_MODEL_SELECTOR = 'AdaptiveTrustModelSelector' 
    TEMPORAL_GRAPH_BASED_TRUST_MODEL = 'TemporalGraphBasedTrustModel'

class ExperimentSettings:
    
    def __init__(   self, 
                    experiment_id : str, 
                    experiment_name : str,
                    verify_authenticity_accident : bool,
                    verify_authenticity_traffic_light : bool,
                    trust_model_name : str,
                    trust_model_description : str,
                    use_relationship_context : bool,
                    trust_computation_model : TrustComputationModel,
                    trust_decision_making_model : TrustDecisionMethod,
                    trust_update_model : TrustUpdateModel,
                    transaction_exchange_scheme : TransactionExchangeScheme,
                    max_transaction_exchange_distance : int,
                    apdative_trust_model_selector : TrustModelSelector = None,
                    reputation_scope : ReputationScope = ReputationScope.LOCAL,
                    reputation_context : ReputationContextSettings = ReputationContextSettings.NO_CONTEXT,
                    reputation_computation_strategy : ReputationComputationStrategy = ReputationComputationStrategy.AVERAEG_OF_LAST_N_TRANSACTIONS,
                    trustworthy_threshold_for_trustee : float = 0.7,
                    threshold_for_required_trustworthy_relationships : int = 2,
                    trust_threshold : float = 0.5
                 ):
        
        
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        self.verify_authenticity_accident = verify_authenticity_accident
        self.verify_authenticity_traffic_light = verify_authenticity_traffic_light
        self.trust_model = trust_model_name
        self.use_relationship_context = use_relationship_context
        self.trust_computation_model = trust_computation_model
        self.trust_decision_making_model = trust_decision_making_model

        self.trust_update_strategy = trust_update_model
        self.transaction_exchange_scheme = transaction_exchange_scheme
        self.max_transaction_exchange_distance = max_transaction_exchange_distance
        self.trust_model_description = trust_model_description

        
        self.adaptive_trust_model_selector = apdative_trust_model_selector

        self.reputation_scope = reputation_scope
        self.reputation_context = reputation_context
        self.reputation_computation_strategy = reputation_computation_strategy
        self.trustworthy_threshold_for_trustee = trustworthy_threshold_for_trustee
        self.threshold_for_required_trustworthy_relationships = threshold_for_required_trustworthy_relationships


        self.trust_threshold = trust_threshold


EXPERIMENTS : List[ExperimentSettings] = []



experiment_settings_mutual_context_aware_trust_model = ExperimentSettings(experiment_id="EXP003",
                                            experiment_name="EXP_ACCURACY_TRUST_CONVERGENCE_PERFORMANCE", 
                                            verify_authenticity_accident=True,
                                            verify_authenticity_traffic_light=True,
                                            trust_model_name="mctse_evaluation_model",
                                            trust_model_description=ExperimentModelsDescription.MUTUAL_CONTEXT_AWARE_TRUSTWORTHY_SERVICE_EVALUATION.value,
                                            use_relationship_context=True,
                                            trust_computation_model=TrustComputationModel.MUTUAL_CONTEXT_AWARE_TRUSTWORTHY_SERVICE_EVALUATION.value,
                                            trust_decision_making_model=TrustDecisionMethod.THRESHOLD_BASED_TRUST_DECISION_MAKING.value,
                                            trust_update_model=TrustUpdateModel.TRUST_COMPUTATION_VALUE.value,
                                            transaction_exchange_scheme=TransactionExchangeScheme.NO_TRANSACTION_EXCHANGE.value,
                                            max_transaction_exchange_distance=0)

experiment_settings_rafey__2016_cbstm_iot = ExperimentSettings(experiment_id="EXP003",
                                            experiment_name="EXP_ACCURACY_TRUST_CONVERGENCE_PERFORMANCE", 
                                            verify_authenticity_accident=True,
                                            verify_authenticity_traffic_light=True,
                                            trust_model_name="cbstm_iot",
                                            trust_model_description=ExperimentModelsDescription.CBSTM_IOT.value,
                                            use_relationship_context=True,
                                            trust_computation_model=TrustComputationModel.CONTEXT_BASED_TRUST_MODEL_FOR_IOT.value,
                                            trust_decision_making_model=TrustDecisionMethod.THRESHOLD_BASED_TRUST_DECISION_MAKING.value,
                                            trust_update_model=TrustUpdateModel.TRUST_COMPUTATION_VALUE.value,
                                            transaction_exchange_scheme=TransactionExchangeScheme.ONLY_DIRECT_TRANSACTION_EXCHANGE.value,
                                            max_transaction_exchange_distance=30)

experiment_settings_abderrahim_2018_ctms_siot = ExperimentSettings(experiment_id="EXP003",
                                            experiment_name="EXP_ACCURACY_TRUST_CONVERGENCE_PERFORMANCE", 
                                            verify_authenticity_accident=True,
                                            verify_authenticity_traffic_light=True,
                                            trust_model_name="ctms_siot",
                                            trust_model_description=ExperimentModelsDescription.CTMS.value,
                                            use_relationship_context=False,
                                            trust_computation_model=TrustComputationModel.CONTEXT_BASED_TRUST_MANAGEMENT_SYSTEM_FOR_IOT.value,
                                            trust_decision_making_model=TrustDecisionMethod.THRESHOLD_BASED_TRUST_DECISION_MAKING.value,
                                            trust_update_model=TrustUpdateModel.TRUST_UPDATE_ABDERRAHIM_2017.value,
                                            transaction_exchange_scheme=TransactionExchangeScheme.ONLY_DIRECT_TRANSACTION_EXCHANGE.value,
                                            max_transaction_exchange_distance=30)


# My models
# EXPERIMENTS.append(experiment_settings_ontology)
# EXPERIMENTS.append(experiment_settings_temporal_graph_based_model)
# EXPERIMENTS.append(experiment_settings_context_aware_trust_model)

EXPERIMENTS.append(experiment_settings_mutual_context_aware_trust_model)
EXPERIMENTS.append(experiment_settings_rafey__2016_cbstm_iot)
EXPERIMENTS.append(experiment_settings_abderrahim_2018_ctms_siot)



# Trust Inference Models





