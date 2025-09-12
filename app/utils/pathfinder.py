import os
import datetime

project_root = os.getenv("RESEARCH_PROJECT_ROOT", default="/app")
date_str = None




def create_folder(path):
    os.makedirs(path, exist_ok=True)
    return path

def get_base_path():
    global date_str 
    if date_str == None:
        date_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

      
    
    return create_folder(os.path.join(project_root, 'output', date_str))

def get_trust_model_path(trust_model):
    base_path = get_base_path()
    return create_folder(os.path.join(base_path, trust_model))

def get_experiment_path(trust_model, experiment_name):
    trust_model_path = get_trust_model_path(trust_model)
    return create_folder(os.path.join(trust_model_path, experiment_name))

def get_simulation_path(trust_model, experiment_name, simulation_run_number):
    experiment_path = get_experiment_path(trust_model, experiment_name)
    simulation_dir = f'simulation_run_{simulation_run_number}'
    return create_folder(os.path.join(experiment_path, simulation_dir))

def get_simulation_data_path(trust_model, experiment_name, simulation_run_number):
    simulation_path = get_simulation_path(trust_model, experiment_name, simulation_run_number)
    return create_folder(os.path.join(simulation_path, 'data', 'simulation_data'))

def get_profiler_path(trust_model, experiment_name, simulation_run_number):
    simulation_path = get_simulation_path(trust_model, experiment_name, simulation_run_number)
    return create_folder(os.path.join(simulation_path, 'data', 'profiler'))

def get_simulation_results_path(trust_model, experiment_name, simulation_run_number):
    simulation_path = get_simulation_path(trust_model, experiment_name, simulation_run_number)
    return create_folder(os.path.join(simulation_path, 'results'))

def get_experiment_settings_path(trust_model, experiment_name):
    experiment_path = get_experiment_path(trust_model, experiment_name)
    return create_folder(os.path.join(experiment_path, 'experiments_settings'))

def get_experiment_results_path(trust_model, experiment_name):
    experiment_path = get_experiment_path(trust_model, experiment_name)
    return create_folder(os.path.join(experiment_path, 'results'))


def get_accident_debug_path(trust_model, experiment_name, simulation_run_number):
    simulation_path = get_simulation_data_path(trust_model, experiment_name, simulation_run_number)
    return create_folder(os.path.join(simulation_path, 'debug', 'accident_reports'))


def get_traffic_light_debug_path(trust_model, experiment_name, simulation_run_number):
    simulation_path = get_simulation_data_path(trust_model, experiment_name, simulation_run_number)
    return create_folder(os.path.join(simulation_path, 'debug', 'traffic_light_reports'))

def get_simulation_data_output_path(trust_model, experiment_name, simulation_run_number):
    simulation_path = get_simulation_data_path(trust_model, experiment_name, simulation_run_number)
    return create_folder(os.path.join(simulation_path, 'output'))

def get_simulation_data_screenshot_path(trust_model, experiment_name, simulation_run_number):
    simulation_path = get_simulation_data_path(trust_model, experiment_name, simulation_run_number)
    return create_folder(os.path.join(simulation_path, 'screenshots'))