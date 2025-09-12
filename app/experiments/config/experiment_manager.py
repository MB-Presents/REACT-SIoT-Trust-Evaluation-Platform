from typing import Dict, Any, Union
from pathlib import Path

from experiments.settings import Settings
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings
from scenarios.canberra_case_study.apps.intelligent_traffic_light.constants import TrafficLightApplicationSettings
from trust.settings import TrustManagementSettings
from .models import ExperimentConfiguration


class ExperimentSettingsManager:
    """Manages experiment settings and their persistence."""
    
    def __init__(self, config: ExperimentConfiguration):
        self.config = config
    
    def apply_to_global_settings(self, settings_modules: Dict[str, Union[Settings, TrustManagementSettings, AccidentSettings, TrafficLightApplicationSettings]]) -> None:
        """Apply experiment configuration to global settings modules.
        
        Args:
            settings_modules: Dictionary mapping module names to their objects
        """
        # Apply simulation settings
        sim_settings = settings_modules.get('Settings')
        if sim_settings:
            self._apply_simulation_settings(sim_settings)
        
        # Apply trust management settings
        trust_settings = settings_modules.get('TrustManagementSettings')
        if trust_settings:
            self._apply_trust_settings(trust_settings)
        
        # Apply accident settings
        accident_settings = settings_modules.get('AccidentSettings')
        if accident_settings:
            self._apply_accident_settings(accident_settings)
        
        # Apply traffic light settings
        traffic_settings = settings_modules.get('TrafficLightApplicationSettings')
        if traffic_settings:
            self._apply_traffic_light_settings(traffic_settings)
    
    def _apply_simulation_settings(self, settings: Any) -> None:
        """Apply simulation configuration to settings object."""
        settings.EXPERIMENT_ID = self.config.experiment_id
        settings.EXPERIMENT_NAME = self.config.experiment_name
        settings.TRUST_MODEL_DESCRIPTION = self.config.trust_model_description
        settings.SELECTED_TRUST_MODEL = self.config.trust_model_name
        
        sim_config = self.config.simulation_config
        settings.MAX_NUMBER_SIMULATION_RUNS = sim_config.max_simulation_runs
        settings.MAX_NUMBER_TRAFFIC_ACCIDENTS = sim_config.max_traffic_accidents
        settings.MAX_SIMULATION_DURATION = sim_config.max_simulation_duration
        settings.INTERVAL_OF_ACCIDENTS = sim_config.accident_interval
        settings.INTERVAL_OF_FALSE_ACCIDENTS = sim_config.false_accident_interval
        settings.INTERVAL_OF_FALSE_TRAFFIC_LIGHT_REQUESTS = sim_config.false_traffic_light_requests_interval
        settings.PERCENTAGE_OF_MALICIOUS_VEHICLES = sim_config.malicious_vehicle_percentage
        
        auth_config = self.config.authentication_config
        settings.VERIFY_ACCIDENT_REPORT_AUTHENTICITY = auth_config.verify_accident_authenticity
        settings.VERIFY_TRAFFIC_LIGHT_REQUEST_AUTHENTICITY = auth_config.verify_traffic_light_authenticity
    
    def _apply_trust_settings(self, settings: Any) -> None:
        """Apply trust configuration to settings object."""
        trust_config = self.config.trust_config
        settings.USE_RELATIONSHIP_CONTEXT = trust_config.use_relationship_context
        settings.TRUST_COMPUTATION_MODEL = trust_config.computation_model
        settings.TRUST_DECISION_MAKING_MODEL = trust_config.decision_making_model
        settings.TRUST_UPDATE_MODEL = trust_config.update_model
        settings.TRANSACTION_EXCHANGE_SCHEME = trust_config.transaction_exchange_scheme
        settings.MAX_TRANSACTION_EXCHANGE_DISTANCE = trust_config.max_transaction_exchange_distance
        settings.TRUST_TRANSACTION_THRESHOLD = trust_config.trust_threshold
        settings.TRUSTWORTHY_THRESHOLD_OF_RELATIONSHIPS = trust_config.trustworthy_threshold_for_trustee
        settings.THRESHOLD_FOR_NUM_OF_TRUSTWORTHY_RELATIONSHIPS = trust_config.threshold_for_required_trustworthy_relationships
        
        rep_config = self.config.reputation_config
        settings.REPUTATION_SCOPE = rep_config.scope
        settings.REPUTATION_CONTEXT = rep_config.context
        settings.REPUTATION_COMPUTATION_STRATEGY = rep_config.computation_strategy
        
        if self.config.adaptive_trust_model_selector:
            settings.USES_ADAPTIVE_TRUST_MODEL_SELECTION = True
            settings.ADAPTIVE_TRUST_MODEL_SELECTOR = self.config.adaptive_trust_model_selector
    
    def _apply_accident_settings(self, settings: Any) -> None:
        """Apply accident configuration to settings object."""
        accident_config = self.config.accident_config
        settings.SERVICE_REQUESTOR_DISTANCE = accident_config.service_requestor_distance
        settings.INITIAL_EMEREGENCY_PARKING_TIME = accident_config.initial_emergency_parking_time
        settings.PARKING_TIME_HOSPITAL = accident_config.parking_time_hospital
        settings.PARKING_TIME_ACCIDENT = accident_config.parking_time_accident
        settings.REPORTER_RADIUS = accident_config.reporter_radius
        settings.MAX_NUMBER_OF_ACCIDENTS = accident_config.max_accidents
        settings.ALLOWED_ACCIDENT_SPEED = accident_config.allowed_accident_speed
    
    def _apply_traffic_light_settings(self, settings: Any) -> None:
        """Apply traffic light configuration to settings object."""
        traffic_config = self.config.traffic_light_config
        settings.SERVICE_REQUESTOR_DISTANCE = traffic_config.service_requestor_distance
        settings.VEHICLE_DISTANCE_SENSING = traffic_config.vehicle_distance_sensing
        settings.SMART_PHONE_DISTANCE_SENSING = traffic_config.smart_phone_distance_sensing
    
    def collect_settings_report(self, settings_modules: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Collect all settings into a report format."""
        report = {}
        
        for module_name, settings_obj in settings_modules.items():
            if hasattr(settings_obj, '__dict__'):
                # Filter out internal Python attributes
                settings_dict = {
                    k: v for k, v in vars(settings_obj).items() 
                    if not k.startswith('__')
                }
                report[module_name] = settings_dict
        
        return report
    
    def write_settings_report(self, settings_report: Dict[str, Dict[str, Any]], filepath: Path) -> None:
        """Write settings report to file."""
        with open(filepath, 'w') as file:
            file.write("=" * 60 + "\n")
            file.write(" SIoT Experiment Configuration Report\n")
            file.write("=" * 60 + "\n\n")
            
            # Write experiment metadata first
            file.write(f"Experiment ID: {self.config.experiment_id}\n")
            file.write(f"Experiment Name: {self.config.experiment_name}\n")
            file.write(f"Trust Model: {self.config.trust_model_name}\n")
            file.write(f"Model Description: {self.config.trust_model_description}\n\n")
            
            for category, settings_dict in settings_report.items():
                file.write(f"--- {category} ---\n")
                for key, value in sorted(settings_dict.items()):
                    if isinstance(value, (list, dict)):
                        formatted_value = '\n    '.join(str(value).split(','))
                    else:
                        formatted_value = value
                    file.write(f"{key}: {formatted_value}\n")
                file.write("\n")