# %%
import sys

from dataset_builder.data_processing.subgraph_extraction.dataset_creation_subgraph import encode_categorial_device_features
from dataset_builder.data_processing_raw.models import SituationClasses
from dataset_builder.data_processing_raw.utils import get_events_in_time, is_event_nearby
sys.path.insert(0, '/app')


import pandas as pd
from torch import Tensor


import numpy as np
from pandas import DataFrame
import torch

from sklearn.preprocessing import OneHotEncoder
from core.models.devices.common import DeviceInternalStatus, DeviceShapeStatus, DeviceType



def one_hot_encode_features(df, features, categories):
    """One-hot encode specified features in the DataFrame."""
    encoder = OneHotEncoder(sparse_output=False, categories=categories)
    feature_values = [df[feature].values.reshape(-1, 1) for feature in features]
    encoded_data = encoder.fit_transform(np.hstack(feature_values))
    column_names = encoder.get_feature_names_out(features)
    return pd.DataFrame(encoded_data, index=df.index, columns=column_names)

def clean_up_dataframe(df):
    """Clean up and rearrange the DataFrame."""
    df['color'] = df['color'].replace({None: np.nan, '': np.nan})
    ordered_columns = ['device_id', 'time', 'situation_label', 'longitude', 'latitude'] + \
                      [col for col in df.columns if col not in ['device_id', 'time', 'situation_label', 'longitude', 'latitude']]
    return df[ordered_columns]

def encode_node_features(df_devices, labels):
    """Encode node features and labels into the DataFrame."""
    df_devices['situation_label'] = labels[:, 0]
    
    # One-hot encode categorical features
    categories = [
        [e.name for e in DeviceType],
        [e.name for e in DeviceShapeStatus],
        [e.name for e in DeviceInternalStatus]
    ]
    df_encoded = one_hot_encode_features(df_devices, ['type', 'shape_status', 'status'], categories)
    
    # Concatenate the original DataFrame and the encoded DataFrame
    df_devices = pd.concat([df_devices, df_encoded], axis=1)
    
    # Clean up the DataFrame
    df_devices = df_devices.drop(columns=['position', 'shape_status', 'type', 'object_type', 'status'])
    df_devices = clean_up_dataframe(df_devices)
    
    return df_devices


# def encode_categorial_device_features(df_devices):
#     device_type_list = [e.name for e in DeviceType]
#     device_shape_status_list = [e.name for e in DeviceShapeStatus]
#     device_status = [e.name for e in DeviceInternalStatus]
    
#     encoder : OneHotEncoder = OneHotEncoder(sparse_output=False, categories=[device_type_list, device_shape_status_list,device_status])

#     object_type = df_devices['type'].values.reshape(-1, 1)
#     state = df_devices['shape_status'].values.reshape(-1, 1)
#     device_status = df_devices['status'].values.reshape(-1, 1)
    
    
#     encoded_data = encoder.fit_transform(np.hstack((object_type, state, device_status)))
#     df_encoded = pd.DataFrame(encoded_data, index=df_devices.index, columns=encoder.get_feature_names_out(['type', 'shape_status','status']))
    
#     return df_encoded


# def encode_node_features(df_devices,labels):
    
#     df_devices['situation_label'] = labels[:, 0]
#     df_encoded = encode_categorial_device_features(df_devices)
#     df_devices = pd.concat([df_devices, df_encoded], axis=1)

#     if len(df_encoded.index) != len(df_devices.index):
#         print(f"ERROR: len(df_encoded.index) != len(df_devices.index); len(df_encoded.index) {len(df_encoded.index)}, len(df_devices.index) {len(df_devices.index)}")

#     if len(df_devices.index) != len(df_devices.index):
#         print(f"ERROR: len(df_devices_tensor.index) != len(df_devices.index); len(df_devices_tensor.index) {len(df_devices.index)}, len(df_devices.index) {len(df_devices.index)}")
    
#     df_devices = df_devices.drop(columns=['position','shape_status','type','object_type','status'])
#     df_devices['color'] = df_devices['color'].replace({None: np.nan, '': np.nan})

