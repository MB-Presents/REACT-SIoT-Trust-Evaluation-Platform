


from __future__ import annotations
from typing import TYPE_CHECKING


import sys
import os
project_root = os.getenv("RESEARCH_PROJECT_ROOT", default="/app")
sys.path.insert(0, project_root)
import numpy as np

from sklearn.preprocessing import OneHotEncoder

from core.models.devices.common import DeviceBehaviour, DeviceInternalStatus, DeviceRecordType, DeviceShapeStatus
from core.models.uniform.components.report_models import ReportType
from trust.data_models.TrustVerifierRoles import TrustVerfierRoles
from trust.data_models.transaction.data_models.abstract_transaction import AbstractTransaction
from trust.data_models.transaction.data_models.direct_recommendation import DirectRecommendation
from trust.data_models.transaction.status import TransactionStatus
from trust.data_models.transaction.type import TransactionType


from trust.situation_recognition_module.situation_recognition import SituationSettings

from pandas import DataFrame
import pandas as pd






from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from scipy.spatial import distance


from trust.data_models.TrustVerifierRoles import TrustVerfierRoles
from pandas import DataFrame
from core.models.devices.common import DeviceBehaviour, DeviceInternalStatus, DeviceRecordType, DeviceShapeStatus, DeviceType


from trust.data_models.transaction.status import TransactionStatus
from trust.data_models.transaction.transaction_controller import TransactionType
from trust.situation_recognition_module.situation_recognition import SituationSettings




if TYPE_CHECKING:

    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.uniform.components.report import SendingPacket
    from trust.situation_recognition_module.situation_recognition import SituationSettings



def get_trustworthiness_label(df_relationships):


    df_relationships['trustworthiness'] = trustworthy_label_encoder.transform([df_relationships['trustworthiness']])[0]
    
    df_relationships['report_trustworthiness'] = int(df_relationships['report_trustworthiness'])
    
    
    return df_relationships



def get_encoded_categorial_features(df_relationships):

    df_relationships = replace_column_with_encoded_data(df_relationships, 'role', role_one_hot)
    df_relationships = replace_column_with_encoded_data(df_relationships, 'transaction_type', transaction_type_one_hot)
    df_relationships = replace_column_with_encoded_data(df_relationships, 'status', status_one_hot)
    df_relationships = replace_column_with_encoded_data(df_relationships, 'task_context', task_context_one_hot)
    
    df_relationships = replace_column_with_encoded_data(df_relationships, 'trustee_type', device_one_hot)
    df_relationships = replace_column_with_encoded_data(df_relationships, 'trustor_type', device_one_hot)
    
    # df_relationships = replace_column_with_encoded_data(df_relationships, 'trustee_status', device_status_one_hot)
    # df_relationships = replace_column_with_encoded_data(df_relationships, 'trustor_status', device_status_one_hot)
    
    # df_relationships = replace_column_with_encoded_data(df_relationships, 'trustee_record_type', record_type_one_hot)
    # df_relationships = replace_column_with_encoded_data(df_relationships, 'trustor_record_type', record_type_one_hot)
    
    # df_relationships = replace_column_with_encoded_data(df_relationships, 'trustee_shape_status', shape_status_one_hot)
    # df_relationships = replace_column_with_encoded_data(df_relationships, 'trustor_shape_status', shape_status_one_hot)

    return df_relationships


def get_distance(df_relationships : dict):
    
    df_relationships['distance'] = distance.euclidean(df_relationships['trustee_location'], df_relationships['trustor_location'])
    
    return df_relationships

def one_hot_encode_enum(enum_class):
    members = [e.name for e in enum_class]
    categories = [members]
    one_hot_encoder = OneHotEncoder(categories=categories,sparse_output=False,handle_unknown='ignore',dtype=np.int8)
    return one_hot_encoder



