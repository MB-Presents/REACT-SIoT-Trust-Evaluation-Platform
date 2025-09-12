# %%
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from scipy.spatial import distance
# %%
def preprocess_devices(df_devices):
    # Load the CSV

    
    # Extract the required columns
    u_list = df_devices['device_id'].tolist()
    ts_list = df_devices['time'].tolist()
    label_list = df_devices['situation_label'].tolist()
    
    return pd.DataFrame({'u': u_list,
                         'ts': ts_list,
                         'label': label_list})

def preprocess_relationships(df_relationships):

    u_list = df_relationships['origin_device_id'].tolist()
    i_list = df_relationships['target_device_id'].tolist()
    ts_list = df_relationships['time'].tolist()
    distance_list = df_relationships['distance'].tolist()
    label = df_relationships['post_label'].tolist()
    return pd.DataFrame({'u': u_list,
                         'i': i_list,
                         'ts': ts_list,
                         'distance': distance_list,
                         'post_label': label})
    
def get_negative_edges(devices_df, relationships_df):
    all_candidate_negative_pairs = []

    unique_timestamps = devices_df['time'].unique()

    for ts in unique_timestamps:
        devices_at_ts = devices_df[devices_df['time'] == ts]
        coords = devices_at_ts[['longitude', 'latitude']].values
        distances = distance.cdist(coords, coords)
        
        max_num_negative_edges, j_big = np.where((distances > 50))
        num_positive_edges, j_small = np.where((distances <= 50))

        num_negative_pairs = min(len(max_num_negative_edges), len(num_positive_edges))
        selected_indices = np.random.choice(range(len(max_num_negative_edges)), num_negative_pairs, replace=False)

        selected_i_big = max_num_negative_edges[selected_indices]
        selected_j_big = j_big[selected_indices]

        pairs = pd.DataFrame(np.column_stack([selected_i_big, selected_j_big, distances[selected_i_big, selected_j_big]])).drop_duplicates().values
        pairs_df = pd.DataFrame(pairs, columns=['src_idx', 'tgt_idx', 'dist'])
        
        pairs_df = pairs_df.join(devices_at_ts[['device_id']].reset_index(), how='left', on='src_idx', lsuffix='_pairs', rsuffix='_devices')
        pairs_df.rename(columns={'device_id': 'src_device_id'}, inplace=True)

        pairs_df = pairs_df.join(devices_at_ts[['device_id']].reset_index(), how='left', on='tgt_idx', lsuffix='_pairs', rsuffix='_devices')
        pairs_df.rename(columns={'device_id': 'tgt_device_id'}, inplace=True)

        pairs_df['time'] = ts
        all_candidate_negative_pairs.extend(pairs_df[['time', 'src_device_id', 'tgt_device_id', 'dist']].values.tolist())
        
        print(f'Time: {ts}, Num negative pairs: {len(pairs_df)}')
        

    # Convert to DataFrame for easier filtering
    all_candidate_negative_pairs_df = pd.DataFrame(all_candidate_negative_pairs, columns=['time', 'src_device_id', 'tgt_device_id', 'distance'])

    # Create a set of tuples representing existing relationships
    existing_relationships = set(
        relationships_df.apply(lambda row: (row['time'], row['origin_device_id'], row['target_device_id']), axis=1)
    )

    # Filter out rows that are already in relationships_df
    filtered_negative_pairs = [
        row for row in all_candidate_negative_pairs if (row[0], row[1], row[2]) not in existing_relationships
    ]

    negative_samples_df = pd.DataFrame(filtered_negative_pairs, columns=['time', 'origin_device_id', 'target_device_id', 'distance'])
    negative_samples_df['post_label'] = -1

    print(f"Generate Negative edges: negative_samples_df.shape: {negative_samples_df.shape}")
    
    return negative_samples_df

def get_node_features(devices_df):
    node_feature_cols = devices_df.columns.difference(['device_id', 'time', 'situation_label', 'color', 'device_id_initial']).tolist()
    node_feature_cols_2 = devices_df.columns.difference(['situation_label', 'color', 'device_id_initial']).tolist()

    df_node_features = devices_df[node_feature_cols_2]
    df_node_features['signal'].fillna(0, inplace=True)
    node_features = df_node_features[node_feature_cols].values
    return df_node_features
    
