# %%
import numpy as np
import pandas as pd
from scipy.spatial import distance



    
def get_negative_edges(devices_df, relationships_df):
    all_candidate_negative_pairs = []

    unique_timestamps = devices_df['ts'].unique()

    # for ts in unique_timestamps:
    #     devices_at_ts = devices_df[devices_df['ts'] == ts]
    #     coords = devices_at_ts[['longitude', 'latitude']].values
    #     distances = distance.cdist(coords, coords)
        
    #     max_num_negative_edges, j_big = np.where((distances > 50))
          
    #     is_posotive_edge = np.logical_and(distances <= 50, distances > 0)
    #     num_positive_edges, j_small = np.where(is_posotive_edge)

    #     num_negative_pairs = min(len(max_num_negative_edges), len(num_positive_edges))
        
    #     selected_indices = np.random.choice(range(len(max_num_negative_edges)), num_negative_pairs, replace=False)

    #     selected_i_big = max_num_negative_edges[selected_indices]
    #     selected_j_big = j_big[selected_indices]

    #     pairs = pd.DataFrame(np.column_stack([selected_i_big, selected_j_big, distances[selected_i_big, selected_j_big]])).drop_duplicates().values
    #     pairs_df = pd.DataFrame(pairs, columns=['u', 'i', 'dist'])
        
        
    #     pairs_df['ts'] = ts
    #     all_candidate_negative_pairs.extend(pairs_df[['ts', 'u', 'i', 'dist']].values.tolist())
        
    #     print(f'Time: {ts}, Num negative pairs: {len(pairs_df)}, Num positive pairs: {len(num_positive_edges)}')
        
    for ts in unique_timestamps:
        devices_at_ts = devices_df[devices_df['ts'] == ts]
        u_values = devices_at_ts['u'].values  # Extract 'u' values
        coords = devices_at_ts[['longitude', 'latitude']].values
        distances = distance.cdist(coords, coords)

        max_num_negative_edges, j_big = np.where((distances > 50))

        is_positive_edge = np.logical_and(distances <= 50, distances > 0)
        num_positive_edges, j_small = np.where(is_positive_edge)

        num_negative_pairs = min(len(max_num_negative_edges), len(num_positive_edges))

        selected_indices = np.random.choice(range(len(max_num_negative_edges)), num_negative_pairs, replace=False)

        selected_i_big = max_num_negative_edges[selected_indices]
        selected_j_big = j_big[selected_indices]

        # Map indices to 'u' values
        selected_u_big = u_values[selected_i_big]
        selected_u_j_big = u_values[selected_j_big]

        # Filter out pairs where 'u' is 0
        valid_pairs = np.column_stack([selected_u_big, selected_u_j_big, distances[selected_i_big, selected_j_big]])
        valid_pairs = valid_pairs[valid_pairs[:, 0] > 0]
        valid_pairs = valid_pairs[valid_pairs[:, 1] > 0]

        pairs_df = pd.DataFrame(valid_pairs, columns=['u', 'i', 'dist'])
        pairs_df['ts'] = ts
        all_candidate_negative_pairs.extend(pairs_df[['ts', 'u', 'i', 'dist']].values.tolist())


    # Create a set of tuples representing existing relationships
    existing_relationships = set(
        relationships_df.apply(lambda row: (row['ts'], row['u'], row['i']), axis=1)
    )

    filtered_negative_pairs = [
        row for row in all_candidate_negative_pairs if (row[0], row[1], row[2]) not in existing_relationships
    ]

    negative_samples_df = pd.DataFrame(filtered_negative_pairs, columns=['ts', 'u', 'i', 'dist'])
    negative_samples_df['relationship_label'] = -1

    print(f"Generate Negative edges: negative_samples_df.shape: {negative_samples_df.shape}")
    
    return negative_samples_df


    
def merge_dataframes_to_dict(df_interaction_events, df_node_features):
    """
    Convert two dataframes to dictionaries and merge them based on keys.

    Parameters:
    - df1: The main dataframe (combined_df in your context).
    - df2: The second dataframe (df_node_features in your context).

    Returns:
    - A dictionary with merged data.
    """

    node_features = {(row['ts'],row['u']): row.to_dict() for _, row in df_node_features.iterrows()}

    interaction_events = {(row['ts'],row['i']): row.to_dict() for _, row in df_interaction_events.iterrows()}

    # Iterate over df1_dict to merge with df2_dict
    for interaction_id, value in interaction_events.items():
        if interaction_id in node_features:
            
            del node_features[interaction_id]['u']
            del node_features[interaction_id]['ts']
            
            for feature_key, feature_value in node_features[interaction_id].items():
                interaction_events[interaction_id][feature_key] = feature_value
        elif interaction_id not in node_features:
            print(f"Key {interaction_id} not in node feature") 

    return interaction_events


# def merge_dataframes_to_dict(df_interaction_events, df_node_features):
#     # Set 'ts' and 'u' as multi-index for both dataframes
#     df_node_features.set_index(['ts', 'u'], inplace=True)
#     df_interaction_events.set_index(['ts', 'u'], inplace=True)

#     # Merge the dataframes
#     merged_df = df_interaction_events.join(df_node_features, lsuffix='_interaction', rsuffix='_node', how='left')

#     # Drop redundant columns
#     merged_df.drop(columns=['ts_interaction', 'u_interaction'], inplace=True, errors='ignore')
    

#     # Convert the merged dataframe to a dictionary
#     merged_dict = {(idx[0], idx[1]): row.to_dict() for idx, row in merged_df.iterrows()}
#     # merged_df = merged_df.loc[~merged_df.index.duplicated(keep='first')]
#     # merged_dict = merged_df.to_dict(orient='index') 
#     # merged_dict = merged_df.to_dict(orient='index')

#     return merged_dict

# def merge_dataframes_to_dict(df_interaction_events, df_node_features):
#     # Merge the dataframes based on 'ts' and 'label'
#     merged_df = df_interaction_events.merge(df_node_features, left_on=['ts', 'u', 'i'], right_on=['ts', 'u', 'label'], how='left')

#     # Drop redundant columns
#     merged_df.drop(columns=['u_interaction', 'label'], inplace=True, errors='ignore')

#     # Convert the merged dataframe to a dictionary
#     merged_dict = merged_df.to_dict(orient='index')

#     return merged_dict


# def merge_dataframes_to_dict(df_interaction_events, df_node_features):
#     # Set index for df_interaction_events
#     df_interaction_events.set_index(['ts', 'u', 'i'], inplace=True)
#     df_node_features.set_index(['ts', 'u', 'label'], inplace=True)

#     # Merge the dataframes based on indices using .merge()
#     merged_df = df_interaction_events.merge(df_node_features, on=['ts', 'u'], how='left', suffixes=('_interaction', '_node'))


#     # Convert the merged dataframe to a dictionary
#     merged_dict = merged_df.to_dict(orient='index')

#     # Reset index to convert index columns back to regular columns
#     merged_df.reset_index(inplace=True)

#     # Rename the index columns to the desired names
#     merged_df.rename(columns={'ts': 'level_0', 'u': 'level_1', 'i': 'level_2', 'label': 'level_3'}, inplace=True)

#     return merged_dict




def set_positive_edge_labels(relationships_df):
    relationships_df['relationship_label'] = 1
    return relationships_df


def aggregate_edges(relationships_df, negative_samples_df):
    relationships_df = pd.concat([relationships_df, negative_samples_df])
    relationships_df = relationships_df.sort_values(by=['ts', 'u', 'i', 'dist'])
    print(f"Combine positive and negative egdes: relationships_df.shape: {relationships_df.shape}")
    return relationships_df



