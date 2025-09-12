
from traci import constants as tc


class ScenarioParameters:


    TIME : float = 0
    DEVICE_ID : int = 1
    logging_info_active =  True


class ScenarioDeviceConfiguration:

    TRACI_CONSTANTS = [
        tc.VAR_TYPE,
        tc.VAR_SPEED,
        tc.VAR_ANGLE,
        tc.VAR_LENGTH,
        tc.VAR_WIDTH,
    ]

    TRACI_PERSON_CONSTANTS = TRACI_CONSTANTS + [
        tc.VAR_POSITION,
        tc.VAR_VEHICLE
    ]

    TRACI_VEHICLE_CONSTANTS = TRACI_CONSTANTS + [
        tc.VAR_POSITION3D,
        tc.VAR_SIGNALS,
        tc.VAR_VEHICLECLASS
    ]
    
    SMART_PHONE_FEATURES = [
        tc.VAR_SPEED, 
        tc.VAR_POSITION,
        tc.VAR_TYPE,
        tc.VAR_ROAD_ID,
        tc.VAR_LANE_ID,
        tc.VAR_LANEPOSITION
    ]
    
    VEHICLE_FEATURES = [tc.VAR_SPEED,
        tc.VAR_POSITION,
        tc.VAR_SIGNALS,
        tc.VAR_ROAD_ID,
        tc.VAR_LANE_ID,
        tc.VAR_COLOR,
        tc.VAR_LANEPOSITION, 
        tc.VAR_TYPE,
        tc.VAR_LENGTH,
        tc.VAR_WIDTH,
        tc.VAR_HEIGHT,
        tc.VAR_LANE_INDEX,
        tc.VAR_VEHICLECLASS]

    TRAFFIC_LIGHT_FEATURES = [  
        tc.TL_CONTROLLED_LANES, 
        tc.TL_CONTROLLED_LINKS, 
        tc.TL_CURRENT_PROGRAM, 
        tc.TL_CURRENT_PHASE,
        tc.TL_NEXT_SWITCH, 
        tc.TL_PHASE_DURATION, 
        tc.TL_RED_YELLOW_GREEN_STATE
    ]

    REPORTER_FEATURES = SMART_PHONE_FEATURES
    
    