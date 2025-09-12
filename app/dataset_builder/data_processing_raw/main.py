

import cProfile
import sys
sys.path.insert(0, '/app')




from pandas import DataFrame
import dataset_builder.data_processing_raw.data_processing.data_access as data_access
import dataset_builder.data_processing_raw.data_processing.preprocessing as preprocessor
import dataset_builder.data_processing_raw.feature_engineering as feature_engineering
from dataset_builder.data_processing_raw.utils import get_device_mapping

import pandas as pd

import dataset_builder.data_processing_raw.validation as validation
from dataset_builder.utils.path_helper import DatasetType, get_profiler_output_path, get_raw_dataset_directory_path


BUILD_DEVICE='local'


def main():
    df_events = data_access.get_events()
    df_reports = data_access.get_reports()
    max_time = data_access.get_max_time()

    df_events = preprocessor.get_event_dataframe(df_events, df_reports)
    df_events_labels = preprocessor.get_event_labels(df_events, max_time)

    start_time = 0
    device_mapping = {}


    df_devices_timeseries = []  
    df_relationships_timeseries = []  

    device_mapping = {}


    devices = data_access.get_device_states_batch(start_time, end_time=max_time)
    
    print("All devices fetched")
    
    for time in range(start_time, max_time):
        print(f"Time: {time}")

        # devices_candidates = data_access.get_device_states(time)
        devices_candidates = devices[time]
        
        device_mapping = get_device_mapping(device_mapping, devices_candidates)
        
        df_devices = feature_engineering.get_df_devices(devices_candidates, device_mapping)
        labels = feature_engineering.get_target_labels(df_events_labels, df_devices, time)
        
        df_devices = feature_engineering.encode_node_features(df_devices,labels)


        df_devices['time'] = time
        df_devices_timeseries.append(df_devices)

        df_relationships = feature_engineering.get_relationships(df_devices)
        df_relationships['time'] = time
        df_relationships_timeseries.append(df_relationships)
        

    df_device_output : DataFrame = preprocessor.get_df_device_output(df_devices_timeseries)
    df_relationships_output : DataFrame = preprocessor.get_df_relationship_output(df_relationships_timeseries)

    df_device_output_time = df_device_output[df_device_output['time'] == 150]

    if validation.is_all_checked(df_device_output, df_relationships_output):
        print("All checked")


    

    output_directory = get_raw_dataset_directory_path(BUILD_DEVICE)

    df_device_output.to_pickle(output_directory.joinpath("df_devices.pkl"))
    df_relationships_output.to_pickle(output_directory.joinpath("df_relationships.pkl"))

    df_device_output.to_csv(output_directory.joinpath("devices.csv"), index=False)
    df_relationships_output.to_csv(output_directory.joinpath("relationships.csv"), index=False)


    




if __name__ == "__main__":
    
    
    dataset_type = DatasetType.RAW_DATASET.value
    
    output_profiler = get_profiler_output_path(dataset_type,BUILD_DEVICE)
    
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

