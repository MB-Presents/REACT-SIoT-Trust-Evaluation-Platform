
from __future__ import annotations
from typing import TYPE_CHECKING
from data_models.report_management.report.report_models import Situation

if TYPE_CHECKING:
    from data_models.report_management.report.report import SendingPacket








from trust_management.trust_recommenders.ontology_based.constants import EmergencyCallFeatureSettings, EmergencyCallMappingSettings, EmergencyCallWeightSettings, FeatureSettings, MappingSettings, TrafficLightFeatureSettings, TrafficLightMappingSettings, TrafficLightWeightSettings, TrustModelSettings, TrustModelSettingsEmergencyCall, TrustModelSettingsTrafficLight, Weight

class SituationSettings:
    mapping_settings : MappingSettings = None
    weights : Weight = None
    feature_settings : FeatureSettings = None
    trust_model_settings : TrustModelSettings = None

    def __init__(self, mapping_settings : MappingSettings, weights : Weight, feature_settings : FeatureSettings, trust_model_settings : TrustModelSettings):
        self.mapping_settings = mapping_settings
        self.weights = weights
        self.feature_settings = feature_settings
        self.trust_model_settings = trust_model_settings



def get_situation_settings(report : SendingPacket):
    situation_settings : SituationSettings = None

    if report.situation == Situation.TRAFFIC_PRIORITY_REQUEST:
        situation_settings = SituationSettings(mapping_settings=TrafficLightMappingSettings, weights=TrafficLightWeightSettings, feature_settings=TrafficLightFeatureSettings, trust_model_settings=TrustModelSettingsTrafficLight)
        
    elif report.situation == Situation.EMERGENCY_REPORT:
        situation_settings = SituationSettings(mapping_settings=EmergencyCallMappingSettings, weights=EmergencyCallWeightSettings, feature_settings=EmergencyCallFeatureSettings, trust_model_settings=TrustModelSettingsEmergencyCall)

    else:
        raise Exception('Situation not supported')
    return situation_settings