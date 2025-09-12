# %%
import math
import sys
sys.path.insert(0, '/app')


from typing import Dict
import utils.query_elk_2 as query_elk_2
from torch_geometric.data  import HeteroData
import pandas as pd
from torch import Tensor

import utils.logging as pickle_logger

import numpy as np
from pandas import DataFrame
import torch


from sklearn.preprocessing import OneHotEncoder
from core.models.devices.common import DeviceInternalStatus, DeviceShapeStatus, DeviceType

from enum import Enum, auto
from typing import List, NamedTuple
from core.models.events.simulation_events import EventState, EventType

events = query_elk_2.get_events()
events = query_elk_2.remove_extra_attributes(events)

df_events = pd.DataFrame(events)
df_events

reports = query_elk_2.get_reports()
reports = query_elk_2.remove_extra_attributes(reports)

df_reports = pd.DataFrame(reports)
df_reports


def correlate_dataframes(df_events, df_report):
    df_events_triggered = df_events[(df_events['is_authentic']) & (df_events['state'] == 'TRIGGERED')]
    
    df_report_solved = df_report[(df_report['report_status'].isin(['ACCIDENT_SOLVED', 'UNSOLVED', 'IN_PROGRESS'])) & (df_report['report_type'] != 'TraffiCPriorityRequest')]

    merged_df = pd.merge(df_events_triggered, df_report_solved, left_on='id', right_on='simulation_event', suffixes=('_event', '_report'), how='inner')

    merged_df['time_x'] = merged_df['time_event'].astype(float).astype(int)
    merged_df['time_y'] = merged_df['time_report'].astype(float).astype(int)

    new_df = merged_df[['id', 'situation_event', 'time_x', 'time_y', 'location','report_status']]
    new_df.columns = ['event_id', 'event_type', 'start_time', 'end_time', 'position','report_status']

    return new_df


def get_device_states(time):
    devices_candidates = query_elk_2.get_object_state_at_timestep(time)
    devices = query_elk_2.remove_extra_attributes(devices_candidates)
    devices_candidates = {item['device_id']: item for item in devices}
    return devices_candidates



df_events_information = correlate_dataframes(df_events, df_reports)
df_events_information

max_time = query_elk_2.get_max_time()

df_events_information['end_time'] = df_events_information.apply(
    lambda row: row['end_time'] if row['report_status'] == 'ACCIDENT_SOLVED' else max_time, axis=1
)

df_events_information

df_events_labels = df_events_information.groupby('event_id').agg({
    'start_time': 'min',
    'end_time': 'min',
    'event_type': 'first',  # assuming event_type is the same for all rows with the same event_id
    'position': 'first',  # assuming position is the same for all rows with the same event_id
    'report_status': 'first'
}).reset_index()

df_events_labels

df_events_labels['position'] = df_events_labels['position'].apply(
    lambda pos: [round(coord, 2) for coord in pos]
)

df_events_labels



max_time = query_elk_2.get_max_time()

start_time = 0

device_network_graph : Dict[int, HeteroData] = {}           
device_mapping = {}

class Event(NamedTuple):
    event_id: int
    status: EventState
    event_type: EventType
    event_catalyst: str
    time: float
    coordinates: List[float]
    authenticity: bool

class SituationClasses(Enum):
    
    AUTHENTIC_COLLISION = auto()
    UNAUTHENTIC_COLLISION = auto()
    
    AUTHENTIC_TRAFFIC_LIGHT_PRIORITY_REQUEST = auto()
    UNAUTHENTIC_TRAFFIC_LIGHT_PRIORITY_REQUEST = auto()
    
    OTHER_SITUATION = auto()


