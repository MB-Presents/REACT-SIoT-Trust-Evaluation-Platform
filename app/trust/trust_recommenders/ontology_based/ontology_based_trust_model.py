
from __future__ import annotations
import math
from typing import TYPE_CHECKING

from core.models.uniform.components.report_models import ReportType
from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import RequestLifecycleStatus
from trust.data_models.TrustVerifierRoles import TrustVerfierRoles

import numpy as np
from trust.situation_recognition_module.situation_recognition import SituationSettings
from trust.trust_recommenders.interface_trust_model import ITrustComputationModel

if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket
    from core.models.devices.genric_iot_device import GenericDevice


import sys
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

sys.path.insert(0, '/Users/marius/Documents/Simulation-Trust-Recommendation/react-siot-trust-evaluation-platform')

import trust.trust_recommenders.ontology_based.mappings as map
from trust.trust_recommenders.ontology_based.constants import FeatureSettings


class OntologyBasedTrustModel(ITrustComputationModel):


    
        
    def preprocess_trust_evaluation(self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> float:

        
        self.update_service_providers(sensory_parameters=sensory_parameters, request=request, situation_settings=situation_settings)
        
        request.service_providers = self.compute_indicators(request.service_providers, situation_settings)
        request.service_providers = self.apply_constaint_filters(request.service_providers, situation_settings)
    
    def check_compliance(   self, 
                            trustor : GenericDevice, 
                            request : SendingPacket = None,
                            sensory_parameters : dict = None,
                            situation_settings : SituationSettings = None) -> bool:
        
        situation_settings.trust_model_settings.TIME_SENSITIVITY_REACHED = False
        
        is_time_compliant = self.check_time_compliance(request, situation_settings)       
        is_distance_compliant =  self.is_distance_compliant(trustor, request)
        
        if request.request_type == ReportType.TraffiCPriorityRequest:
        
            if is_time_compliant:
                situation_settings.trust_model_settings.TIME_SENSITIVITY_REACHED = True
            
            if is_distance_compliant:
                situation_settings.trust_model_settings.TIME_SENSITIVITY_REACHED = True
                situation_settings.trust_model_settings.MIN_SERVICE_PROVIDER = 3
            
            
            smallest_distance = 200
            
            for reporter_id, reporter in request.sending_entities.items():
                location_reporter = np.array(reporter.device._position)
                location_trustor = np.array(trustor._position)
                
                distance = np.linalg.norm(location_reporter - location_trustor)
                
                
                smallest_distance = min(smallest_distance, distance)
            
            if smallest_distance < 10:
                request.event_status = RequestLifecycleStatus.FINISHED
                
            
            
            
            

    def is_distance_compliant(self, trustor, request):
        is_distance_compliant = True
        
        for reporter_id, reporter in request.sending_entities.items():
            location_reporter = np.array(reporter.device._position)
            location_trustor = np.array(trustor._position)
            
            distance = np.linalg.norm(location_reporter - location_trustor)
            
            if distance > 10 and distance <= 150:
                is_distance_compliant = False
                break
        
            
        return is_distance_compliant

    def check_time_compliance(self, request, situation_settings):
        time_compliance = True
        
        if request.remaining_decision_time <= 0:
            situation_settings.trust_model_settings.TIME_SENSITIVITY_REACHED = True
            situation_settings.trust_model_settings.MIN_SERVICE_PROVIDER = 3
            time_compliance = False
            
        return time_compliance
            




    def computate_trust_value(self, trustor : GenericDevice, 
                                    trustee : GenericDevice,
                                    sensory_parameters : dict = None,
                                    request : SendingPacket = None,
                                    situation_settings : SituationSettings = None) -> float:
        
        
        request.trust_score = self.compute_trust_score(request.service_providers, situation_settings, request)    
        
        return request.trust_score
    
    def postprocessing_trust_evaluation(self, 
                                        trustor : GenericDevice, 
                                        request : SendingPacket = None, 
                                        sensory_parameters : dict = None, 
                                        situation_settings : SituationSettings = None) -> float:
        
        
        
        trustor = request.receiving_entity
        trustees = request.service_providers  
        
        for trustee_id, trustee in trustees.items():
            trust_value = trustee['authenticity']
            self.produce_service_providers_trust_transactions(trustor=trustor, trust_value=trust_value, report=request, trustee=trustee['service_provider'])    
    



    def produce_service_providers_trust_transactions(self, trust_value: float, report : SendingPacket, trustor : GenericDevice, trustee : GenericDevice):
                
        selected_record = {}
        
        confidence_value = 0.0
        start_time = 0
        
        for (time, service_provider_id, sensed_device_id), record in report.service_providers.items():
            if service_provider_id == trustee._id:
                
                if time > start_time:
                    start_time = time
                    selected_record = record
                
                
                # if record['confidence'] > confidence_value:
                #     confidence_value = record['confidence']
                #     selected_record = record
                
        if len(selected_record) == 0:
            raise ValueError("No service provider found")
        
        trustor.trust_manager.add_trust_transaction(trustor=trustor, trustee=trustee, trust_value=trust_value, reporting_time=selected_record['time'], transaction_context=report, role=TrustVerfierRoles.SERVICE_PROVIDER)
        
    

    def update_service_providers(self, sensory_parameters : dict, request : SendingPacket, situation_settings  : SituationSettings):
        
        service_providers = self.reason_semantic_features(sensory_parameters, request, situation_settings)
        request.service_providers = self.compute_time_decay(request.service_providers, situation_settings)
        
        request.service_providers.update(service_providers)


    def compute_time_decay(self, service_providers: dict, situation_settings : SituationSettings) -> dict:
            
        feature_settings : FeatureSettings = situation_settings.feature_settings
        max_time_threshold = feature_settings.MAX_TIME_THRESHOLD
        decay_rate = feature_settings.DECAY_FACTOR
        
        for service_provider_id, service_provider in service_providers.items():
            
            if 'time' not in service_provider.keys():
                raise ValueError("Time is not set")
        
        
            time_since_update =  ScenarioParameters.TIME - service_provider['time']
            time_since_update = min(time_since_update, max_time_threshold)
            
            if time_since_update > 0:
                pass
            
            decay_factor = math.exp(-decay_rate * time_since_update)
            
            service_provider['confidence'] = service_provider['confidence'] * decay_factor
            
            service_providers[service_provider_id] = service_provider
            
            
        return service_providers


        
    def reason_semantic_features(self,service_providers: dict,  report : SendingPacket, situation_settings : SituationSettings) -> dict:
        
        service_provider_result = {}
        
        for service_provider_id, service_provider in service_providers.items():
            
        
            if service_provider['sensed_device_id'] == service_provider['service_provider_id']:
                continue
            
            
            if 'fits_speed' in service_provider.keys(): # already computed
                continue
            
            
            
            
            service_provider_record = {}
            
            mapping_settings = situation_settings.mapping_settings
        
            # Numerical features to categorical features
            service_provider_record['service_provider_id'] = service_provider['service_provider_id']
            service_provider_record['sensed_device_id'] = service_provider['sensed_device_id']
            service_provider_record['time'] = service_provider['time']
            service_provider_record['sensed_device_type'] = service_provider['sensed_device_type']
            
            
            # Map into semantic feature space
            service_provider_record['fits_speed'] = map.speed(service_provider['sensed_device_speed'],mapping_settings)
            service_provider_record['fits_dimension'] = map.vehicle_dimensions(service_provider['sensed_device_length'], service_provider['sensed_device_width'],service_provider['sensed_device_height'],mapping_settings)
            
            service_provider_record['vehicle_shape'] = map.object_functional_status(service_provider['sensed_device_functional_status'], mapping_settings)
            service_provider_record['type'] = map.vehicle_type(service_provider['sensed_vehicle_type'],mapping_settings)
            service_provider_record['has_signal'] = map.signals(service_provider['sensed_device_signal'], mapping_settings)
            service_provider_record['closeness_object_of_interest_to_sensed_object'] = map.classify_distance_interested_object(service_provider['sensed_device_position'], report.object_of_interest.location, mapping_settings)
            service_provider_record['speed_category_service_provider'] = map.speed(service_provider['service_provider_speed'], mapping_settings)
            service_provider_record['distance_service_provider_to_sensed_object'] = map.classify_distance(
                service_provider['service_provider_location'], service_provider['sensed_device_position'], mapping_settings)
            
            
            
            # Application criteria
            feature_settings = situation_settings.feature_settings

            service_provider_record['fits_speed'] = service_provider_record['fits_speed'] in feature_settings.SPEED_CRITERIA
            service_provider_record['type'] = service_provider_record['type'] in feature_settings.TYPE_CRITERIA
            service_provider_record['vehicle_shape'] = service_provider_record['vehicle_shape'] in feature_settings.VEHICLE_SHAPE_CRITERIA
            
            
            service_provider_record['has_signal'] = map.has_signal(service_provider_record['has_signal'], feature_settings.SIGNAL_CRITERIA)
            service_provider_record['fits_dimension'] = map.has_dimension(service_provider_record['fits_dimension'], feature_settings.DIMENSION_CRITERIA)
            service_provider_record['does_interested_object_correlates_with_sensed_object'] = map.distance_value_interested_object(
                service_provider_record['closeness_object_of_interest_to_sensed_object'], feature_settings)
            
            service_provider_record['service_provider_speed_value'] = map.speed_numerical(service_provider_record['speed_category_service_provider'], feature_settings)
            service_provider_record['distance_service_provider_to_sensed_object_value'] = map.distance_value_sensed_object(service_provider_record['distance_service_provider_to_sensed_object'], feature_settings)
            
            
            service_provider_record['service_provider'] = service_provider['service_provider']
            service_provider_result[service_provider_id] = service_provider_record
            
            
            
        return service_provider_result


    def compute_indicators(self, service_providers_result: dict, situation_settings: SituationSettings) -> dict:
        
        weights = situation_settings.weights
        
        for service_provider_id, service_provider in service_providers_result.items():
            
            # if 'ti_identification' in service_provider.keys():
            #     continue
            
            identification_score = 0.0
            identification_score += weights.SIGNAL * int(service_provider['has_signal'])

            identification_score += weights.SPEED * int(service_provider['fits_speed'])
            identification_score += weights.DIMENSION * int(service_provider['fits_dimension'])

            identification_score += weights.TYPE * int(service_provider['type'])
            identification_score += weights.VEHICLE_SHAPE * int(service_provider['vehicle_shape'])

            identification_score += weights.LOCATION_ID * int(service_provider['does_interested_object_correlates_with_sensed_object'])
            identification_score = identification_score * (1 / (weights.SIGNAL + weights.SPEED + weights.DIMENSION + weights.TYPE + weights.VEHICLE_SHAPE + weights.LOCATION_ID))  # normalize
            
            service_provider['ti_identification'] = identification_score
            

            service_provider['confidence'] =   (1 / (weights.SPEED_LOCATION + weights.LOCATION_CLOSENESS + weights.POSITION)) * \
                weights.SPEED_LOCATION * service_provider['service_provider_speed_value'] + \
                weights.POSITION * service_provider['distance_service_provider_to_sensed_object_value'] + \
                weights.LOCATION_CLOSENESS * service_provider['does_interested_object_correlates_with_sensed_object'] 
                
        

            
        
        

        return service_providers_result


    def compute_trust_score(self, service_providers_result, situation_settings : SituationSettings, request : SendingPacket) -> float:
        
        trust_model_settings = situation_settings.trust_model_settings

        if len(service_providers_result) < trust_model_settings.MIN_SERVICE_PROVIDER and not trust_model_settings.TIME_SENSITIVITY_REACHED:
            return np.nan
        
        if len(service_providers_result) == 0:
            return np.nan
        
        authenticity_score = 0.0
        
        for service_provider_id, service_provider in service_providers_result.items():
            service_provider['authenticity'] = service_provider['ti_identification'] * service_provider['confidence']
            authenticity_score += service_provider['authenticity']
        
        authenticity_score = authenticity_score / len(service_providers_result)
            
        return authenticity_score


    def apply_constaint_filters(self, service_providers_result, situation_settings : SituationSettings):
        
        service_providers_result = self.apply_trust_model_constraints(service_providers_result, situation_settings)
        result_set_after_confidence_grouping = self.group_by_confidence_of_sensed_device(service_providers_result)        
        final_result_set = self.group_by_identification_indicator(result_set_after_confidence_grouping)
        service_providers_result  = final_result_set
        
        return service_providers_result



    def group_by_identification_indicator(self, result_set_after_confidence_grouping):
        
        result_set_after_grouping = {}

        for service_provider_id, service_provider in result_set_after_confidence_grouping.items():
            service_provider_records = self.get_records_with_same_service_provider_id(service_provider['service_provider_id'], result_set_after_confidence_grouping)
            service_provider_with_highest_key = max(service_provider_records, key=lambda k: service_provider_records[k]['ti_identification'])
            result_set_after_grouping[service_provider_with_highest_key] = service_provider_records[service_provider_with_highest_key]    
        return result_set_after_grouping
        
    def is_object_in_dict(self, service_provider, filtered_service_provider):
        
        for key, value in filtered_service_provider.items():    
            if service_provider['service_provider_id'] == value['service_provider_id'] and service_provider['sensed_device_id'] == value['sensed_device_id'] and service_provider['confidence'] <= value['confidence']:
                return True        
        return False    

    def group_by_confidence_of_sensed_device(self,service_providers : dict):
        
        service_providers_list = list(service_providers.values())
        sorted_service_providers = sorted(service_providers_list, key=lambda k: (k['service_provider_id'], k['sensed_device_id'], k['confidence']), reverse=True)
        service_providers_by_confidence = {}

        for service_provider in sorted_service_providers:
            if not self.is_object_in_dict(service_provider, service_providers_by_confidence):
                key = (service_provider['time'],service_provider['service_provider_id'],service_provider['sensed_device_id'])
                service_providers_by_confidence[key] = service_provider
            
        return service_providers_by_confidence
        
        

    def apply_trust_model_constraints(self,service_providers_result, situation_settings : SituationSettings):
        result_set = {}
        feature_settings : FeatureSettings = situation_settings.feature_settings
        trust_model_settings = situation_settings.trust_model_settings
        
        for service_provider_id, service_provider in service_providers_result.items():
            closeness = service_provider['closeness_object_of_interest_to_sensed_object']
            confidence = service_provider['confidence']

            if closeness not in feature_settings.REQUIRED_CLOSENESS_DISTANCE_SENSED_DEVICE_INTERESTED_OBJECT:
                continue  # Skip this service_provider, do not add it to the result_set

            if confidence < trust_model_settings.CONFIDENCE_THRESHOLD:
                continue  

            result_set[service_provider_id] = service_provider
        
        return result_set



    def get_records_with_same_service_provider_id(self,service_provider_key: str, service_providers_result: dict) -> dict:
        service_provider_records = {}
        for service_provider_id, service_provider in service_providers_result.items():
            if service_provider_key == service_provider['service_provider_id']:
                service_provider_records[service_provider_id] = service_provider
        return service_provider_records