def replace_column_with_encoded_data(transaction_event : dict, column_name : str, encoder : OneHotEncoder):
    # Reshape the data and encode
    column_data = np.array(transaction_event[column_name]).reshape(-1, 1)
    encoded_data = encoder.transform(column_data)
    


    encoded_feature_names = encoder.get_feature_names_out([column_name])

    # del transaction_event[column_name]

    # for i, feature_name in enumerate(encoded_feature_names):
    #         transaction_event[feature_name] = encoded_data[:, i].tolist()

    # return transaction_event
        # Prepare updates in a batch
    updates = {feature_name: encoded_data[:, i].flatten().tolist() for i, feature_name in enumerate(encoded_feature_names)}

    # Remove the original column and update the dictionary in a batch
    transaction_event.pop(column_name, None)  # Use pop to remove the column more safely
    transaction_event.update(updates)

    return transaction_event



def reorder_columns(df_relationships, trustor_features, trustee_features, edge_features, relationship_features):
    selected_columns = relationship_features + edge_features + trustee_features + trustor_features
    existing_columns = [col for col in selected_columns if col in df_relationships.columns]
    df_relationships = df_relationships[existing_columns].copy()
    return df_relationships


def prefix_device_state_keys(device_state, prefix):
    return {f"{prefix}_{key}": value for key, value in device_state.items()}



def join_device_data(transaction : AbstractTransaction) -> dict:
    
    if  not hasattr(transaction,'parent_transaction_id'):
        combined_data = get_combined_data(transaction)
        
    elif hasattr(transaction,'parent_transaction_id'):
        parent_transaction = transaction.parent_transaction
        combined_data = get_combined_data(parent_transaction)

    return combined_data 


def get_combined_data(transaction : AbstractTransaction):
    
    trustee_state = transaction.trustee.to_dict()
    trustor_state = transaction.trustor.to_dict()
        
    trustee_device_state = prefix_device_state_keys(trustee_state, 'trustee')
    trustor_device_state = prefix_device_state_keys(trustor_state, 'trustor')
    
    transaction_dict = transaction.to_dict()
        
    combined_data = {**transaction_dict, **trustee_device_state, **trustor_device_state}
    
    return combined_data
    
    
def get_engineered_features(transaction_dict : dict):
    
    relationship_features = ['time', 'trustee', 'trustor', 'trustworthiness']

    edge_features = [
        'trust_value',
        'report_trustworthiness',
        'distance',
        'last_transaction_id',
        'object_type',
        'role',
        'last_trust_value',
        'last_verified_transaction_trust_value',
        'status',
        'task_context',
        'transaction_type',
        'degree_of_common_friendship',
        'interaction_frequency',
        'last_verified_transaction_id',
        'transaction_id'
        ]

    trustor_features = [
        'trustor_location', 
        'trustor_device_id',
        'trustor_num_trustworthy_relationships',
        'trustor_trustworthy_devices',
        'trustor_type',
        'trustor_record_type',
        'trustor_untrustworthy_devices',
        'trustor_num_trustor_transactions',
        'trustor_status',
        'trustor_speed',
        'trustor_num_trustee_transactions',
        'trustor_num_trust_transactions',
        'trustor_num_untrustworthy_relationships',
        'trustor_shape_status',
        'trustor_position',
        'trustor_num_related_devices',
        'trustor_signal',
        'trustor_sensor_id',
        'trustor_observed_street'
    ]

    trustee_features = [
        'trustee_location',
        'trustee_trustworthy_devices',
        'trustee_record_type',
        'trustee_untrustworthy_devices',
        'trustee_num_trustor_transactions',
        'trustee_num_trustee_transactions',
        'trustee_num_trust_transactions',
        'trustee_position',
        'trustee_num_related_devices',
        'trustee_device_id',
        'trustee_num_trustworthy_relationships',
        'trustee_type',
        'trustee_signal',
        'trustee_status',
        'trustee_speed',
        'trustee_num_untrustworthy_relationships',
        'trustee_shape_status',
        'trustee_sensor_id'
    ]
    
    transaction_event_dict = transaction_dict
    
    transaction_event_dict['trustee_record_type'] = 'STATUS'
    transaction_event_dict['trustor_record_type'] = 'STATUS'
    
    transaction_event_dict = get_trustworthiness_label(transaction_event_dict)
    transaction_event_dict = get_distance(transaction_event_dict)
    
    transaction_event_dict = get_encoded_categorial_features(transaction_event_dict)
    
    # transaction_event_dict['prediction'] = transaction_event_dict['trust_value']
    # transaction_event_dict['trust_prediction_score'] = (transaction_event_dict['trustworthiness'] - (transaction_event_dict['report_trustworthiness'] - transaction_event_dict['trust_value']).abs()).abs()


    # transaction_event_dict.loc[(transaction_event_dict['status_PENDING'] == 1) & (transaction_event_dict['role_SERVICE_PROVIDER'] == 1) & (transaction_event_dict['transaction_type_DIRECT_TRANSACTION'] == 1), 'prediction'] = transaction_event_dict['trust_prediction_score']
    # transaction_event_dict.loc[transaction_event_dict['status_VERIFIED'] == 1, 'prediction'] = transaction_event_dict['trustworthiness']
    
    
    # transaction_event_dict = transaction_event_dict.sort_values(by='time')
    # print(df_relationships.info())
    # print(df_relationships.describe())
    
    
    del transaction_event_dict['last_transaction_id']
    
    
    return transaction_event_dict