def device_feature_tensor(df_devices : DataFrame) -> Tensor:
    
    df_encoded = encode_categorial_device_features(df_devices)
    df_devices = remove_device_features(df_devices)
    
    df_devices_tensor = pd.concat([df_devices, df_encoded], axis=1)
    
    if len(df_encoded.index) != len(df_devices.index):
        print(f"ERROR: len(df_encoded.index) != len(df_devices.index); len(df_encoded.index) {len(df_encoded.index)}, len(df_devices.index) {len(df_devices.index)}")
    
    if len(df_devices_tensor.index) != len(df_devices.index):
        print(f"ERROR: len(df_devices_tensor.index) != len(df_devices.index); len(df_devices_tensor.index) {len(df_devices_tensor.index)}, len(df_devices.index) {len(df_devices.index)}")
    
    
    device_feature_tensor = torch.tensor(df_devices_tensor.values, dtype=torch.long)

    if(torch.isnan(device_feature_tensor).any().item()):
        print(device_feature_tensor)
    
    return device_feature_tensor

def remove_device_features(df_devices):
    all_cols = df_devices.columns.tolist()
    cols_to_drop = ['signal','index','time','device_id','color','position','object_type','type', 'shape_status','status']    
    cols_to_drop = list(set(cols_to_drop) & set(all_cols))
        
    df_devices_drop = df_devices.drop(columns=cols_to_drop,axis=1)
    # df_devices_drop.reset_index(drop=True, inplace=True)
    return df_devices_drop

def encode_categorial_device_features(df_devices):
    device_type_list = [e.name for e in DeviceType]
    device_shape_status_list = [e.name for e in DeviceShapeStatus]
    device_status = [e.name for e in DeviceInternalStatus]
    
    encoder : OneHotEncoder = OneHotEncoder(sparse_output=False, categories=[device_type_list, device_shape_status_list,device_status])

    object_type = df_devices['type'].values.reshape(-1, 1)
    state = df_devices['shape_status'].values.reshape(-1, 1)
    device_status = df_devices['status'].values.reshape(-1, 1)
    
    
    encoded_data = encoder.fit_transform(np.hstack((object_type, state, device_status)))
    df_encoded = pd.DataFrame(encoded_data, index=df_devices.index, columns=encoder.get_feature_names_out(['type', 'shape_status','status']))
    
    return df_encoded


def is_event_nearby(device, coordinates, radius = 50.0):
    
    device_pos = device['position']
    distance = math.dist(device_pos, coordinates)

    if distance <= radius:
        return True
    
    return False

def get_relationships(df_devices: pd.DataFrame):
    relationships = []

    for i, origin_device in df_devices.iterrows():
        scene_position = np.array([origin_device["longitude"], origin_device["latitude"]])

        for j, target_device in df_devices.iterrows():
            
            device_position = np.array([target_device["longitude"], target_device["latitude"]])
            distance = np.linalg.norm(scene_position - device_position)

            if distance < 50:  # Approximately 50m in degrees
                scene_index = origin_device["device_id"]
                device_index = target_device["device_id"]

                distance = round(distance, 2)
                relationships.append((scene_index, device_index, distance))

    df_relationships = pd.DataFrame(relationships, columns=["origin_device_id", "target_device_id", "distance"])

    df_relationships['origin_device_id'] = df_relationships['origin_device_id'].astype(int)
    df_relationships['target_device_id'] = df_relationships['target_device_id'].astype(int)

    df_relationships.sort_index(inplace=True)

    return df_relationships

def get_device_mapping(device_mapping, devices_candidates):
    
    counter = len(device_mapping) + 1
    
    for device_id, device in devices_candidates.items():
        if device_id not in device_mapping:
            
            device_mapping[device_id] = counter
            counter += 1
            
    return device_mapping

def get_df_devices(devices : dict, device_mapping : dict) -> DataFrame:
    
    list_of_dicts = [{**v, 'device_id': k} for k, v in devices.items()]

    df_devices = pd.DataFrame(list_of_dicts)
    
    cols_to_keep = ['position','device_id', 'time', 'object_type', 'speed', 'color','shape_status','status','signal','type']
    all_cols = df_devices.columns.tolist()
    cols_to_drop = list(set(all_cols) - set(cols_to_keep))

    df_devices = df_devices.drop(columns=cols_to_drop)
        
    df_devices[['longitude', 'latitude']] = pd.DataFrame(df_devices['position'].to_list(), index=df_devices.index)
    df_devices['longitude'] = df_devices['longitude'].round(2)
    df_devices['latitude'] = df_devices['latitude'].round(2)
    df_devices['position'] = list(zip(df_devices['longitude'], df_devices['latitude']))
    df_devices['device_id_initial'] = df_devices['device_id']
    df_devices['device_id'] = df_devices['device_id'].map(device_mapping)
    
    df_devices.sort_index()
    
    return df_devices

