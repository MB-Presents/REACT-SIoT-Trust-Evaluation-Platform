import torch

_selected_edge_features = [
        'distance',
        'status_PENDING',
        'status_VERIFIED',
        'status_EXPIRED',
        'role_REPORTER',
        'role_SERVICE_PROVIDER',
        'role_RECOMMENDER',
        'transaction_type_DIRECT_TRANSACTION',
        'transaction_type_DIRECT_RECOMMENDATION',
        'transaction_type_INDIRECT_RECOMMENDATION',
        'task_context_EmergencyReport',
        'task_context_TraffiCPriorityRequest',
        # 'last_trust_value',
        # 'last_verified_transaction_id',
        # 'last_verified_transaction_trust_value',
        'degree_of_common_friendship',
        'interaction_frequency',
        # 'last_transaction_id',
        'trust_value',
        # 'prediction',
        # 'transaction_id',
    ]

_selected_trustor_features = [
    'trustor_speed',
    'trustor_type_EMERGENCY_CENTER',
    'trustor_type_VEHICLE',
    'trustor_type_TRAFFIC_CAMERA',
    'trustor_type_INDUCTION_LOOP',
    'trustor_type_SMART_PHONE',
    'trustor_type_TRAFFIC_LIGHT',
    # 'trustor_location',
    # 'trustor_device_id',
    # 'trustor_num_trustworthy_relationships',
    # 'trustor_trustworthy_devices',
    # 'trustor_untrustworthy_devices',
    # 'trustor_num_trustor_transactions',
    # 'trustor_num_trustee_transactions',
    # 'trustor_num_trust_transactions',
    # 'trustor_num_untrustworthy_relationships',
    # 'trustor_position',
    # 'trustor_num_related_devices',
    # 'trustor_signal',
    # 'trustor_sensor_id',
    # 'trustor_observed_street',
    # 'trustor_status_ACTIVE',
    # 'trustor_status_INACTIVE',
    # 'trustor_status_ERROR',
    # 'trustor_record_type_STATUS',
    # 'trustor_record_type_SENSED',
    # 'trustor_shape_status_ORIGINAL_MANUFACTURED',
    # 'trustor_shape_status_DEFORMED'
]

_selected_trustee_features = [
    'trustee_speed',
    'trustee_type_EMERGENCY_CENTER',
    'trustee_type_VEHICLE',
    'trustee_type_TRAFFIC_CAMERA',
    'trustee_type_INDUCTION_LOOP',
    'trustee_type_SMART_PHONE',
    'trustee_type_TRAFFIC_LIGHT',
    # 'trustee_location',
    # 'trustee_trustworthy_devices',
    # 'trustee_untrustworthy_devices',
    # 'trustee_num_trustor_transactions',
    # 'trustee_num_trustee_transactions',
    # 'trustee_num_trust_transactions',
    # 'trustee_position',
    # 'trustee_num_related_devices',
    # 'trustee_device_id',
    # 'trustee_num_trustworthy_relationships',
    # 'trustee_signal',
    # 'trustee_num_untrustworthy_relationships',
    # 'trustee_sensor_id',
    # 'trustee_status_ACTIVE',
    # 'trustee_status_INACTIVE',
    # 'trustee_status_ERROR',
    # 'trustee_record_type_STATUS',
    # 'trustee_record_type_SENSED',
    # 'trustee_shape_status_ORIGINAL_MANUFACTURED',
    # 'trustee_shape_status_DEFORMED'
]

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

num_memory_nodes = 1200

num_node_features = len(_selected_trustor_features) + len(_selected_trustee_features)

# memory_dim = time_dim = embedding_dim = num_node_features
memory_dim      = num_node_features
time_dim        = num_node_features
embedding_dim   = num_node_features


msg_size = len(_selected_edge_features) 





sliding_window_of_events = 10