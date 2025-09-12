

from enum import Enum, auto
from typing import Dict, List





class TrustModelSettings:
    MIN_SERVICE_PROVIDER = 2
    AUTHENTICITY_THRESHOLD = 0.65
    CONFIDENCE_THRESHOLD = 0.5
    IDENTIFICATION_THRESHOLD = 0.5
    ADAPTIVE_CONFIDENCE_THRESHOLD = 0.5
    ADAPTIVE_IDENTIFICATION_THRESHOLD = 0.5
    
    TIME_SENSITIVITY_REACHED = False
    
    
class TrustModelSettingsEmergencyCall(TrustModelSettings):
    MIN_SERVICE_PROVIDER = 5
    AUTHENTICITY_THRESHOLD = 0.5
    CONFIDENCE_THRESHOLD = 0.7
    
    ADAPTIVE_CONFIDENCE_THRESHOLD = 0.5
    ADAPTIVE_IDENTIFICATION_THRESHOLD = 0.5
    
    
    TIME_SENSITIVITY_REACHED = False
    
    
class TrustModelSettingsTrafficLight(TrustModelSettings):
    MIN_SERVICE_PROVIDER    = 3
    AUTHENTICITY_THRESHOLD  = 0.5
    CONFIDENCE_THRESHOLD    = 0.5
    
    
    ADAPTIVE_CONFIDENCE_THRESHOLD = 0.5
    ADAPTIVE_IDENTIFICATION_THRESHOLD = 0.5
    
    TIME_SENSITIVITY_REACHED = False





class Weight:
    SIGNAL: float = 0.3
    SPEED: float = 0.2
    DIMENSION: float = 0.2

    TYPE: float = 0.2
    VEHICLE_SHAPE: float = 0.4
    # LICENSEPLATE : float = 0.7
    LOCATION_ID: float = 0.3

    LOCATION_CLOSENESS: float = 0.5
    POSITION: float = 0.35
    SPEED_LOCATION: float = 0.15


class WeightSettings:
    SIGNAL: float
    SPEED: float
    DIMENSION: float

    TYPE: float
    VEHICLE_SHAPE: float
    # LICENSEPLATE : float = 0.7
    LOCATION_ID: float

    LOCATION_CLOSENESS: float
    POSITION: float
    SPEED_LOCATION: float


class EmergencyCallWeightSettings:
    SIGNAL: float = 0.2
    SPEED: float = 0.1
    DIMENSION: float = 0.1

    TYPE: float = 0.1
    VEHICLE_SHAPE: float = 0.4
    LICENSEPLATE: float = 0.7
    LOCATION_ID: float = 0.2

    LOCATION_CLOSENESS: float = 0.0
    POSITION: float = 0.9
    SPEED_LOCATION: float = 0.1


class TrafficLightWeightSettings(WeightSettings):
    SIGNAL: float = 0.4
    SPEED: float = 0
    DIMENSION: float = 0.4

    TYPE: float = 0.2
    COLOR: float = 0.4
    VEHICLE_SHAPE: float = 0.2
    # LICENSEPLATE : float = 0.7
    LOCATION_ID: float = 0.5

    LOCATION_CLOSENESS: float = 0.5
    SPEED_LOCATION: float = 0.0
    POSITION: float = 0.5
    
    


