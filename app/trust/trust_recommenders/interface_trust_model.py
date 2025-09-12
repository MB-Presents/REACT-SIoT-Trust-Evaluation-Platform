from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket
    from core.models.devices.genric_iot_device import GenericDevice
    from trust.situation_recognition_module.situation_recognition import SituationSettings




class ITrustComputationModel(ABC):
    

    @abstractmethod
    def check_compliance(   self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> bool:
        pass

    
    @abstractmethod
    def preprocess_trust_evaluation(self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> float:
        pass
    
    
    @abstractmethod
    def computate_trust_value(self, trustor : GenericDevice, 
                                    trustee : GenericDevice,
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None,
                                    situation_settings : SituationSettings = None) -> float:
        pass
    
    
    @abstractmethod
    def postprocessing_trust_evaluation(self, 
                                    trustor : GenericDevice, 
                                    request : SendingPacket = None,
                                    sensory_parameters : dict = None, 
                                    situation_settings : SituationSettings = None) -> float:
        pass
    


    
