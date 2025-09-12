




from enum import Enum, auto


class TrustModel(Enum):
    NONE = auto()
    CBSTM_TRUST_MODEL = auto()
    DYNAMIC_TRUST_MODEL = auto()
    ONTOLOGY_BASED_TRUST_MODEL = auto()
    
class Settings:
    
    INTERVAL_OF_ACCIDENTS: int = 80
    INTERVAL_OF_FALSE_ACCIDENTS: int = 50
    
    INTERVAL_OF_FALSE_TRAFFIC_LIGHT_REQUESTS: int = 100
    
    MAX_NUMBER_SIMULATION_RUNS: int = 3
    MAX_NUMBER_TRAFFIC_ACCIDENTS: int = 3
    SIMULATION_RUN_INDEX: int = 0
    EXPERIMENT_NAME: str = 'PLACEHOLDER'
    EXPERIMENT_ID: str = 'EXP001'
    
    VERIFY_ACCIDENT_REPORT_AUTHENTICITY: bool = True
    VERIFY_TRAFFIC_LIGHT_REQUEST_AUTHENTICITY: bool = True
    
    SELECTED_TRUST_MODEL: TrustModel = TrustModel.ONTOLOGY_BASED_TRUST_MODEL
    
    TRUST_MODEL_DESCRIPTION: str = "Ontology-based Trust Model"
    
    MAX_SIMULATION_DURATION: int = 3600
    PERCENTAGE_OF_MALICIOUS_VEHICLES: float = 0.4
    
    ROOT_DIRECTORY: str = '/app/output/simulation_runs'
    TAKE_SCREENSHOTS : bool = False
    