class  MappingSettings:
    SPEED_STOPPED: float = 0.0
    SPEED_SLOW: float = 8.0
    SPEED_MEDIUM: float = 15.0

    PERMITTED_SIGNALS: List[str]
    
    VEHICLE_DIMENSION_LOWER_BOUNDAIES: Dict[str, float] = {
        'length': 2.5,
        'width': 1.6,
        'height': 0.9
    }
    VEHICLE_DIMENSION_UPPER_BOUNDAIES: Dict[str, float] = {
        'length': 7.0,
        'width': 2.0,
        'height': 1.8
    }

    TRUCK_DIMENSION_LOWER_BOUNDAIES: Dict[str, float] = {
        'length': 6.0,
        'width': 2.2,
        'height': 2.4
    }

    TRUCK_DIMENSION_UPPER_BOUNDAIES: Dict[str, float] = {
        'length': 12.0,
        'width': 2.5,
        'height': 3.5
    }

    BUS_DIMENSION_LOWER_BOUNDAIES: Dict[str, float] = {
        'length': 9.0,
        'width': 2.5,
        'height': 3.5
    }
    BUS_DIMENSION_UPPER_BOUNDAIES: Dict[str, float] = {
        'length': 12.0,
        'width': 3.5,
        'height': 3.5
    }

    MOTOBIKE_DIMENSION_LOWER_BOUNDAIES: Dict[str, float] = {
        'length': 1.5,
        'width': 0.7,
        'height': 1.0
    }

    MOTOBIKE_DIMENSION_UPPER_BOUNDAIES: Dict[str, float] = {
        'length': 2.5,
        'width': 1.0,
        'height': 1.5
    }

    EMERGENCY_VEHICLE_DIMENSION_LOWER_BOUNDAIES: Dict[str, float] = {
        'length': 4.5,
        'width': 1.8,
        'height': 1.8
    }

    EMERGENCY_VEHICLE_DIMENSION_UPPER_BOUNDAIES: Dict[str, float] = {
        'length': 6.8,
        'width': 2.4,
        'height': 3.0
    }

    BICYCLE_DIMENSION_LOWER_BOUNDAIES: Dict[str, float] = {
        'length': 1.0,
        'width': 0.5,
        'height': 0.5
    }

    BICYCLE_DIMENSION_UPPER_BOUNDAIES: Dict[str, float] = {
        'length': 1.7,
        'width': 0.7,
        'height': 1.8
    }

    PERSON_DIMENSION_LOWER_BOUNDAIES: Dict[str, float] = {
        'length': 0.3,
        'width': 0.4,
        'height': 0.5
    }

    PERSON_DIMENSION_UPPER_BOUNDAIES: Dict[str, float] = {
        'length': 0.7,
        'width': 1.2,
        'height': 2.3
    }


    VEHICLE_DIMENSION_SMALL: List[float]
    VEHICLE_DIMENSION_MEDIUM: List[float]
    VEHICLE_DIMENSION_LARGE: List[float]
    VEHICLE_DIMENSION_UNKNOWN: List[float]

    VEHICLE_TYPE_TRUCK: str = "truck_truck"
    VEHICLE_TYPE_CAR: str = "veh_passenger"
    VEHICLE_TYPE_EMERGENCY_VEHICLE : str = "emergency_vehicle"
    VEHICLE_TYPE_MOTORBIKE: str = "moto_motorcycle"
    VEHICLE_TYPE_BUS: str = "bus_bus"
    VEHILCE_TYPE_BICYCLE : str = "bicycle_bicycle"
    
        

    VEHICLE_SHAPE_DAMAGED: List[float] = [255.0, 0.0, 0.0, 255.0]
    VEHICLE_SHAPE_FUNCTIONAL: List[float] = [255.0, 255.0, 0, 255.0]
    VEHICLE_SHAPE_REPAIRED: List[float] = [0, 255, 0, 255.0]
    VEHICLE_SHAPE_UNKNOWN: List[float] = []

    LOCATION_ID_CLOSE: List[str]
    LOCATION_ID_FAR: List[str]

    POSITION_FRONT: List[str]
    POSITION_BACK: List[str]
    POSITION_SIDE: List[str]
    POSITION_UNKNOWN: List[str]

    SPEED_LOCATION_FAST: List[float]
    SPEED_LOCATION_MEDIUM: List[float]
    SPEED_LOCATION_SLOW: List[float]
    SPEED_LOCATION_UNKNOWN: List[float]

    SIGNAL_GREEN: List[str]
    SIGNAL_YELLOW: List[str]
    SIGNAL_RED: List[str]
    SIGNAL_UNKNOWN: List[str]

    CLOSE_DISTANCE_SENSED_OBJECT: float
    DISTANT_DISTANCE_SENSED_OBJECT: float
    FAR_DISTANCE_SENSED_OBJECT: float

    CLOSE_DISTANCE_INTERESTED_OBJECT: float
    DISTANT_DISTANCE_INTERESTED_OBJECT: float
    FAR_DISTANCE_INTERESTED_OBJECT: float

    VEHICLE_TYPE_TRUCK: str
    VEHICLE_TYPE_CAR: str


class EmergencyCallMappingSettings(MappingSettings):
    SPEED_STOPPED: float = 0.0
    SPEED_SLOW: float = 8.0
    SPEED_MEDIUM: float = 15.0

    CLOSE_DISTANCE_SENSED_OBJECT: float = 30.0
    DISTANT_DISTANCE_SENSED_OBJECT: float = 50.0
    FAR_DISTANCE_SENSED_OBJECT: float = 70.0

    NEAR_DISTANCE_INTERESTED_OBJECT: float = 0.0
    CLOSE_DISTANCE_INTERESTED_OBJECT: float = 10.0
    DISTANT_DISTANCE_INTERESTED_OBJECT: float = 20.0
    FAR_DISTANCE_INTERESTED_OBJECT: float = 30.0

    PERMITTED_SIGNALS: List[str] = ['emergency_blinker', 'brake_light']