def merge_dataframes_to_dict(df_combined_dict, df_node_features):
    """
    Convert two dataframes to dictionaries and merge them based on keys.

    Parameters:
    - df1: The main dataframe (combined_df in your context).
    - df2: The second dataframe (df_node_features in your context).

    Returns:
    - A dictionary with merged data.
    """

    node_feature_dict = {(row['device_id'], row['time']): row.to_dict() for _, row in df_node_features.iterrows()}

    result_dict = {(row['u'], row['ts']): row.to_dict() for _, row in df_combined_dict.iterrows()}

    # Iterate over df1_dict to merge with df2_dict
    for key, value in result_dict.items():
        if key in node_feature_dict:
            
            del node_feature_dict[key]['device_id']
            del node_feature_dict[key]['time']
            
            for feature_key, feature_value in node_feature_dict[key].items():
                result_dict[key][feature_key] = feature_value
        elif key not in node_feature_dict:
            print(f"Key {key} not in node_feature_dict") 

    return result_dict


def set_positive_edge_labels(relationships_df):
    relationships_df['post_label'] = 1
    return relationships_df


def aggregate_edges(relationships_df, negative_samples_df):
    relationships_df = pd.concat([relationships_df, negative_samples_df])
    relationships_df = relationships_df.sort_values(by=['time', 'origin_device_id', 'target_device_id', 'distance'])
    print(f"Combine positive and negative egdes: relationships_df.shape: {relationships_df.shape}")
    return relationships_df



def combine_devices_features_and_relationships(devices_df, relationships_df):
    
    
    node_feature_cols = devices_df.columns.difference(['u', 'ts', 'label']).tolist()
    combined_df = pd.merge(relationships_df, devices_df, how='left', left_on=['u', 'ts'], right_on=['u', 'ts'], suffixes=('', '_src'))

    target_labels = pd.merge(relationships_df, devices_df[['u', 'ts', 'label']], how='left', left_on=['i', 'ts'], right_on=['u', 'ts'])
    combined_df['target_label'] = target_labels['label']

    # TODO: ISSUE WITH LENGTH OF EDGES
    combined_df['distance'] = relationships_df['distance'].values
    return combined_df



data_name = 'iot-unsw'
DATA_DIR = '/app/tgn/data'
DATA_DIR_OUTPUT = os.path.join(DATA_DIR, 'iot-unsw-2')

Path(DATA_DIR_OUTPUT).mkdir(parents=True, exist_ok=True)

DEVICES_PATH = os.path.join(DATA_DIR, 'devices.csv')
RELATIONSHIPS_PATH = os.path.join(DATA_DIR, 'relationships.csv')

OUT_RELATION_DF = os.path.join(DATA_DIR_OUTPUT, 'ml_{}_edges.csv'.format(data_name))
OUT_NODE_DF = os.path.join(DATA_DIR_OUTPUT, 'ml_{}_nodes.csv'.format(data_name))
OUT_FEAT = os.path.join(DATA_DIR_OUTPUT, 'ml_{}_edge_features.npy'.format(data_name))
OUT_NODE_FEAT = os.path.join(DATA_DIR_OUTPUT, 'ml_{}_node_features.npy'.format(data_name))
OUT_DATASET = os.path.join(DATA_DIR_OUTPUT, 'ml_{}.csv'.format(data_name))

devices_df = pd.read_csv(DEVICES_PATH)
relationships_df = relationships_df_edge_feature = pd.read_csv(RELATIONSHIPS_PATH)

df_node_features = get_node_features(devices_df)
edge_features = relationships_df_edge_feature[['distance']].values

relationships_df = set_positive_edge_labels(relationships_df)
negative_samples_df = get_negative_edges(devices_df, relationships_df)

relationships_df = aggregate_edges(relationships_df, negative_samples_df)

devices_df = preprocess_devices(devices_df)
devices_df.to_csv(OUT_NODE_DF)

relationships_df = preprocess_relationships(relationships_df)
relationships_df.to_csv(OUT_RELATION_DF)


df_interaction_events = combine_devices_features_and_relationships(devices_df, relationships_df)
interaction_events_dict = merge_dataframes_to_dict(df_interaction_events, df_node_features)

result_df = pd.DataFrame.from_dict(interaction_events_dict, orient='index')
result_df.reset_index(inplace=True)
result_df.rename(columns={'index': 'key'}, inplace=True)
result_df.to_csv(OUT_DATASET)
