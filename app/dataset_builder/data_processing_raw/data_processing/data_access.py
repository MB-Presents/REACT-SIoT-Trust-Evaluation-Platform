import utils.query_elk_2 as query_elk_2
import pandas as pd

def get_events():
    events = query_elk_2.get_events()
    events = query_elk_2.remove_extra_attributes(events)
    df_events = pd.DataFrame(events)
    return df_events

def get_reports():
    reports = query_elk_2.get_reports()
    reports = query_elk_2.remove_extra_attributes(reports)
    df_reports = pd.DataFrame(reports)
    return df_reports

def get_device_states(time):
    devices_candidates = query_elk_2.get_object_state_at_timestep(time)
    devices = query_elk_2.remove_extra_attributes(devices_candidates)
    devices_candidates = {item['device_id']: item for item in devices}
    return devices_candidates

def get_max_time():
    return query_elk_2.get_max_time()



def get_device_states_batch(start_time, end_time):
    # Fetch device states for a range of times in a single batch query
    # Assuming query_elk.get_object_states_for_time_range is a function that can fetch states for a range of times
    batch_device_states = query_elk_2.get_object_states_for_time_range(start_time, end_time)
    
    
    # Initialize an empty dictionary to hold device states keyed by time
    device_states_by_time = {}
    
    for record in batch_device_states:
        time = record['time']
        device_id = record['device_id']
        
        if time not in device_states_by_time:
            device_states_by_time[time] = {}
        
        # Remove extra attributes if needed
        device_state = query_elk_2.remove_extra_record_attributes(record)
        
        device_states_by_time[time][device_id] = device_state
    
    return device_states_by_time