def preprocess_data(trustor : GenericDevice, trustee : GenericDevice, trust_value : float, request : SendingPacket, transaction : AbstractTransaction, situation_settings : SituationSettings) -> DataFrame:
    
    
    interaction_frequency = trustor.trust_manager.trust_transaction_controller.transaction_manager.get_transaction_frequency(transaction.trustor._id, transaction.trustee._id)
    degree_of_trustworthiness = trustor.trust_manager.trust_transaction_controller.get_friendship_similarity_by_transaction(transaction)

    last_transaction_id, last_trust_value = trustor.trust_manager.trust_transaction_controller.get_last_transaction_of_trustee(transaction.trustee._id)
    last_verified_transaction_id, last_verified_transaction_trust_value = trustor.trust_manager.trust_transaction_controller.get_last_verified_transaction(transaction.trustee._id)
    parent_transaction_id = transaction.original_transaction_id if isinstance(transaction, DirectRecommendation) else None
    
    
    #transaction to list 
    transaction_dict = {
            'transaction_id' : transaction._id,
            'transaction_type' : transaction.type.name,
            'trustor' : transaction.trustor._id,
            'trustee' : transaction.trustee._id,
            'time': transaction.transaction_context.creation_time,
            'trustor_location' : transaction.transaction_context.trustor_location,
            'trustee_location' : transaction.transaction_context.trustee_location,
            'trust_value' : transaction.trust_value,
            'status' : transaction.status.name,
            'task_context': request.request_type.name,
            'trustworthiness' : transaction.trustee._behaviour.name,
            'role' : transaction.role.name,
            'last_trust_value' : last_trust_value,
            'last_verified_transaction_trust_value' : last_verified_transaction_trust_value,
            'last_verified_transaction_id' : last_verified_transaction_id,
            'last_transaction_id' : last_transaction_id,
            'parent_transaction_id' : parent_transaction_id,
            'interaction_frequency' : interaction_frequency,
            'degree_of_common_friendship' : degree_of_trustworthiness,
            'reporting_time' : transaction.reporting_time,
            'verification_time' : transaction.verification_time,
            'report_trustworthiness' : transaction.task_context.simulation_event.is_authentic,
        }
    
    
    # df_trust_transactions : DataFrame = DataFrame(transaction_dict)
    
    # new_order = ['time', 'trustee', 'trustor', 'trust_value', 'report_trustworthiness'] + [col for col in df_trust_transactions.columns if col not in ['time', 'trustee', 'trustor', 'trust_value', 'report_trustworthiness']]
    # df_trust_transactions = df_trust_transactions[new_order]    
    
    # df_trust_transactions_device_states = preprocessing.get_and_join_device_states(df_trust_transactions)
        
    transaction_dict = join_device_data(transaction)        
    
    
    
    exclude_columns = [ 'trustee_manufacturer',
                        'trustee_model',
                        'trustee_firmware_version',
                        'trustee_affiliations',
                        'trustee_hardware_version',
                        'trustee_services',
                        'trustee_id',
                        'trustee_serial_number',
                        'trustee_next_maintenance_date',
                        'trustee_properties',
                        'trustee_experiment_id',
                        'trustee_last_maintenance_date',
                        'trustee_date_of_manufacture',
                        'trustee_lane_position',
                        'trustee_lane_id',
                        'trustee_edge_id',
                        'trustee_time',
                        'trustee_simulation_run_id',
                        'trustee_color',
                        'trustee_object_type',
                        'parent_transaction_id',
                
                        'trustor_simulation_run_id',
                        'trustor_last_maintenance_date',
                        'trustor_date_of_manufacture',
                        'trustor_lane_position',
                        'trustor_lane_id',
                        'trustor_edge_id',
                        'trustor_time',
                        'trustor_object_type',
                        'trustor_color',
                        'trustor_manufacturer', 
                        'trustor_model', 
                        'trustor_firmware_version',
                        'trustor_affiliations',
                        'trustor_hardware_version',
                        'trustor_services',
                        'trustor_id',
                        'trustor_serial_number',
                        'trustor_next_maintenance_date',
                        'trustor_properties',
                        'trustor_experiment_id'
                ]

    transaction_dict = {key: value for key, value in transaction_dict.items() if key not in exclude_columns}
    

    trustor_id = trustor._device_map_id
    trustee_id = trustee._device_map_id
    
    
    transaction_dict['trustor'] = trustor_id
    transaction_dict['trustee'] = trustee_id

    return transaction_dict



