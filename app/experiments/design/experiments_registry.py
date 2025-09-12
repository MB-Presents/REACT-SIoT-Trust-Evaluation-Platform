# experiments/design/experiments_registry.py
from typing import List
from .models import ExperimentModelsDescription
from .settings import ExperimentSettings
from trust.trust_recommenders.trust_model import TrustComputationModel
from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod
from trust.trust_update.trust_update import TrustUpdateModel
from trust.transaction_exchange_scheme.trust_inference_engine import TransactionExchangeScheme

EXPERIMENTS: List[ExperimentSettings] = []

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




