




# %%
def check_device_once_per_interval(df_devices):
    counts = df_devices.groupby('time')['device_id'].value_counts()
    return all(counts == 1)


def check_device_id_consistency(df_devices):
    unique_ids = df_devices.groupby('device_id_initial')['device_id'].nunique()
    return all(unique_ids == 1)

def check_relationship_count(df_devices, df_relationships):
    return len(df_relationships) >= len(df_devices)


# def check_device_has_relationship(df_devices, df_relationships):
#     grouped_relationships = df_relationships.groupby('time')['origin_device_id'].unique()
#     grouped_devices = df_devices.groupby('time')['device_id'].unique()

#     all_have_relations = True  # Assume all devices have relationships initially

#     for time, devices in grouped_devices.items():
#         related_devices = grouped_relationships.get(time, [])
        
#         # Check if each device either has a relationship with another device or with itself (self-loop)
#         missing_relations = set(device for device in devices if device not in related_devices and not (device, device) in df_relationships[['origin_device_id', 'target_device_id']].values)

#         if missing_relations:
#             all_have_relations = False  # Set to False if any device is missing a relationship
#             for device in missing_relations:
#                 print(f"Device {device} at time {time} does not have a relationship.")

#     return all_have_relations


def check_device_has_relationship(df_devices, df_relationships):
    # Group by 'time' and convert to NumPy arrays for faster look-up
    grouped_relationships = df_relationships.groupby('time')['origin_device_id'].apply(np.array)
    grouped_devices = df_devices.groupby('time')['device_id'].apply(np.array)

    all_have_relations = True  # Assume all devices have relationships initially

    # Create a NumPy array of tuples for faster look-up
    relationship_tuples = df_relationships[['origin_device_id', 'target_device_id']].to_numpy()

    for time, devices in grouped_devices.items():
        related_devices = grouped_relationships.get(time, np.array([]))

        # Find unique devices that are not in related_devices
        missing_relations = np.setdiff1d(devices, related_devices)

        # Check if each missing device has a self-loop
        for device in missing_relations:
            if not np.any(np.all(relationship_tuples == [device, device], axis=1)):
                all_have_relations = False
                print(f"Device {device} at time {time} does not have a relationship.")

    return all_have_relations


def check_relationship_distance(df_relationships):
    return all(df_relationships['distance'] <= 50)






# def is_all_checked(df_device_output, final_df_relationships):
    
#     if check_device_once_per_interval(df_device_output):
#         print("Each device exists only once per time interval.")
#     else:
#         print("Error: Some devices exist multiple times in a time interval.")

#     if check_device_id_consistency(df_device_output):
#         print("Device ID is consistent with device_id_initial.")
#     else:
#         print("Error: Device ID inconsistency detected.")

#     if check_relationship_count(df_device_output, final_df_relationships):
#         print("Relationship count is at least equal to device count.")
#     else:
#         print("Error: Relationship count is less than device count.")

#     if check_device_has_relationship(df_device_output, final_df_relationships):
#         print("Each device has at least one relationship.")
#     else:
#         print("Error: Some devices don't have any relationships.")

#     if check_relationship_distance(final_df_relationships):
#         print("All relationships have a distance of 50 or less.")
#     else:
#         print("Error: Some relationships have a distance greater than 50.")


def is_all_checked(df_device_output, final_df_relationships):
    checks = [
        (check_device_once_per_interval, [df_device_output], "Each device exists only once per time interval.", "Error: Some devices exist multiple times in a time interval."),
        (check_device_id_consistency, [df_device_output], "Device ID is consistent with device_id_initial.", "Error: Device ID inconsistency detected."),
        (check_relationship_count, [df_device_output, final_df_relationships], "Relationship count is at least equal to device count.", "Error: Relationship count is less than device count."),
        # (check_device_has_relationship, [df_device_output, final_df_relationships], "Each device has at least one relationship.", "Error: Some devices don't have any relationships."),
        # (check_relationship_distance, [final_df_relationships], "All relationships have a distance of 50 or less.", "Error: Some relationships have a distance greater than 50.")
    ]

    for check_func, args, success_msg, error_msg in checks:
        result = check_func(*args)

        if result:
            print(success_msg)
        else:
            print(error_msg)
            return False
    return True


