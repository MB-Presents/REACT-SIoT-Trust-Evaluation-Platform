# %%
import sys
sys.path.insert(0, '/app')


import pandas as pd









def get_event_dataframe(df_events, df_report):
    df_events_triggered = df_events[(df_events['is_authentic']) & (df_events['state'] == 'TRIGGERED')]
    
    df_report_solved = df_report[(df_report['report_status'].isin(['ACCIDENT_SOLVED', 'UNSOLVED', 'IN_PROGRESS'])) & (df_report['report_type'] != 'TraffiCPriorityRequest')]
    df_report_solved['object_of_interest'] = df_report['object_of_interest']

    merged_df = pd.merge(df_events_triggered, df_report_solved, left_on='id', right_on='simulation_event', suffixes=('_event', '_report'), how='inner')

    merged_df['time_x'] = merged_df['time_event'].astype(float).astype(int)
    merged_df['time_y'] = merged_df['time_report'].astype(float).astype(int)

    new_df = merged_df[['id', 'situation_event', 'time_x', 'time_y', 'location','report_status','object_of_interest']]
    new_df.columns = ['event_id', 'event_type', 'start_time', 'end_time', 'position','report_status','object_of_interest']

    return new_df




def get_event_labels(df_events,  max_time):
    df_events_information = df_events


    df_events_information['end_time'] = df_events_information.apply(
        lambda row: row['end_time'] if row['report_status'] == 'ACCIDENT_SOLVED' else max_time, axis=1
    )

    df_events_labels = df_events_information.groupby('event_id').agg({
        'start_time': 'min',
        'end_time': 'min',
        'event_type': 'first',  # assuming event_type is the same for all rows with the same event_id
        'position': 'first',  # assuming position is the same for all rows with the same event_id
        'report_status': 'first',
        'object_of_interest': 'first'
    }).reset_index()

    df_events_labels['position'] = df_events_labels['position'].apply(
        lambda pos: [round(coord, 2) for coord in pos]
    )
    
    return df_events_labels



def get_df_device_output(all_df_devices):
    final_df_devices = pd.concat(all_df_devices, ignore_index=True)
    return final_df_devices




def get_df_relationship_output(all_df_relationships):
    final_df_relationships = pd.concat(all_df_relationships, ignore_index=True)
    columns_order = ['time', 'origin_device_id', 'target_device_id'] + [col for col in final_df_relationships.columns if col not in ['time', 'origin_device_id', 'target_device_id']]
    final_df_relationships = final_df_relationships[columns_order]
    return final_df_relationships


