



from enum import Enum
from trust.adaptive_trust_model_selector.context_based_trust_model_selector.adaptive_trust_model_selector import AdaptiveTrustModelSelector


class TrustModelSelector(Enum):
    
    CONTEXT_BASED_TRUST_MODEL_SELECTOR = AdaptiveTrustModelSelector()