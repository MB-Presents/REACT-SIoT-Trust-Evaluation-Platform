

import math
from typing import List
import string
from core.models.devices.common import DeviceShapeStatus

from trust.trust_recommenders.ontology_based.constants import FeatureSettings, MappingSettings


def signals(signal : int, mapping_settings : MappingSettings) -> List[str]:


    if signal ==  None:
        return []



    if not isinstance(signal, int):
        # TODO: Add error message
        return False

    EMERGENCY_BLINKER_MASK =    0b100
    BRAKE_LIGHT_MASK =          0b1000
    EMERGENCY_BLUE_LIGHT =      0b100000000000
    EMERGENCY_RED_LIGHT =       0b1000000000000
    EMERGENCY_YELLOW_LIGHT =    0b10000000000000
    
    signals :List[str] = []

    for permitted_signal in mapping_settings.PERMITTED_SIGNALS:
        if signal & EMERGENCY_BLINKER_MASK and permitted_signal == 'emergency_blinker':
            signals.append('emergency_blinker')
        elif signal & BRAKE_LIGHT_MASK and permitted_signal == 'brake_light':
            signals.append('brake_light')
        elif signal & EMERGENCY_BLUE_LIGHT and permitted_signal == 'emergency_blue_light':
            signals.append('emergency_blue_light')
        elif signal & EMERGENCY_RED_LIGHT and permitted_signal == 'emergency_red_light':
            signals.append('emergency_red_light')
        elif signal & EMERGENCY_YELLOW_LIGHT and permitted_signal == 'emergency_yellow_light':
            signals.append('emergency_yellow_light')

    return signals



def has_signal(record, signal_criteria : List[str]) -> bool:
    
    
    intersecting_set =  set(record).intersection(set(signal_criteria))

    if len(intersecting_set) > 0:
        return True
    return False





def speed_numerical(speed : str, feature_settings: FeatureSettings):

    if (speed == 'stopped'):
        return feature_settings.SPEED_STOPPED

    elif speed == 'slow':
        return feature_settings.SPEED_SLOW

    elif speed == 'medium':
        return feature_settings.SPEED_MEDIUM

    elif speed == 'fast':
        return feature_settings.SPEED_FAST

    elif speed == 'no existent':
        return feature_settings.SPEED_NO_EXISTENT


def speed(speed: float, mapping_settings: MappingSettings):

    if speed == None:
        return 'no existent'

    
    if (speed == mapping_settings.SPEED_STOPPED):
        return 'stopped'

    elif (speed > mapping_settings.SPEED_STOPPED) & (speed <= mapping_settings.SPEED_SLOW):
        return 'slow'

    elif (speed > mapping_settings.SPEED_SLOW) & (speed <= mapping_settings.SPEED_MEDIUM):
        return 'medium'

    elif (speed > mapping_settings.SPEED_MEDIUM):
        return 'fast'
    
    
    


def is_emergency_vehicle_dimension(length : float, width : float, height : float, mapping_settings: MappingSettings):
    
    if length == None or width == None or height== None:
        return False
    

    is_emengency_vehcile_length = (length >= mapping_settings.EMERGENCY_VEHICLE_DIMENSION_LOWER_BOUNDAIES['length']) & (length <= mapping_settings.EMERGENCY_VEHICLE_DIMENSION_UPPER_BOUNDAIES['length'])
    is_emeregency_vehicle_width = (width >= mapping_settings.EMERGENCY_VEHICLE_DIMENSION_LOWER_BOUNDAIES['width']) & (width <= mapping_settings.EMERGENCY_VEHICLE_DIMENSION_UPPER_BOUNDAIES['width'])
    
    is_emergency_vehicle_height = (height >= mapping_settings.EMERGENCY_VEHICLE_DIMENSION_LOWER_BOUNDAIES['height']) & (height <= mapping_settings.EMERGENCY_VEHICLE_DIMENSION_UPPER_BOUNDAIES['height'])
    
    if is_emengency_vehcile_length & is_emeregency_vehicle_width & is_emergency_vehicle_height:
        return True


    return False