class TrafficLightMappingSettings(MappingSettings):
    SPEED_STOPPED: float = 0.0
    SPEED_SLOW: float = 8.0
    SPEED_MEDIUM: float = 15.0

    CLOSE_DISTANCE_SENSED_OBJECT: float = 30.0          # 10.0
    DISTANT_DISTANCE_SENSED_OBJECT: float = 50.0        # 30.0
    FAR_DISTANCE_SENSED_OBJECT: float = 100.0            # 100.0

    NEAR_DISTANCE_INTERESTED_OBJECT: float = 10.0
    CLOSE_DISTANCE_INTERESTED_OBJECT: float = 30.0
    DISTANT_DISTANCE_INTERESTED_OBJECT: float = 50.0
    FAR_DISTANCE_INTERESTED_OBJECT: float = 70.0

    PERMITTED_SIGNALS: List[str] = ['emergency_blue_light', 'emergency_yellow_light', 'emergency_red_light']


class FeatureSettings:
    SPEED_STOPPED: float
    SPEED_SLOW: float
    SPEED_MEDIUM: float
    SPEED_FAST: float
    SPEED_NO_EXISTENT : float = 0.0

    VEHICLE_DIMENSION_SMALL: float
    VEHICLE_DIMENSION_MEDIUM: float
    VEHICLE_DIMENSION_LARGE: float
    VEHICLE_DIMENSION_UNKNOWN: float = 0.0
    

    VEHICLE_TYPE_CAR: float
    VEHICLE_TYPE_TRUCK: float
    VEHICLE_TYPE_BUS: float
    VEHICLE_TYPE_UNKNOWN: float = 0.0

    VEHICLE_COLOR_RED: float
    VEHICLE_COLOR_BLUE: float
    VEHICLE_COLOR_GREEN: float
    VEHICLE_COLOR_UNKNOWN: float = 0.0

    LOCATION_ID_CLOSE: float
    LOCATION_ID_FAR: float

    POSITION_FRONT: float
    POSITION_BACK: float
    POSITION_SIDE: float
    POSITION_UNKNOWN: float 

    SPEED_LOCATION_FAST: float
    SPEED_LOCATION_MEDIUM: float
    SPEED_LOCATION_SLOW: float
    SPEED_LOCATION_UNKNOWN: float = 0.0

    SIGNAL_GREEN: float
    SIGNAL_YELLOW: float
    SIGNAL_RED: float
    SIGNAL_UNKNOWN: float = 0.0

    NEAR_DISTANCE_SENSED_OBJECT: float
    CLOSE_DISTANCE_SENSED_OBJECT: float
    DISTANT_DISTANCE_SENSED_OBJECT: float
    FAR_DISTANCE_SENSED_OBJECT: float
    NO_SENSED_OBJECT : float = 0.0


    NEAR_DISTANCE_INTERESTED_OBJECT: float
    CLOSE_DISTANCE_INTERESTED_OBJECT: float
    DISTANT_DISTANCE_INTERESTED_OBJECT: float
    FAR_DISTANCE_INTERESTED_OBJECT: float
    NO_INTERESTED_OBJECT : float = 0.0

    REQUIRED_CLOSENESS_DISTANCE: List[str]

    SPEED_CRITERIA: List[str]
    DIMENSION_CRITERIA: List[str]
    TYPE_CRITERIA: List[str]
    COLOR_CRITERIA: List[str]
    VEHICLE_SHAPE_CRITERIA : List[str]

    SIGNAL_CRITERIA: List[str]
    
    DECAY_FACTOR : float 
    MAX_TIME_THRESHOLD : float

