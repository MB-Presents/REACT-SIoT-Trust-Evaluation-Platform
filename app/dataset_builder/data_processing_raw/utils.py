import math
from pandas import DataFrame


def get_device_mapping(device_mapping, devices_candidates):
    
    counter = len(device_mapping) + 1
    
    for device_id, device in devices_candidates.items():
        if device_id not in device_mapping:
            
            device_mapping[device_id] = counter
            counter += 1
            
    return device_mapping


def get_events_in_time(df_events : DataFrame, time):
    return df_events[(df_events.start_time <= time) & (df_events.end_time >= time)]

    
    
def is_event_nearby(device, coordinates, radius = 50.0):
    
    device_pos = device['position']
    distance = math.dist(device_pos, coordinates)

    if distance <= radius:
        return True
    
    return False