def is_vehicle_dimension(length : float, width : float, height : float, mapping_settings: MappingSettings):

    if length == None or width == None or height== None:
        return False


    is_vehcile_length = (length >= mapping_settings.VEHICLE_DIMENSION_LOWER_BOUNDAIES['length']) & (length <= mapping_settings.VEHICLE_DIMENSION_UPPER_BOUNDAIES['length'])
    is_vehicle_width = (width >= mapping_settings.VEHICLE_DIMENSION_LOWER_BOUNDAIES['width']) & (width <= mapping_settings.VEHICLE_DIMENSION_UPPER_BOUNDAIES['width'])
    
    is_vehicle_height = (height >= mapping_settings.VEHICLE_DIMENSION_LOWER_BOUNDAIES['height']) & (height <= mapping_settings.VEHICLE_DIMENSION_UPPER_BOUNDAIES['height'])
    
    if is_vehcile_length & is_vehicle_width & is_vehicle_height:
        return True


    return False


def is_truck_dimension(length : float, width : float, height : float, mapping_settings: MappingSettings):
    
    if length == None or width == None or height== None:
        return False

    is_truck_length = (length >= mapping_settings.TRUCK_DIMENSION_LOWER_BOUNDAIES['length']) & (length <= mapping_settings.TRUCK_DIMENSION_UPPER_BOUNDAIES['length'])
    is_truck_width = (width >= mapping_settings.TRUCK_DIMENSION_LOWER_BOUNDAIES['width']) & (width <= mapping_settings.TRUCK_DIMENSION_UPPER_BOUNDAIES['width'])
    
    is_truck_height = (height >= mapping_settings.TRUCK_DIMENSION_LOWER_BOUNDAIES['height']) & (height <= mapping_settings.TRUCK_DIMENSION_UPPER_BOUNDAIES['height'])
    
    if is_truck_length & is_truck_width & is_truck_height:
        return True


    return False


def is_bus_dimension(length : float, width : float, height : float, mapping_settings: MappingSettings):
    
    if length == None or width == None or height== None:
        return False

    is_bus_length = (length >= mapping_settings.BUS_DIMENSION_LOWER_BOUNDAIES['length']) & (length <= mapping_settings.BUS_DIMENSION_UPPER_BOUNDAIES['length'])
    is_bus_width = (width >= mapping_settings.BUS_DIMENSION_LOWER_BOUNDAIES['width']) & (width <= mapping_settings.BUS_DIMENSION_UPPER_BOUNDAIES['width'])
    
    is_bus_height = (height >= mapping_settings.BUS_DIMENSION_LOWER_BOUNDAIES['height']) & (height <= mapping_settings.BUS_DIMENSION_UPPER_BOUNDAIES['height'])
    
    if is_bus_length & is_bus_width & is_bus_height:
        return True


    return False

def is_motobike_dimension(length : float, width : float, height : float, mapping_settings: MappingSettings):
    
    if length == None or width == None or height== None:
        return False

    is_motobike_length = (length >= mapping_settings.MOTOBIKE_DIMENSION_LOWER_BOUNDAIES['length']) & (length <= mapping_settings.MOTOBIKE_DIMENSION_UPPER_BOUNDAIES['length'])
    is_motobike_width = (width >= mapping_settings.MOTOBIKE_DIMENSION_LOWER_BOUNDAIES['width']) & (width <= mapping_settings.MOTOBIKE_DIMENSION_UPPER_BOUNDAIES['width'])
    
    is_motobike_height = (height >= mapping_settings.MOTOBIKE_DIMENSION_LOWER_BOUNDAIES['height']) & (height <= mapping_settings.MOTOBIKE_DIMENSION_UPPER_BOUNDAIES['height'])
    
    if is_motobike_length & is_motobike_width & is_motobike_height:
        return True


    return False