#     columns_order = ['device_id', 'time', 'situation_label', 'longitude', 'latitude'] + [col for col in df_devices.columns if col not in ['device_id', 'time', 'situation_label', 'longitude', 'latitude']]
#     df_devices = df_devices[columns_order]

#     return df_devices

def get_target_labels(df_events, df_device, time):
    events_at_time = get_events_in_time(df_events, time)
    
    num_classes = 1
    numpy_array = np.zeros((len(df_device), num_classes), dtype=np.int64)
    
    accident_objects = events_at_time['object_of_interest'].to_list()
    
    if not events_at_time.empty:
        device_objects = df_device['device_id_initial'].to_list()
        
        for i, device_object in enumerate(device_objects):
            if device_object in accident_objects:
                numpy_array[i, 0] = 1
    
    return numpy_array


# def get_target_labels(df_events, df_device, time):
#     events_at_time = get_events_in_time(df_events, time)
    
#     # Initialize the result array
#     num_classes = 1
#     numpy_array = np.zeros((len(df_device), num_classes), dtype=np.int64)
    
#     accident_objects = events_at_time['object_of_interest'].to_list()
    
#     if not events_at_time.empty:
#         # Convert the 'position' column to a 2D NumPy array
#         event_coords = np.array(events_at_time['position'].tolist())
#         device_coords = np.array(df_device['position'].tolist())
        
#         # Create a KD-Tree for events
#         tree = cKDTree(event_coords)
        
#         # Query the KD-Tree to find all events within a distance of 50 for each device
#         distances, indices = tree.query(device_coords, distance_upper_bound=50)
        
#         # Update the result array based on the query results
#         numpy_array[distances < 50, 0] = 1
    
#     return numpy_array

    
# def get_target_labels(df_events, df_device, time):
#     events_at_time = get_events_in_time(df_events, time)
#     num_classes = len(SituationClasses)
#     num_classes = 1

#     empty_tensor = torch.zeros(len(df_device),dtype=torch.long) 
#     numpy_array = np.zeros((len(df_device), num_classes), dtype=np.int64)

#     for device_index, (_, device) in enumerate(df_device.iterrows()):
#         classified_event_classes = []

#         for _, event in events_at_time.iterrows():
#             if is_event_nearby(device, event['position'], radius=50.0):
#                 classification = SituationClasses.AUTHENTIC_COLLISION
#                 classified_event_classes.append(classification)
#                 empty_tensor[device_index] = 1
#                 numpy_array[device_index][0] = 1

#         if len(classified_event_classes) == 0:
#             classified_event_classes.append(SituationClasses.OTHER_SITUATION)
#             empty_tensor[device_index] = 0
#             numpy_array[device_index][0] = 0


#     return numpy_array  


# def relationship_attr_tensor(df_relationships):
#     df_distance = df_relationships.drop(['origin_device_id', 'target_device_id'], axis=1)
    
#     is_distance_big_as_50 = df_distance['distance'] > 50
    
#     if is_distance_big_as_50.any():
#         print(f"Distance is bigger than 50: {df_distance[is_distance_big_as_50]}")
    
#     edge_attr_tensor = torch.tensor(df_distance.values.astype(np.float32))
#     return edge_attr_tensor





def remove_device_features(df_devices):
    all_cols = df_devices.columns.tolist()
    cols_to_drop = ['signal','index','time','device_id','color','position','object_type','type', 'shape_status','status']    
    cols_to_drop = list(set(cols_to_drop) & set(all_cols))
        
    df_devices_drop = df_devices.drop(columns=cols_to_drop,axis=1)
    return df_devices_drop





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




from scipy.spatial import cKDTree
import pandas as pd
import numpy as np

