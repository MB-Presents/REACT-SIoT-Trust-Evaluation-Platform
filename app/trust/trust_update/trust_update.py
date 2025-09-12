from enum import Enum

from trust.trust_update.context_based_model.trust_inference_based_model import TrustInferenceModel
from trust.trust_update.sum_based_update.sum_based_model import AverageSumModel
from trust.trust_update.trust_computation_value.trust_computation_value import TrustComputationValue
from trust.trust_update.context_based_update.abderahhim_update import TRUST_UPDATE_ABDERRAHIM_2017


class TrustUpdateModel(Enum):
    TRUST_COMPUTATION_VALUE = TrustComputationValue()
    AVERAGE_SUM_MODEL = AverageSumModel()
    CONTEXT_BASED_RELEATIONSHIP_MODEL = TrustInferenceModel()
    TRUST_UPDATE_ABDERRAHIM_2017 = TRUST_UPDATE_ABDERRAHIM_2017()