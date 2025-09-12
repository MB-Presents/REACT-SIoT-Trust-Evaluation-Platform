from enum import Enum
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

ROOT_DIRS = {
    'local': '/app/scenario_identification',
    'server': '/export/home/s2995839/scenario_identification'
}

RELATIVE_PATHS = {
    'dataset_folder': 'data',
    'in_memory_dataset_folder': 'data/in_memory_dataset',
    'node_embedding_output_folder': 'output/node_embeddings',
    'loss_output_folder': 'output/trainings_process',
    'model_output_folder': 'output/model',
    'graph_images_folder': 'output/graph-images',
    'data_folder': 'data',
    'raw_dataset_folder': 'data/raw',
    'profiler_output_folder': 'output/profiler',
    'evaluation_folder': 'output/evaluation',
    'output_video_folder': 'output/video'
}

FILE_NAMES = {
    'in_memory_dataset': 'dataset.pt',
    'output_video': 'video.mp4',
    'link_prediction_model': 'link_prediction_model.pt',
    'node_classification_model': 'node_classification_model.pt',
    'confusion_maxtrix': 'confusion_matrix.png',
    'roc_curve': 'roc_curve.png',
    'evaluation_results': 'evaluation_results.png',
    'trainings_loss': 'trainings_loss.png'
}

OPTIONS = {
    'dataset_name': 'iot-unsw',
    'task':{
        'node_classification': 'node_classification',
        'edge_prediction': 'edge_prediction',
        'subgraph_classification': 'subgraph_classification'
    },
    # 'node_classification': 'node_classification',
    # 'edge_prediction': 'edge_prediction',
    # 'subgraph_classification': 'subgraph_classification',
    'extension':{
        'node_classification': 'csv',
        'edge_prediction': 'csv',
        'subgraph_classification': 'pkl'
    }
}

BUILD_DEVICE = os.getenv("BUILD_DEVICE", "local")  # Read from Environment variable
DATASET_TYPE = None
DATASET_TASK = None


class DatasetType(Enum):
    NODE_CLASSIFICATION_SITUATION_LABELS = 'node_classification_situation_labels'
    NODE_CLASSIFICATION_DISTANCE_LABELS = 'node_classification_distance_labels'
    LINK_PREDICTION_SITUATION_LABELS = 'link_prediction_situation_labels'
    LINK_PREDICTION_DISTANCE_LABELS = 'link_prediction_distance_labels'
    SUBGRAPH_CLASSIFICATION_SITUATION_LABELS = 'subgraph_classification_situation_labels'
    SUBGRAPH_CLASSIFICATION_DISTANCE_LABELS = 'subgraph_classification_distance_labels'
    RAW_DATASET = 'raw_dataset'

class DatasetTask(Enum):
    NODE_CLASSIFICATION = 'node_classification'
    LINK_PREDICTION = 'edge_prediction'
    SUBGRAPH_CLASSIFICATION = 'subgraph_classification'
    


def set_constants(dataset_type, dataset_task, experiment_name='none'):
    global DATASET_TYPE
    global DATASET_TASK
    global EXPERIMENT_NAME
    
    DATASET_TYPE = dataset_type
    DATASET_TASK = dataset_task
    EXPERIMENT_NAME = experiment_name


def get_path(key):
    try:
        root_dir = ROOT_DIRS[BUILD_DEVICE]
        relative_path = RELATIVE_PATHS[key]
    except KeyError:
        raise ValueError("Invalid running environment or key specified.")
    
    full_path = Path(root_dir) / relative_path
    return full_path

def ensure_directory_exists(path):
    
    if not isinstance(path,Path):
        path = Path(path)
        
    if not path.exists():
        path.mkdir(parents=True)

def join_dataset_type_to_path(path, dataset_type):
    path = os.path.join(path, dataset_type)
    return Path(path)


def get_csv_file_name():
    
    
    EXTENSION = '.csv'
    
    file = f"{ OPTIONS['dataset_name'] }_{ OPTIONS['task'][DATASET_TASK] }.{OPTIONS['extension'][DATASET_TASK]}"
    return file


def get_roc_curve_file_path():
    evaluation_directory = get_evaluation_directory_path() 
    file_path = os.path.join(evaluation_directory, FILE_NAMES['roc_curve'])
    return  file_path

def get_evaluation_result_path():
    evaluation_directory = get_evaluation_directory_path() 
    file_path = os.path.join(evaluation_directory, FILE_NAMES['evaluation_results'])
    return  file_path

def get_evaluation_directory_path():
    path = get_path('evaluation_folder')
    
    if EXPERIMENT_NAME != 'none':
        path = os.path.join(path, EXPERIMENT_NAME)
    
    
    path = join_dataset_type_to_path(path, DATASET_TYPE)
    ensure_directory_exists(path)
    return path
    
