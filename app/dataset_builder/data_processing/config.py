
import sys
sys.path.insert(0, '/app') 
import os
from dataset_builder.utils.path_helper import DatasetTask, DatasetType, get_dataset_directory_path, get_raw_dataset_directory_path, set_constants


BUILD_DEVICE='local'
# DATASET_OPTION='node_classification'
DATASET_OPTION='edge_prediction'
# DATASET_OPTION='subgraph_classification'
dataset_type = DatasetType.LINK_PREDICTION_SITUATION_LABELS.value


# Constants
BUILD_DEVICE = 'local'
DATASET_OPTION = 'edge_prediction' 
DATA_NAME = 'iot-unsw'

# Directory Paths
DATASET_TYPE = DatasetType.LINK_PREDICTION_DISTANCE_LABELS.value
DATASET_TASK = DatasetTask.LINK_PREDICTION.value

set_constants(DATASET_TYPE, DATASET_TASK)

DATA_DIR = get_dataset_directory_path()
DATA_DIR_OUTPUT = os.path.join(DATA_DIR, f"{DATA_NAME}")


DATA_INPUT_DIR = get_raw_dataset_directory_path()

# File Paths
DEVICES_PATH = os.path.join(DATA_INPUT_DIR, 'devices.csv')
RELATIONSHIPS_PATH = os.path.join(DATA_INPUT_DIR, 'relationships.csv')


OUT_NODE_RAW_DF = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_nodes_raw.csv")
OUT_RELATION_RAW_DF = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_edges_raw.csv")

# Output File Paths
OUT_RELATION_DF = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_edges.csv")
OUT_NODE_DF = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_nodes.csv")
OUT_FEAT = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_edge_features.npy")
OUT_NODE_FEAT = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_node_features.npy")
OUT_DATASET = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}.csv")




OUT_NODE_CLASSIFICATION_SITUATION_DF = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_situation_labels.csv")
OUT_NODE_CLASSIFICATION_DISTANCE_DF = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_distance_labels.csv")

DATA_DIR_OUTPUT = os.path.join(DATA_DIR, f"{DATA_NAME}_{DATASET_OPTION}")
OUT_EDGE_PREDICTION_DATASET = os.path.join(DATA_DIR_OUTPUT, f"ml_{DATA_NAME}_edge_prediction.csv")

# Create output directory if it doesn't exist
# if not os.path.exists(DATA_DIR_OUTPUT):
#     os.makedirs(DATA_DIR_OUTPUT)