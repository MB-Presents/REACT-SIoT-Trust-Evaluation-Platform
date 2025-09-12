


from __future__ import annotations

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Union
from abc import ABC, abstractmethod


if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.uniform.components.report import SendingPacket
    from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod

    from trust.settings import TrustModelScheme
    from trust.situation_recognition_module.situation_recognition import SituationSettings
    from trust.trust_recommenders.context_based_trust_models.mutual_context_aware_trustworthy_service_evaluation import MutualContextAwareTrustworthyServiceEvaluationModel
    from trust.trust_recommenders.trust_model import TrustComputationModel
    from trust.trust_update.trust_update import TrustUpdateModel


class ITrustModelSelectionModel(ABC):
    
    @abstractmethod
    def select_trust_computation_model(self, trustor : GenericDevice, report : SendingPacket, sensory_parameters : dict = None, situation_settings : SituationSettings = None):
        pass
    
    @abstractmethod
    def select_trust_decision_making_model(self, trustor : GenericDevice, report : SendingPacket, sensory_parameters : dict = None, situation_settings : SituationSettings = None):
        pass
    
    @abstractmethod
    def select_trust_update_model(self, trustor : GenericDevice, report : SendingPacket, sensory_parameters : dict = None, situation_settings : SituationSettings = None):
        pass

    
    @abstractmethod
    def get_trust_computation_model(self) -> TrustComputationModel:
        pass

    
    @abstractmethod
    def get_trust_decision_making_model(self) -> TrustDecisionMethod:
        pass
    
    @abstractmethod
    def get_trust_update_model(self) -> TrustUpdateModel:
        pass