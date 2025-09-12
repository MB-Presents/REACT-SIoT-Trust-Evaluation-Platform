# %%
import pandas as pd


# %%
def preprocess_devices(df_devices):
    # Load the CSV

    
    # Extract the required columns
    u_list = df_devices['device_id'].tolist()
    ts_list = df_devices['time'].tolist()
    label_list = df_devices['situation_label'].tolist()
    
    return pd.DataFrame({
                        'ts': ts_list,
                        'u': u_list,
                        'label': label_list
    })

def preprocess_devices_features(df_devices):
    df_copy = df_devices.rename(columns={
        'time': 'ts',
        'device_id': 'u',
        'situation_label': 'label'
    })
    return df_copy


def preprocess_relationships(df_relationships):

    u_list = df_relationships['origin_device_id'].tolist()
    i_list = df_relationships['target_device_id'].tolist()
    ts_list = df_relationships['time'].tolist()
    distance_list = df_relationships['distance'].tolist()
    # label = df_relationships['post_label'].tolist()
    return pd.DataFrame({'u': u_list,
                         'i': i_list,
                         'ts': ts_list,
                         'dist': distance_list,
                        #  'relationship_label': label
                         })
    
def get_node_features(devices_df):
    
    node_feature_cols = devices_df.columns.difference(['situation_label', 'color', 'device_id_initial']).tolist()

    df_node_features = devices_df[node_feature_cols]
    df_node_features['signal'].fillna(0, inplace=True)
    
    reordered_columns = ['ts', 'u', 'label'] + [col for col in df_node_features.columns if col not in ['ts', 'u', 'label']]
    df_node_features = df_node_features[reordered_columns]
    df_node_features.sort_values(by=['ts', 'u', 'label'], inplace=True)
    
    
    
    return df_node_features

def get_edge_features(relationships_df_edge_feature):
    edge_features = relationships_df_edge_feature[['distance']].values
    return edge_features
    


