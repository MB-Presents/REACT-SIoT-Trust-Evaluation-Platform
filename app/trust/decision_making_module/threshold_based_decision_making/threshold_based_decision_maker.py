from __future__ import annotations
import math
from typing import TYPE_CHECKING

import numpy as np

from core.models.events.simulation_events import VerificationState


from trust.decision_making_module.trust_decision_making_interface import ITrustDecisionMaking
from trust.settings import TrustManagementSettings




if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket

    from core.models.devices.genric_iot_device import GenericDevice
    from trust.situation_recognition_module.situation_recognition import SituationSettings













class ThresholdBasedDecisionMaker(ITrustDecisionMaking):
    
    def __init__(self, threshold : float = 0.5 ):
        
        self.threshold = TrustManagementSettings.TRUST_TRANSACTION_THRESHOLD
        
    def make_trust_decision(self, 
                            trustor : GenericDevice, 
                            trustee : GenericDevice,
                            trust_value : float,
                            request : SendingPacket = None,
                            situation_settings : SituationSettings = None) -> VerificationState:
            
        if (trust_value == None or trust_value == np.nan or trust_value == float("nan") or trust_value is None or math.isnan(trust_value)) and not situation_settings.trust_model_settings.TIME_SENSITIVITY_REACHED:
            return VerificationState.UNVERIFIED
        
        elif trust_value > self.threshold:
            return VerificationState.AUTHENTIC

        elif trust_value <= self.threshold:
            return VerificationState.NOT_AUTHENTIC

        # INFO: Currently trust recommendation will be conducted only once

        
        elif situation_settings.trust_model_settings.TIME_SENSITIVITY_REACHED:
            return VerificationState.NOT_VERIFIEDABLE
        
        else:
            raise Exception("Trust Decision could not be made")
        
        