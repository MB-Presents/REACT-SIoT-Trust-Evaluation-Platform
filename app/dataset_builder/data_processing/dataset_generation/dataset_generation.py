# %%
import sys
sys.path.insert(0, '/app')

from networkx import Graph, connected_components
import numpy as np
import pandas as pd


import pandas as pd
from feature_engineering.feature_engineering import aggregate_edges, merge_dataframes_to_dict

from dataset_builder.data_processing.data_aggregation.data_aggregation import combine_devices_features_and_relationships  
import networkx as nx
    


from pandas import DataFrame

def generate_node_classification_dataset(df_devices, label_type):
    
    df_devices.rename(columns={'device_id_initial': 'device_name'}, inplace=True)

    # 'longitude', 'latitude',
    col_to_exclude = ['device_id', 'time', 'situation_label',  'color']
    other_feature_columns = df_devices.columns.difference(col_to_exclude).tolist()
    
    
    
    
    if label_type == 'situation':
        node_features = df_devices[['device_id', 'time', 'situation_label'] + other_feature_columns]

        # device_time = node_features[node_features['time'] == 150]
        
    elif label_type == 'distance':
    
        node_features = df_devices.copy()
        accident_vehicles = node_features[node_features['situation_label'] == 1]

        for index, row in accident_vehicles.iterrows():
            coords_vehicles = node_features[['longitude', 'latitude']].values
            coords_target = np.array([row['longitude'], row['latitude']])
            distances = np.linalg.norm(coords_vehicles - coords_target, axis=1)
            within_radius = distances <= 0.0005  
            node_features.loc[within_radius, 'situation_label'] = 1
    
    return node_features


def generate_edge_prediction_dataset(positive_relationships_df : DataFrame, negative_samples_df : DataFrame, df_devices : DataFrame, df_node_features : DataFrame):
    
    df_relationships = aggregate_edges(positive_relationships_df, negative_samples_df)
    # df_interaction_events = combine_devices_features_and_relationships(df_devices, df_relationships)
    df_interaction_events =  df_relationships
    
    interaction_events_dict = merge_dataframes_to_dict(df_interaction_events, df_node_features)

    result_df = pd.DataFrame.from_dict(interaction_events_dict, orient='index')
    result_df.reset_index(inplace=True,drop=True)
    result_df.rename(columns={'index': 'key'}, inplace=True)
    

    return result_df


def generate_subgraph_classification_dataset(devices_df, relationships_df):
    ts_subgraphs_dict = {}

    for ts, group in relationships_df.groupby('ts'):
        G = nx.Graph()

        # Add nodes
        devices_at_ts = devices_df[devices_df['ts'] == ts]
        for index, row in devices_at_ts.iterrows():
            node_id = row['u']
            node_attrs = row.drop(['ts', 'u']).to_dict()
            G.add_node(node_id, **node_attrs)

        # Add edges
        for index, row in group.iterrows():
            u, v, dist = row['u'], row['i'], row['dist']
            G.add_edge(u, v, dist=dist)

        # Create subgraphs and filter out isolated nodes
        for sg in nx.connected_components(G):
            if len(sg) > 1:  # Remove subgraphs with no relationships (i.e., isolated nodes)
                subgraph = G.subgraph(sg)
                label = 1 if any(data['label'] == 1 for node, data in subgraph.nodes(data=True)) else 0
                subgraph.graph['label'] = label

                if ts not in ts_subgraphs_dict:
                    ts_subgraphs_dict[ts] = []
                ts_subgraphs_dict[ts].append(subgraph)

    return ts_subgraphs_dict
