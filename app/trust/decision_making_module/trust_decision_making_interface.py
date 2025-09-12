from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod

from core.models.events.simulation_events import VerificationState





if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket

    from core.models.devices.genric_iot_device import GenericDevice
    from trust.situation_recognition_module.situation_recognition import SituationSettings




class ITrustDecisionMaking(ABC):
    @abstractmethod
    def make_trust_decision(self, trustor : GenericDevice, 
                            trustee : GenericDevice,
                            trust_value : float,
                            request : SendingPacket = None,
                            situation_settings : SituationSettings = None) -> VerificationState:
        pass