def is_bicycle_dimension(length : float, width : float, height : float, mapping_settings: MappingSettings):
    
    if length == None or width == None or height== None:
        return False
    

    is_bicycle_length = (length >= mapping_settings.BICYCLE_DIMENSION_LOWER_BOUNDAIES['length']) & (length <= mapping_settings.BICYCLE_DIMENSION_UPPER_BOUNDAIES['length'])
    is_bicycle_width = (width >= mapping_settings.BICYCLE_DIMENSION_LOWER_BOUNDAIES['width']) & (width <= mapping_settings.BICYCLE_DIMENSION_UPPER_BOUNDAIES['width'])
    
    is_bicycle_height = (height >= mapping_settings.BICYCLE_DIMENSION_LOWER_BOUNDAIES['height']) & (height <= mapping_settings.BICYCLE_DIMENSION_UPPER_BOUNDAIES['height'])
    
    if is_bicycle_length & is_bicycle_width & is_bicycle_height:
        return True


    return False

def is_person_dimension(length : float, width : float, height : float, mapping_settings: MappingSettings):
    
    if length == None or width == None or height== None:
        return False

    is_person_length = (length >= mapping_settings.PERSON_DIMENSION_LOWER_BOUNDAIES['length']) & (length <= mapping_settings.PERSON_DIMENSION_UPPER_BOUNDAIES['length'])
    is_person_width = (width >= mapping_settings.PERSON_DIMENSION_LOWER_BOUNDAIES['width']) & (width <= mapping_settings.PERSON_DIMENSION_UPPER_BOUNDAIES['width'])
    
    is_person_height = (height >= mapping_settings.PERSON_DIMENSION_LOWER_BOUNDAIES['height']) & (height <= mapping_settings.PERSON_DIMENSION_UPPER_BOUNDAIES['height'])
    
    if is_person_length & is_person_width & is_person_height:
        return True
    return False

def has_dimension(record, dimension_criteria : List[str]) -> bool:

    intersecting_set = set(record).intersection(set(dimension_criteria))

    if len(intersecting_set) > 0:
        return True
    return False

def vehicle_dimensions(length : float, width : float, height : float, mapping_settings: MappingSettings):
    
    possible_vehicle_categories = []
    
    if length ==  None or width == None or height == None:
        return possible_vehicle_categories
    
    if is_emergency_vehicle_dimension(length, width, height, mapping_settings):
        possible_vehicle_categories.append('emergency_vehicle')
        
    if is_truck_dimension(length, width, height, mapping_settings):
        possible_vehicle_categories.append('truck')
    
    if is_bus_dimension(length, width, height, mapping_settings):
        possible_vehicle_categories.append('bus')
    
    if is_motobike_dimension(length, width, height, mapping_settings):
        possible_vehicle_categories.append('motobike')
    
    if is_bicycle_dimension(length, width, height, mapping_settings):
        possible_vehicle_categories.append('bicycle')
        
    if is_person_dimension(length, width, height, mapping_settings):
        possible_vehicle_categories.append('person')
        
    if is_vehicle_dimension(length, width, height, mapping_settings):
        possible_vehicle_categories.append('vehicle')
    
    
    
    return possible_vehicle_categories
    


def object_functional_status(device_shape_status: DeviceShapeStatus, mapping_settings: MappingSettings):

    if device_shape_status == None:
        return 'unknown'
    
    if DeviceShapeStatus.ORIGINAL_MANUFACTURED == device_shape_status:
        return 'functional'
    
    elif DeviceShapeStatus.DEFORMED == device_shape_status:
        return 'damaged'
    
    elif DeviceShapeStatus.HEAVILY_DAMAGED == device_shape_status:
        return 'damaged'
    
        
    elif DeviceShapeStatus.DENTS == device_shape_status:
        return 'dents'
    
    elif DeviceShapeStatus.SCRATCHES == device_shape_status:
        return 'scratches'
    else:
        return 'unknown'
    