def get_confusion_matrix_file_path():    
    evaluation_directory = get_evaluation_directory_path() 
    file_path = os.path.join(evaluation_directory, FILE_NAMES['confusion_maxtrix'])
    return  file_path

def get_dataset_file_path():
    
    DATA_DIR = get_dataset_directory_path()
    DATA_DIR = Path(os.path.join(DATA_DIR, OPTIONS['dataset_name']))
    ensure_directory_exists(DATA_DIR)
    
    file_name = get_csv_file_name()
    DATA_DIR_FILES_PATH = os.path.join(DATA_DIR, file_name)
    
    return DATA_DIR_FILES_PATH
    
def get_trainings_loss_file_path():
    output_trainings_loss_path = get_evaluation_directory_path()
    file_path = os.path.join(output_trainings_loss_path, FILE_NAMES['trainings_loss'])
    return file_path

def get_dataset_path():
    path = get_path('dataset_folder')
    path = join_dataset_type_to_path(path, DATASET_TYPE)
    ensure_directory_exists(Path(path))
    return path

def get_in_memory_dataset_path():
    folder_path = get_path('in_memory_dataset_folder')
    
    # TODO: WRONG JUST TEST FOR TASK
    DATASET_TYPE = DatasetType.LINK_PREDICTION_DISTANCE_LABELS.value
# DATASET_TASK = DatasetTask.LINK_PREDICTION.value    

    # set_constants(DATASET_TYPE, DATASET_TASK, experiment_name)
    folder_path = join_dataset_type_to_path(folder_path, DATASET_TYPE)
    ensure_directory_exists(Path(folder_path))
    return os.path.join(folder_path, FILE_NAMES['in_memory_dataset'])



def get_loss_output_path():
    path = get_path('loss_output_folder')
    path = join_dataset_type_to_path(path, DATASET_TYPE)
    ensure_directory_exists(path)
    return path



def get_graph_images_timeslot_output_path():
    path = get_path('graph_images_folder')
    path = join_dataset_type_to_path(path, DATASET_TYPE)
    
    ensure_directory_exists(path)
    return path


def get_dataset_directory_path():
    
    path = get_path('data_folder')
    # path = join_dataset_type_to_path(path, DATASET_TYPE)
    ensure_directory_exists(path)
    return path

def get_raw_dataset_directory_path():
    path = get_path('raw_dataset_folder')
    ensure_directory_exists(path)
    return path

def get_image_output_directory(dataset_name):
    base_output_path = get_graph_images_timeslot_output_path(BUILD_DEVICE)
    return os.path.join(base_output_path, dataset_name)



def get_profiler_output_path():
    path = get_path('profiler_output_folder')
    path = join_dataset_type_to_path(path, DATASET_TYPE)
    ensure_directory_exists(path)
    return path


def get_output_video_path(dataset_name):
    path = get_path('output_video_folder')
    path = join_dataset_type_to_path(path, dataset_name)
    
    ensure_directory_exists(path)
    
    return os.path.join(path, FILE_NAMES['output_video'])


def get_experiment_directory():
    
    path = get_path('evaluation_folder')
    
    if EXPERIMENT_NAME != 'none':
        path = os.path.join(path, EXPERIMENT_NAME)
    
    return path

def get_trainings_logs_path():
    path = get_experiment_directory()
    
    path = os.path.join(path, 'trainings_logs')
    
    ensure_directory_exists(path)
    
    file_name = 'trainings_logs.txt'
    
    
    file_path = os.path.join(path, file_name)
      
    
    
    return file_path



def get_experiment_report_path():
    
    path = get_experiment_directory()
    path = os.path.join(path, 'experiment_report')
    
    ensure_directory_exists(path)
    
    file_name = 'experiment_report.txt'
    file_path = os.path.join(path, file_name)
    
    return file_path


def get_experiment_config_path():
        
    path = get_experiment_directory()
    path = os.path.join(path, 'experiment_config')
    
    ensure_directory_exists(path)
    
    file_name = 'experiment_config.txt'
    file_path = os.path.join(path, file_name)
    
    return file_path




def get_model_output_path():
    path = get_experiment_directory()
    path = os.path.join(path, 'model')
    
    ensure_directory_exists(path)
    
    if DATASET_TASK == DatasetTask.NODE_CLASSIFICATION.value:
        filename = FILE_NAMES['node_classification_model']
    elif DATASET_TASK == DatasetTask.LINK_PREDICTION.value:
        filename = FILE_NAMES['link_prediction_model']
    
    model_file_path = os.path.join(path, filename)
    
    
    return model_file_path



def get_node_embedding_output_folder_path():
    path = get_experiment_directory()
    path = os.path.join(path, 'node_embeddings')
    
    ensure_directory_exists(path)
    
    return path