def get_relationships(df_devices: pd.DataFrame):
    # Create a NumPy array from the DataFrame
    coords = df_devices[['longitude', 'latitude']].to_numpy()
    
    # Create a KD-Tree
    tree = cKDTree(coords)
    
    # Query the KD-Tree to find all points within a distance of 50 for each point
    pairs = tree.query_pairs(50)
    
    relationships = []
    for i, j in pairs:
        origin_device = df_devices.iloc[i]
        target_device = df_devices.iloc[j]
        
        scene_position = coords[i]
        device_position = coords[j]
        
        distance = np.linalg.norm(scene_position - device_position)
        
        scene_index = origin_device["device_id"]
        device_index = target_device["device_id"]
        
        distance = round(distance, 2)
        relationships.append((scene_index, device_index, distance))
        
    df_relationships = pd.DataFrame(relationships, columns=["origin_device_id", "target_device_id", "distance"])
    
    df_relationships['origin_device_id'] = df_relationships['origin_device_id'].astype(int)
    df_relationships['target_device_id'] = df_relationships['target_device_id'].astype(int)
    
    df_relationships.sort_index(inplace=True)
    
    return df_relationships



# def get_relationships(df_devices: pd.DataFrame):
#     relationships = []

#     for i, origin_device in df_devices.iterrows():
#         scene_position = np.array([origin_device["longitude"], origin_device["latitude"]])

#         for j, target_device in df_devices.iterrows():
            
#             device_position = np.array([target_device["longitude"], target_device["latitude"]])
#             distance = np.linalg.norm(scene_position - device_position)

#             if distance < 50:  # Approximately 50m in degrees
#                 scene_index = origin_device["device_id"]
#                 device_index = target_device["device_id"]

#                 distance = round(distance, 2)
#                 relationships.append((scene_index, device_index, distance))

#     df_relationships = pd.DataFrame(relationships, columns=["origin_device_id", "target_device_id", "distance"])

#     df_relationships['origin_device_id'] = df_relationships['origin_device_id'].astype(int)
#     df_relationships['target_device_id'] = df_relationships['target_device_id'].astype(int)

#     df_relationships.sort_index(inplace=True)

#     return df_relationships


# def get_df_devices(devices : dict, device_mapping : dict) -> DataFrame:
    
#     list_of_dicts = [{**v, 'device_id': k} for k, v in devices.items()]

#     df_devices = pd.DataFrame(list_of_dicts)
    
#     cols_to_keep = ['position','device_id', 'time', 'object_type', 'speed', 'color','shape_status','status','signal','type']
#     all_cols = df_devices.columns.tolist()
#     cols_to_drop = list(set(all_cols) - set(cols_to_keep))

#     df_devices = df_devices.drop(columns=cols_to_drop)
        
#     df_devices[['longitude', 'latitude']] = pd.DataFrame(df_devices['position'].to_list(), index=df_devices.index)
#     df_devices['longitude'] = df_devices['longitude'].round(2)
#     df_devices['latitude'] = df_devices['latitude'].round(2)
#     df_devices['position'] = list(zip(df_devices['longitude'], df_devices['latitude']))
#     df_devices['device_id_initial'] = df_devices['device_id']
#     df_devices['device_id'] = df_devices['device_id'].map(device_mapping)
    
#     df_devices.sort_index()
    
#     return df_devices

def get_df_devices(devices: dict, device_mapping: dict) -> pd.DataFrame:
    
    # Create DataFrame
    list_of_dicts = [{**v, 'device_id': k} for k, v in devices.items()]
    df_devices = pd.DataFrame(list_of_dicts)
    
    # Keep only necessary columns that are present in the DataFrame
    cols_to_keep = ['position', 'device_id', 'time', 'object_type', 'speed', 'color', 'shape_status', 'status', 'signal', 'type']
    cols_to_keep = list(set(cols_to_keep).intersection(set(df_devices.columns)))
    df_devices = df_devices[cols_to_keep]
    
    # Split 'position' into 'longitude' and 'latitude'
    df_devices[['longitude', 'latitude']] = pd.DataFrame(df_devices['position'].to_list(), index=df_devices.index)
    
    # Round coordinates to 2 decimal places and create a new 'position' column
    df_devices['longitude'] = df_devices['longitude'].round(2)
    df_devices['latitude'] = df_devices['latitude'].round(2)
    df_devices['position'] = list(zip(df_devices['longitude'], df_devices['latitude']))
    
    # Map 'device_id' and create 'device_id_initial'
    df_devices['device_id_initial'] = df_devices['device_id']
    df_devices['device_id'] = df_devices['device_id'].map(device_mapping)
    
    return df_devices