def relationship_attr_tensor(df_relationships):
    df_distance = df_relationships.drop(['origin_device_id', 'target_device_id'], axis=1)
    
    is_distance_big_as_50 = df_distance['distance'] > 50
    
    if is_distance_big_as_50.any():
        print(f"Distance is bigger than 50: {df_distance[is_distance_big_as_50]}")
    
    edge_attr_tensor = torch.tensor(df_distance.values.astype(np.float32))
    return edge_attr_tensor

    
def get_target_labels(df_events, df_device, time):
    events_at_time = get_events_in_time(df_events, time)
    num_classes = len(SituationClasses)

    empty_tensor = torch.zeros(len(df_device),dtype=torch.long) 

    num_classes = 1
    numpy_array = np.zeros((len(df_device), num_classes), dtype=np.int64)

    for device_index, (_, device) in enumerate(df_device.iterrows()):
        classified_event_classes = []

        for _, event in events_at_time.iterrows():
            if is_event_nearby(device, event['position'], radius=50.0):
                classification = SituationClasses.AUTHENTIC_COLLISION
                classified_event_classes.append(classification)
                empty_tensor[device_index] = 1
                numpy_array[device_index][0] = 1

        if len(classified_event_classes) == 0:
            classified_event_classes.append(SituationClasses.OTHER_SITUATION)
            empty_tensor[device_index] = 0
            numpy_array[device_index][0] = 0


    return numpy_array  

def get_events_in_time(df_events : DataFrame, time):
    return df_events[(df_events.start_time <= time) & (df_events.end_time >= time)]

    
def get_target_labels(df_events, df_device, time):
    events_at_time = get_events_in_time(df_events, time)
    num_classes = len(SituationClasses)

    empty_tensor = torch.zeros(len(df_device),dtype=torch.long) 

    num_classes = 1
    numpy_array = np.zeros((len(df_device), num_classes), dtype=np.int64)

    for device_index, (_, device) in enumerate(df_device.iterrows()):
        classified_event_classes = []

        for _, event in events_at_time.iterrows():
            if is_event_nearby(device, event['position'], radius=50.0):
                classification = SituationClasses.AUTHENTIC_COLLISION
                classified_event_classes.append(classification)
                empty_tensor[device_index] = 1
                numpy_array[device_index][0] = 1

        if len(classified_event_classes) == 0:
            classified_event_classes.append(SituationClasses.OTHER_SITUATION)
            empty_tensor[device_index] = 0
            numpy_array[device_index][0] = 0


    return numpy_array  

def encode_node_features(df_devices,labels):
    
    df_devices['situation_label'] = labels[:, 0]
    df_encoded = encode_categorial_device_features(df_devices)
    df_devices = pd.concat([df_devices, df_encoded], axis=1)

    if len(df_encoded.index) != len(df_devices.index):
        print(f"ERROR: len(df_encoded.index) != len(df_devices.index); len(df_encoded.index) {len(df_encoded.index)}, len(df_devices.index) {len(df_devices.index)}")

    if len(df_devices.index) != len(df_devices.index):
        print(f"ERROR: len(df_devices_tensor.index) != len(df_devices.index); len(df_devices_tensor.index) {len(df_devices.index)}, len(df_devices.index) {len(df_devices.index)}")
    
    df_devices = df_devices.drop(columns=['position','shape_status','type','object_type','status'])
    df_devices['color'] = df_devices['color'].replace({None: np.nan, '': np.nan})

    columns_order = ['device_id', 'time', 'situation_label', 'longitude', 'latitude'] + [col for col in df_devices.columns if col not in ['device_id', 'time', 'situation_label', 'longitude', 'latitude']]
    df_devices = df_devices[columns_order]

    return df_devices

    

