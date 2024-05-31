
import yaml
from experiment_design import ExperimentSettings
from experiments.settings import Settings
from scenario.emergency_response.constants import AccidentSettings
from scenario.intelligent_traffic_light.constants import TrafficLightApplicationSettings
import simulation_config
from trust_management.settings import TrustManagementSettings, TrustModelScheme
from simulation_config import SimulationConfiguration
from simulation_config import AccidentConfiguration
from simulation_config import TrafficLightApplicationConfiguration

def configure_experiment_settings(EXPERIMENT_SETTINGS : ExperimentSettings):
    
    Settings.MAX_NUMBER_TRAFFIC_ACCIDENTS = SimulationConfiguration.MAX_NUMBER_OF_TRAFFIC_ACCIDENTS
    Settings.MAX_NUMBER_SIMULATION_RUNS = SimulationConfiguration.MAX_NUMBER_OF_SIMULATION_RUNS
    Settings.INTERVAL_OF_ACCIDENTS = SimulationConfiguration.INTERVAL_OF_ACCIDENTS
    Settings.INTERVAL_OF_FALSE_ACCIDENTS = SimulationConfiguration.INTERVAL_OF_FALSE_ACCIDENTS
    
    Settings.INTERVAL_OF_FALSE_TRAFFIC_LIGHT_REQUESTS = SimulationConfiguration.INTERVAL_OF_FALSE_TRAFFIC_LIGHT_REQUESTS
    
    Settings.SIMULATION_RUN_INDEX = SimulationConfiguration.SIMULATION_RUN_INDEX
    
    Settings.MAX_SIMULATION_DURATION = SimulationConfiguration.MAX_SIMULATION_DURATION
    Settings.PERCENTAGE_OF_MALICIOUS_VEHICLES = SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES
    
    Settings.INTERVAL_OF_ACCIDENTS = SimulationConfiguration.INTERVAL_OF_ACCIDENTS
    Settings.INTERVAL_OF_FALSE_ACCIDENTS = SimulationConfiguration.INTERVAL_OF_FALSE_ACCIDENTS

    AccidentSettings.INITIAL_EMEREGENCY_PARKING_TIME = AccidentConfiguration.INITIAL_EMEREGENCY_PARKING_TIME
    AccidentSettings.PARKING_TIME_HOSPITAL = AccidentConfiguration.PARKING_TIME_HOSPITAL
    AccidentSettings.PARKING_TIME_ACCIDENT = AccidentConfiguration.PARKING_TIME_ACCIDENT
    AccidentSettings.EMERGENCY_TYPE_ID = AccidentConfiguration.EMERGENCY_TYPE_ID
    AccidentSettings.ALLOWED_ROAD_VEHICLES = AccidentConfiguration.ALLOWED_ROAD_VEHICLES
    AccidentSettings.ALLOWED_VEHICLE_COLLISION_TYPES = AccidentConfiguration.ALLOWED_VEHICLE_COLLISION_TYPES
    AccidentSettings.ALLOWED_VEHICLE_FAKE_COLLISION_TYPES = AccidentConfiguration.ALLOWED_VEHICLE_FAKE_COLLISION_TYPES
    AccidentSettings.ALLOWED_VEHICLE_REPORTER_TYPES = AccidentConfiguration.ALLOWED_VEHICLE_REPORTER_TYPES
    AccidentSettings.MAX_NUMBER_OF_ACCIDENTS = AccidentConfiguration.MAX_NUMBER_OF_ACCIDENTS
    AccidentSettings.ALLOWED_EMERGENCY_VEHICLES = AccidentConfiguration.ALLOWED_EMERGENCY_VEHICLES
    AccidentSettings.ALLOWED_ACCIDENT_SPEED = AccidentConfiguration.ALLOWED_ACCIDENT_SPEED
    AccidentSettings.REPORTER_RADIUS = AccidentConfiguration.REPORTER_RADIUS
    # AccidentSettings.EMERGENCY_VEH_IDS = EMERGENCY_VEH_IDS
    # AccidentSettings.EMERGENCY_DROP_OFF_LANE_POSITION = EMERGENCY_DROP_OFF_LANE_POSITION
    AccidentSettings.EMERGENCY_VEHS = AccidentConfiguration.EMERGENCY_VEHS
    
    AccidentSettings.SERVICE_REQUESTOR_DISTANCE = AccidentConfiguration.ACCIDENT_SERVICE_REQUESTOR_DISTANCE


    TrafficLightApplicationSettings.SERVICE_REQUESTOR_DISTANCE = TrafficLightApplicationConfiguration.TRAFFIC_LIGHT_SERVICE_REQUESTOR_DISTANCE
    TrafficLightApplicationSettings.VEHICLE_DISTANCE_SENSING = TrafficLightApplicationConfiguration.TRAFFIC_LIGHT_VEHICLE_DISTANCE_SENSING
    TrafficLightApplicationSettings.SMART_PHONE_DISTANCE_SENSING = TrafficLightApplicationConfiguration.TRAFFIC_LIGHT_SMART_PHONE_DISTANCE_SENSING

    
    Settings.EXPERIMENT_ID = EXPERIMENT_SETTINGS.experiment_id
    Settings.EXPERIMENT_NAME = EXPERIMENT_SETTINGS.experiment_name
    Settings.TRUST_MODEL_DESCRIPTION = EXPERIMENT_SETTINGS.trust_model_description
    
    
    Settings.VERIFY_ACCIDENT_REPORT_AUTHENTICITY = EXPERIMENT_SETTINGS.verify_authenticity_accident
    Settings.VERIFY_TRAFFIC_LIGHT_REQUEST_AUTHENTICITY = EXPERIMENT_SETTINGS.verify_authenticity_traffic_light
    Settings.SELECTED_TRUST_MODEL = EXPERIMENT_SETTINGS.trust_model

    TrustManagementSettings.USE_RELATIONSHIP_CONTEXT                = EXPERIMENT_SETTINGS.use_relationship_context


    TrustManagementSettings.TRUST_COMPUTATION_MODEL                 = EXPERIMENT_SETTINGS.trust_computation_model
    TrustManagementSettings.TRUST_DECISION_MAKING_MODEL             = EXPERIMENT_SETTINGS.trust_decision_making_model

    TrustManagementSettings.TRUST_UPDATE_MODEL                   = EXPERIMENT_SETTINGS.trust_update_strategy
    TrustManagementSettings.TRANSACTION_EXCHANGE_SCHEME             = EXPERIMENT_SETTINGS.transaction_exchange_scheme
    TrustManagementSettings.MAX_TRANSACTION_EXCHANGE_DISTANCE       = EXPERIMENT_SETTINGS.max_transaction_exchange_distance

    TrustManagementSettings.REPUTATION_SCOPE                        = EXPERIMENT_SETTINGS.reputation_scope
    TrustManagementSettings.REPUTATION_CONTEXT                      = EXPERIMENT_SETTINGS.reputation_context
    TrustManagementSettings.REPUTATION_COMPUTATION_STRATEGY         = EXPERIMENT_SETTINGS.reputation_computation_strategy
    
    TrustManagementSettings.TRUSTWORTHY_THRESHOLD_OF_RELATIONSHIPS       = EXPERIMENT_SETTINGS.trustworthy_threshold_for_trustee
    TrustManagementSettings.THRESHOLD_FOR_NUM_OF_TRUSTWORTHY_RELATIONSHIPS = EXPERIMENT_SETTINGS.threshold_for_required_trustworthy_relationships
    
    TrustManagementSettings.TRUST_TRANSACTION_THRESHOLD = EXPERIMENT_SETTINGS.trust_threshold
    
    
    if EXPERIMENT_SETTINGS.adaptive_trust_model_selector is not None:
        TrustManagementSettings.USES_ADAPTIVE_TRUST_MODEL_SELECTION = True
        TrustManagementSettings.ADAPTIVE_TRUST_MODEL_SELECTOR = EXPERIMENT_SETTINGS.adaptive_trust_model_selector
    
    
    TrustManagementSettings.TRUST_MODEL_SCHEME = TrustModelScheme(trust_computation_model=TrustManagementSettings.TRUST_COMPUTATION_MODEL,
                                                                  trust_decision_making_model=TrustManagementSettings.TRUST_DECISION_MAKING_MODEL,
                                                                  trust_update_model=TrustManagementSettings.TRUST_UPDATE_MODEL)
    
    
    

def load_configuration(configuration_file_path):
    data = None
    
    with open(configuration_file_path) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
        print(data)
    
    
    if data is None:
        raise Exception("No configuration data found")
    return data
    