class EmergencyCallFeatureSettings(FeatureSettings):
    SPEED_STOPPED: float = 1
    SPEED_SLOW: float = 0.9
    SPEED_MEDIUM: float = 0.8
    SPEED_FAST: float = 0.7
    

    VEHICLE_DIMENSION_SMALL: float = 0.9
    VEHICLE_DIMENSION_MEDIUM: float = 0.8
    VEHICLE_DIMENSION_LARGE: float = 0.7
    VEHICLE_DIMENSION_UNKNOWN: float = 0.6
    

    VEHICLE_TYPE_CAR: float = 0.9
    VEHICLE_TYPE_TRUCK: float = 0.8
    VEHICLE_TYPE_BUS: float = 0.7
    VEHICLE_TYPE_UNKNOWN: float = 0.6
    

    VEHICLE_COLOR_RED: float = 0.9
    VEHICLE_COLOR_BLUE: float = 0.8
    VEHICLE_COLOR_GREEN: float = 0.7
    VEHICLE_COLOR_UNKNOWN: float = 0.6

    LOCATION_ID_CLOSE: float = 0.9
    LOCATION_ID_FAR: float = 0.8
    

    POSITION_FRONT: float = 0.9
    POSITION_BACK: float = 0.8
    POSITION_SIDE: float = 0.7
    POSITION_UNKNOWN: float = 0.6
    

    SPEED_LOCATION_FAST: float = 0.9
    SPEED_LOCATION_MEDIUM: float = 0.8
    SPEED_LOCATION_SLOW: float = 0.7
    SPEED_LOCATION_UNKNOWN: float = 0.6

    SIGNAL_GREEN: float = 0.9
    SIGNAL_YELLOW: float = 0.8
    SIGNAL_RED: float = 0.7
    SIGNAL_UNKNOWN: float = 0.6
    

    NEAR_DISTANCE_SENSED_OBJECT: float = 1.0
    CLOSE_DISTANCE_SENSED_OBJECT: float = 0.9
    DISTANT_DISTANCE_SENSED_OBJECT: float = 0.75
    FAR_DISTANCE_SENSED_OBJECT: float = 0


    # ACCIDENT VEHICLE
    NEAR_DISTANCE_INTERESTED_OBJECT: float = 1.0
    CLOSE_DISTANCE_INTERESTED_OBJECT: float = 0.8
    DISTANT_DISTANCE_INTERESTED_OBJECT: float = 0.4
    FAR_DISTANCE_INTERESTED_OBJECT: float = 0

    REQUIRED_CLOSENESS_DISTANCE_SENSED_DEVICE_INTERESTED_OBJECT: List[str] = ['nearby']

    SPEED_CRITERIA: List[str] = ['stopped']
    DIMENSION_CRITERIA: List[str] = ['truck','bus','motobike','vehicle']
    TYPE_CRITERIA: List[str] = ['car', 'truck', 'bus']
    VEHICLE_SHAPE_CRITERIA: List[str] = ['damaged']
    
    SIGNAL_CRITERIA: List[str] = ['emergency_blinker']
    
    DECAY_FACTOR : float = 0.0005
    MAX_TIME_THRESHOLD : float = 60


class TrafficLightFeatureSettings(FeatureSettings):
    SPEED_STOPPED: float = 1
    SPEED_SLOW: float = 0.9
    SPEED_MEDIUM: float = 0.8
    SPEED_FAST: float = 0.7

    VEHICLE_DIMENSION_SMALL: float = 0.9
    VEHICLE_DIMENSION_MEDIUM: float = 0.8
    VEHICLE_DIMENSION_LARGE: float = 0.7
    VEHICLE_DIMENSION_UNKNOWN: float = 0.6

    VEHICLE_TYPE_CAR: float = 0.9
    VEHICLE_TYPE_TRUCK: float = 0.8
    VEHICLE_TYPE_BUS: float = 0.7
    VEHICLE_TYPE_UNKNOWN: float = 0.6

    VEHICLE_COLOR_RED: float = 0.9
    VEHICLE_COLOR_BLUE: float = 0.8
    VEHICLE_COLOR_GREEN: float = 0.7
    VEHICLE_COLOR_UNKNOWN: float = 0.6

    LOCATION_ID_CLOSE: float = 0.9
    LOCATION_ID_FAR: float = 0.8

    POSITION_FRONT: float = 0.9
    POSITION_BACK: float = 0.8
    POSITION_SIDE: float = 0.7
    POSITION_UNKNOWN: float = 0.6

    SPEED_LOCATION_FAST: float = 0.9
    SPEED_LOCATION_MEDIUM: float = 0.8
    SPEED_LOCATION_SLOW: float = 0.7
    SPEED_LOCATION_UNKNOWN: float = 0.6

    SIGNAL_GREEN: float = 0.9
    SIGNAL_YELLOW: float = 0.8
    SIGNAL_RED: float = 0.7
    SIGNAL_UNKNOWN: float = 0.6

    NEAR_DISTANCE_SENSED_OBJECT: float = 1.0
    CLOSE_DISTANCE_SENSED_OBJECT: float = 0.9
    DISTANT_DISTANCE_SENSED_OBJECT: float = 0.6
    FAR_DISTANCE_SENSED_OBJECT: float = 0

    # ACCIDENT VEHICLE
    NEAR_DISTANCE_INTERESTED_OBJECT: float = 1.0
    CLOSE_DISTANCE_INTERESTED_OBJECT: float = 0.7
    DISTANT_DISTANCE_INTERESTED_OBJECT: float = 0.4
    FAR_DISTANCE_INTERESTED_OBJECT: float = 0

    REQUIRED_CLOSENESS_DISTANCE_SENSED_DEVICE_INTERESTED_OBJECT: List[str] = ['nearby']
    
    SPEED_CRITERIA: List[str] = ['stopped', 'slow','medium','fast']
    DIMENSION_CRITERIA: List[str] = ['emergency_vehicle']
    TYPE_CRITERIA: List[str] = ['emergency']
    VEHICLE_SHAPE_CRITERIA: List[str] = ['functional']
    SIGNAL_CRITERIA: List[str] = ['emergency_blue_light']
    
    
    
    DECAY_FACTOR : float = 0.05
    MAX_TIME_THRESHOLD : float = 20