# %%


start_time = 0
all_df_devices = []  # List to store dataframes of devices for each time
all_df_relationships = []  # List to store dataframes of relationships for each time

device_mapping = {}

for time in range(start_time, max_time):
    print(f"Time: {time}")

    devices_candidates = get_device_states(time)
    device_mapping = get_device_mapping(device_mapping, devices_candidates)
    df_devices = get_df_devices(devices_candidates, device_mapping)
    
    labels = get_target_labels(df_events_labels, df_devices, time)
    
    df_devices = encode_node_features(df_devices,labels)

    df_devices['time'] = time
    all_df_devices.append(df_devices)

    df_relationships = get_relationships(df_devices)
    df_relationships['time'] = time

    all_df_relationships.append(df_relationships)



final_df_devices = pd.concat(all_df_devices, ignore_index=True)
final_df_relationships = pd.concat(all_df_relationships, ignore_index=True)
columns_order = ['time', 'origin_device_id', 'target_device_id'] + [col for col in final_df_relationships.columns if col not in ['time', 'origin_device_id', 'target_device_id']]
final_df_relationships = final_df_relationships[columns_order]

# Export the dataframes to .pkl files
final_df_devices.to_pickle("df_devices.pkl")
final_df_relationships.to_pickle("df_relationships.pkl")

# %%
def check_device_once_per_interval(df_devices):
    counts = df_devices.groupby('time')['device_id'].value_counts()
    return all(counts == 1)


def check_device_id_consistency(df_devices):
    unique_ids = df_devices.groupby('device_id_initial')['device_id'].nunique()
    return all(unique_ids == 1)

def check_relationship_count(df_devices, df_relationships):
    return len(df_relationships) >= len(df_devices)


def check_device_has_relationship(df_devices, df_relationships):
    grouped_relationships = df_relationships.groupby('time')['origin_device_id'].unique()
    grouped_devices = df_devices.groupby('time')['device_id'].unique()

    all_have_relations = True  # Assume all devices have relationships initially

    for time, devices in grouped_devices.items():
        related_devices = grouped_relationships.get(time, [])
        
        # Check if each device either has a relationship with another device or with itself (self-loop)
        missing_relations = set(device for device in devices if device not in related_devices and not (device, device) in df_relationships[['origin_device_id', 'target_device_id']].values)

        if missing_relations:
            all_have_relations = False  # Set to False if any device is missing a relationship
            for device in missing_relations:
                print(f"Device {device} at time {time} does not have a relationship.")

    return all_have_relations


def check_relationship_distance(df_relationships):
    return all(df_relationships['distance'] <= 50)


if check_device_once_per_interval(final_df_devices):
    print("Each device exists only once per time interval.")
else:
    print("Error: Some devices exist multiple times in a time interval.")

if check_device_id_consistency(final_df_devices):
    print("Device ID is consistent with device_id_initial.")
else:
    print("Error: Device ID inconsistency detected.")

if check_relationship_count(final_df_devices, final_df_relationships):
    print("Relationship count is at least equal to device count.")
else:
    print("Error: Relationship count is less than device count.")

if check_device_has_relationship(final_df_devices, final_df_relationships):
    print("Each device has at least one relationship.")
else:
    print("Error: Some devices don't have any relationships.")

if check_relationship_distance(final_df_relationships):
    print("All relationships have a distance of 50 or less.")
else:
    print("Error: Some relationships have a distance greater than 50.")



# %%
outcome = final_df_devices[final_df_devices['situation_label'] != 0]

# %%
final_df_devices.to_csv("devices.csv",index=False)
final_df_relationships.to_csv("relationships.csv",index=False)

# %%
pickle_logger.write_pickle("device_subgraph_0_200", device_network_graph, directory="output")



