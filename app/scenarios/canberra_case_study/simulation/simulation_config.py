# config.py

# Simulation Settings

from core.models.devices.common import DeviceType
from trust.decision_making_module.trust_decision_maker import TrustDecisionMethod

from trust.transaction_exchange_scheme.trust_inference_engine import TransactionExchangeScheme
from trust.trust_recommenders.trust_model import TrustComputationModel


class SimulationConfiguration:
    

    MAX_NUMBER_OF_SIMULATION_RUNS = 3
    
    MAX_NUMBER_OF_TRAFFIC_ACCIDENTS = 10
    MAX_SIMULATION_DURATION = 3600

    INTERVAL_OF_ACCIDENTS = 100
    INTERVAL_OF_FALSE_ACCIDENTS = 100

    INTERVAL_OF_FALSE_TRAFFIC_LIGHT_REQUESTS = 60

    PERCENTAGE_OF_MALICIOUS_VEHICLES = 0.20  # Covers only smartphones and vehicles
    SIMULATION_RUN_INDEX = 0


class AccidentConfiguration:

    INITIAL_EMEREGENCY_PARKING_TIME: int = 10800

    PARKING_TIME_HOSPITAL : int = 3600
    PARKING_TIME_ACCIDENT : int = 20 
    EMERGENCY_TYPE_ID : str = "emergency_vehicle"

    ACCIDENT_SERVICE_REQUESTOR_DISTANCE : int = 40

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

    MAX_NUMBER_OF_ACCIDENTS = 20
    ALLOWED_EMERGENCY_VEHICLES = ['emergency']
    ALLOWED_ACCIDENT_SPEED = 5
    REPORTER_RADIUS = 30

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



class TrafficLightApplicationConfiguration:

    TRAFFIC_LIGHT_SERVICE_REQUESTOR_DISTANCE : int = 400
    TRAFFIC_LIGHT_VEHICLE_DISTANCE_SENSING : int = 60
    TRAFFIC_LIGHT_SMART_PHONE_DISTANCE_SENSING : int = 60

