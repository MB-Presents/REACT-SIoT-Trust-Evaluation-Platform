import pandas as pd
from preprocessing.data_preprocessing import preprocess_devices, preprocess_devices_features, preprocess_relationships, get_node_features
from feature_engineering.feature_engineering import get_negative_edges, set_positive_edge_labels
from dataset_generation.dataset_generation import generate_node_classification_dataset, generate_edge_prediction_dataset, generate_subgraph_classification_dataset

import config


import cProfile
import pickle

from dataset_builder.utils.path_helper import DatasetTask, DatasetType, get_dataset_file_path, get_profiler_output_path, set_constants

def main():
    
    df_devices = df_device_features = pd.read_csv(config.DEVICES_PATH)
    
    df_devices  = preprocess_devices(df_devices)
    df_device_features = preprocess_devices_features(df_device_features)
    df_node_features = get_node_features(df_device_features)
    
    
    df_node_features.to_csv(config.OUT_NODE_RAW_DF)
    
    df_relaionships = pd.read_csv(config.RELATIONSHIPS_PATH)
    df_relaionships = preprocess_relationships(df_relaionships)
    
    df_relaionships.to_csv(config.OUT_RELATION_RAW_DF)

    # Preprocess data

    if config.DATASET_OPTION == 'node_classification':
        
        DATASET_TYPE = DatasetType.NODE_CLASSIFICATION_SITUATION_LABELS.value
        DATASET_TASK = DatasetTask.NODE_CLASSIFICATION.value

        set_constants(DATASET_TYPE, DATASET_TASK)
        
        node_classification_dataset_situation = generate_node_classification_dataset(df_devices, 'situation')
        
        
        output_name = get_dataset_file_path(config.dataset_type, config.BUILD_DEVICE, config.DATASET_OPTION)
               
        node_classification_dataset_situation.to_csv(config.OUT_NODE_CLASSIFICATION_SITUATION_DF)

        # Generate dataset based on distance
        node_classification_dataset_distance = generate_node_classification_dataset(df_devices, 'distance')
        
        
        output_name = get_dataset_file_path(config.dataset_type, config.BUILD_DEVICE, config.DATASET_OPTION)
               
        node_classification_dataset_distance.to_csv(config.OUT_NODE_CLASSIFICATION_DISTANCE_DF)
        return

    if config.DATASET_OPTION == 'edge_prediction':
        
        DATASET_TYPE = DatasetType.LINK_PREDICTION_DISTANCE_LABELS.value
        DATASET_TASK = DatasetTask.LINK_PREDICTION.value

        set_constants(DATASET_TYPE, DATASET_TASK)
        

        df_relaionships = set_positive_edge_labels(df_relaionships)
        negative_samples_df = get_negative_edges(df_device_features, df_relaionships)

        edge_prediction_dataset = generate_edge_prediction_dataset(df_relaionships, negative_samples_df, df_devices, df_node_features)        
        
        output_name = get_dataset_file_path()
               
        
        edge_prediction_dataset.to_csv(output_name)

    
    elif config.DATASET_OPTION == 'subgraph_classification':
        
        DATASET_TASK = DatasetTask.SUBGRAPH_CLASSIFICATION.value
        DATASET_TYPE = DatasetType.SUBGRAPH_CLASSIFICATION_DISTANCE_LABELS.value
        set_constants(DATASET_TYPE, DATASET_TASK)
        
        subgraph_classification_dataset = generate_subgraph_classification_dataset(df_devices, df_relaionships)
        
        output_name = get_dataset_file_path()
        
        
        with open(output_name, 'wb') as f:
            pickle.dump(subgraph_classification_dataset, f)
            

# if __name__ == "__main__":
#     main()



if __name__ == "__main__":
    
    output_profiler = get_profiler_output_path()
    
    try:
        cProfile.run('main()', str(output_profiler.joinpath("output.dat")))
    
    finally:
        
        import pstats
        from pstats import SortKey
        
        with open(str(output_profiler.joinpath("output_time.txt")), "w") as f:
            p = pstats.Stats(str(output_profiler.joinpath("output.dat")), stream=f)
            p.sort_stats("time").print_stats()

        with open(str(output_profiler.joinpath("output_calls.txt")), "w") as f:
            p = pstats.Stats(str(output_profiler.joinpath("output.dat")), stream=f)
            p.sort_stats("calls").print_stats()

        with open(str(output_profiler.joinpath("output_cumulative_times.txt")), "w") as f:
            p = pstats.Stats(str(output_profiler.joinpath("output.dat")), stream=f)
            p.sort_stats(SortKey.CUMULATIVE).print_stats()

