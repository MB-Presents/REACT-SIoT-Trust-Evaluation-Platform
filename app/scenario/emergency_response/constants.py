from enum import Enum, auto
from traci import lane

from data_models.iot_devices.common import DeviceType


class AccidentVehicleAssignmentState(Enum):
    """The status of an accident report."""
    
    PENDING = auto()
    PROCESSING = auto()
    PROCESSED = auto()

class EmergencyVehicleStatus(Enum):
    AT_START = auto()
    HEADING_TO_ACCIDENT = auto()
    AT_ACCIDENT = auto()
    HEADING_TO_HOSPITAL = auto()
    STOPPED_AT_HOSPITAL = auto()
    FINISHED = auto()
    
    
class AccidentStatus(Enum): 
    UNSOLVED = auto()
    AUTHENTICITY_ASSESSMENT = auto()
    IN_PROGRESS = auto()
    COMPLETE_SOLVED = auto()
    IGNORE_UNSOVLED = auto()
    ACCIDENT_SOLVED = auto()
    IN_PROGRESS_HOSPITAL = auto()
    
class AccidentSettings:
    INITIAL_EMEREGENCY_PARKING_TIME: int = 10800
    
    PARKING_TIME_HOSPITAL : int = 3600
    PARKING_TIME_ACCIDENT : int = 20 
    EMERGENCY_TYPE_ID : str = "emergency_vehicle"
    
    SERVICE_REQUESTOR_DISTANCE : int = 70


    ALLOWED_ROAD_VEHICLES = [
        'private',
        'emergency',
        'authority', 'army', 'vip', 'passenger', 'hov', 'taxi', 'bus', 'coach',
        'delivery', 'truck', 'trailer', 'motorcycle',
        'moped',
        'bicycle',
        'evehicle',
        'custom1',
        'custom2'
    ]

    ALLOWED_VEHICLE_COLLISION_TYPES = ['veh_passenger']
    ALLOWED_VEHICLE_FAKE_COLLISION_TYPES = ["veh_passenger", "truck_truck", "bus_bus"]
    
    # ALLOWED_VEHICLE_REPORTER_TYPES = ['veh_passenger', 'ped_pedestrian', 'moto_motorcycle', 'bike_bicycle']
    ALLOWED_VEHICLE_REPORTER_TYPES = [
        DeviceType.VEHICLE,
        DeviceType.SMART_PHONE
    ]

    MAX_NUMBER_OF_ACCIDENTS = 10
    ALLOWED_EMERGENCY_VEHICLES = ['emergency']
    ALLOWED_ACCIDENT_SPEED = 5
    REPORTER_RADIUS = 30
    
    
    EMERGENCY_VEH_IDS = ['emergency_veh_1']
    EMERGENCY_DROP_OFF_LANE_POSITION = 145
    # EMERGENCY_VEH_IDS = ['emergency_veh_1','emergency_veh_2']
    
    EMERGENCY_VEHS = {
        'emergency_veh_1': {
            'emergency_drop_off': '668452814',
            'emergency_drop_off_lane': '668452814_0',
            'emergency_drop_off_position': 145,
            'initial_emergency_location': '994397868',
            'initial_parking_time': 10800,
            'emergency_vehicle_type': 'emergency_vehicle'
            },
        'emergency_veh_2': {
            'emergency_drop_off': '668452814',
            'emergency_drop_off_lane': '668452814_0',
            'emergency_drop_off_position': 120,
            'initial_emergency_location': '994397868',
            'initial_parking_time': 10800,
            'emergency_vehicle_type': 'emergency_vehicle'
        },
        
    }
    
    EMERGENCY_DROP_OFF = '668452814'  # North of Canberra
    EMERGENCY_DROP_OFF_LANE = EMERGENCY_DROP_OFF + "_0"
    
    
    EMERGENCY_LANE = '668452814_0'
    INITIAL_EMERGENCY_LOCATION = '994397868'
        
    EMERGENCY_DROP_OFF_LENGTH = None



    
