from enum import Enum

from trust_management.trust_update.sum_based_update.sum_based_model import AverageSumModel
from trust_management.trust_update.trust_computation_value.trust_computation_value import TrustComputationValue
from trust_management.trust_update.context_based_update.abderahhim_update import TRUST_UPDATE_ABDERRAHIM_2017


class TrustUpdateModel(Enum):
    TRUST_COMPUTATION_VALUE = TrustComputationValue()
    AVERAGE_SUM_MODEL = AverageSumModel()
    TRUST_UPDATE_ABDERRAHIM_2017 = TRUST_UPDATE_ABDERRAHIM_2017()