def vehicle_type(vehicle_type : str, mapping_settings: MappingSettings):
    
    if vehicle_type == None:
        return 'unknown'

    if (vehicle_type == mapping_settings.VEHICLE_TYPE_CAR):
        return 'car'

    elif (vehicle_type == mapping_settings.VEHICLE_TYPE_TRUCK):
        return 'truck'
    
    elif (vehicle_type == mapping_settings.VEHICLE_TYPE_BUS):
        return 'bus'
    
    elif (vehicle_type == mapping_settings.VEHICLE_TYPE_MOTORBIKE):    
        return 'motorbike'
    
    elif (vehicle_type == mapping_settings.VEHILCE_TYPE_BICYCLE):
        return 'bicycle'
    
    elif (vehicle_type == mapping_settings.VEHICLE_TYPE_EMERGENCY_VEHICLE):
        return 'emergency'
    
    else:
        return 'other type'
    
    
 



def classify_distance(object_1 : List[float], object_2 : List[float], mapping_settings : MappingSettings):
    
    if object_1 ==  None or object_2 == None:
        return 'unknown'

    distance = math.dist([float(object_1[0]), float(object_1[1])], [float(object_2[0]), float(object_2[1])])

    if distance <= mapping_settings.CLOSE_DISTANCE_SENSED_OBJECT:
        return 'nearby'

    elif distance > mapping_settings.CLOSE_DISTANCE_SENSED_OBJECT and distance <= mapping_settings.DISTANT_DISTANCE_SENSED_OBJECT:
        return 'close'

    elif distance > mapping_settings.DISTANT_DISTANCE_SENSED_OBJECT and distance <= mapping_settings.FAR_DISTANCE_SENSED_OBJECT:
        return 'distant'

    elif distance > mapping_settings.FAR_DISTANCE_SENSED_OBJECT:
        return 'far'

    return 'unknown'


    
    
def classify_distance_interested_object(sensed_device_position: List[float], object_of_interest_position: List[float], mapping_settings : MappingSettings):

    if sensed_device_position == None or object_of_interest_position ==  None:
        return 'unknown'

    distance = math.dist([float(sensed_device_position[0]), float(sensed_device_position[1])], [float(object_of_interest_position[0]), float(object_of_interest_position[1])])

    if distance <= mapping_settings.CLOSE_DISTANCE_INTERESTED_OBJECT:
        return 'nearby'

    elif distance > mapping_settings.CLOSE_DISTANCE_INTERESTED_OBJECT and distance <= mapping_settings.DISTANT_DISTANCE_INTERESTED_OBJECT:
        return 'close'

    elif distance > mapping_settings.DISTANT_DISTANCE_INTERESTED_OBJECT and distance <= mapping_settings.FAR_DISTANCE_INTERESTED_OBJECT:
        return 'distant'

    elif distance > mapping_settings.FAR_DISTANCE_INTERESTED_OBJECT:
        return 'far'

    return 'unknown'



def distance_value_sensed_object(distance : str, settings : FeatureSettings):


    if (distance == 'nearby'):
        return settings.NEAR_DISTANCE_SENSED_OBJECT

    elif (distance == 'close'):
        return settings.CLOSE_DISTANCE_SENSED_OBJECT
    
    elif (distance == 'distant'):
        return settings.DISTANT_DISTANCE_SENSED_OBJECT

    elif (distance == 'far'):
        return settings.FAR_DISTANCE_SENSED_OBJECT

    return settings.NO_SENSED_OBJECT


def distance_value_interested_object(distance : str, settings : FeatureSettings):


    if (distance == 'nearby'):
        return settings.NEAR_DISTANCE_INTERESTED_OBJECT

    elif (distance == 'close'):
        return settings.CLOSE_DISTANCE_INTERESTED_OBJECT
    
    elif (distance == 'distant'):
        return settings.DISTANT_DISTANCE_INTERESTED_OBJECT

    elif (distance == 'far'):
        return settings.FAR_DISTANCE_INTERESTED_OBJECT

    return settings.NO_INTERESTED_OBJECT