trustworthy_label_encoder = LabelEncoder()
members = [e.name for e in DeviceBehaviour]
trustworthy_label_encoder.fit(members)

status_one_hot = one_hot_encode_enum(TransactionStatus)
status_one_hot.fit([['PENDING'], ['VERIFIED'], ['EXPIRED']])

transaction_type_one_hot = one_hot_encode_enum(TransactionType)
transaction_type_one_hot.fit([['DIRECT_TRANSACTION'], ['DIRECT_RECOMMENDATION'], ['DIRECT_RECOMMENDATION']]) 
role_one_hot = one_hot_encode_enum(TrustVerfierRoles)
role_one_hot.fit([['SERVICE_PROVIDER'], ['REPORTER'], ['RECOMMENDER']])

task_context_one_hot = one_hot_encode_enum(ReportType)
task_context_one_hot.fit([['EmergencyReport'], ['TrafficPriorityRequest']])

device_one_hot = one_hot_encode_enum(DeviceType)
device_one_hot.fit([['TRAFFIC_CAMERA'], ['INDUCTION_LOOP'], ['SMART_PHONE'], ['VEHICLE'], ['EMERGENCY_CENTER'], ['TRAFFIC_LIGHT']])

device_status_one_hot = one_hot_encode_enum(DeviceInternalStatus)
device_status_one_hot.fit([['ACTIVE'], ['INACTIVE']])

record_type_one_hot = one_hot_encode_enum(DeviceRecordType)
record_type_one_hot.fit([['STATUS'], ['SENSED']])

shape_status_one_hot = one_hot_encode_enum(DeviceShapeStatus)
shape_status_one_hot.fit([['ORIGINAL_MANUFACTURED'], ['DEFORMED']])
