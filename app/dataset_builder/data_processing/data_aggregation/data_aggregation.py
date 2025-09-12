
import pandas as pd


def combine_devices_features_and_relationships(devices_df, relationships_df):
    
    
    node_feature_cols = devices_df.columns.difference(['u', 'ts', 'label']).tolist()
    combined_df = pd.merge(relationships_df, devices_df, how='left', left_on=['u', 'ts'], right_on=['u', 'ts'], suffixes=('', '_src'))

    target_labels = pd.merge(relationships_df, devices_df[['u', 'ts', 'label']], how='left', left_on=['i', 'ts'], right_on=['u', 'ts'])
    combined_df['target_label'] = target_labels['label']

    # TODO: ISSUE WITH LENGTH OF EDGES
    combined_df['dist'] = relationships_df['dist'].values
    return combined_df
