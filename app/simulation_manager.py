import os
import time
from experiments.settings import Settings
from simulation_config import SimulationConfiguration
from utils import query_elk
import utils.postprocessing.experiment_setting as experiment_settings_writer
import utils.logging as logger
import experiments.handler as experiment_manager

import experiment_design
import simulator

import pathfinder
import experiments.process_experiment_results as process_results
import time

def main():


    # clean_output_directory()
    
    # logger.get_logger().delete_index()
    # logger.get_logger().create_index()


        
    
    for experiment_settings in experiment_design.EXPERIMENTS:
        
        experiment_manager.configure_experiment_settings(experiment_settings)
        experiments_result = []
        print(f"Running Experiment: {Settings.EXPERIMENT_NAME} with trust model: {Settings.SELECTED_TRUST_MODEL} with {Settings.MAX_NUMBER_SIMULATION_RUNS} runs")
        
        Settings.SIMULATION_RUN_INDEX = 0
        SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES = 0.3
        
        while Settings.SIMULATION_RUN_INDEX < Settings.MAX_NUMBER_SIMULATION_RUNS:
            
            logger.get_logger().delete_index()
            logger.get_logger().create_index()

            simulation_results = simulator.start_experiment_run() 
            
            if simulation_results == None:
                # Settings.SIMULATION_RUN_INDEX -= 1
                continue
                       
            simulation_result_path = pathfinder.get_simulation_results_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)

            log_simulation_results(simulation_results, simulation_result_path)            
            experiments_result.append(simulation_results)
            
            log_simulation_output_data()

            
            Settings.SIMULATION_RUN_INDEX += 1

        log_experiment_settings()
        
        log_experiment_results(experiments_result)

        temp_experiment_name = "ROBUSTUNESS_EXPERIMENT"

        Settings.SIMULATION_RUN_INDEX = 0
        
        while SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES < 0.4:
            SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES += 0.1
            Settings.EXPERIMENT_NAME = temp_experiment_name + "_MALICIOUS_DEGREE" + str(SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES)
            print(f"Running Experiment: {Settings.EXPERIMENT_NAME} with trust model: {Settings.SELECTED_TRUST_MODEL} with {Settings.MAX_NUMBER_SIMULATION_RUNS} runs")
        
            Settings.SIMULATION_RUN_INDEX = 0
            
            while Settings.SIMULATION_RUN_INDEX < 3:
                
                logger.get_logger().delete_index()
                logger.get_logger().create_index()
                
                simulation_results = simulator.start_experiment_run()    
                
                if simulation_results == None:
                    # Settings.SIMULATION_RUN_INDEX -= 1
                    continue
                        
                simulation_result_path = pathfinder.get_simulation_results_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)

                log_simulation_results(simulation_results, simulation_result_path)            
                experiments_result.append(simulation_results)
                
                log_simulation_output_data()
                
                Settings.SIMULATION_RUN_INDEX += 1
            
            # Save Experiment Settings
            log_experiment_settings()
        
            # Set experiment statistics
            log_experiment_results(experiments_result)
            
        SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES = 0.2




def log_experiment_results(experiments_result):
    experiment_statistics, df_experiment_results = process_results.get_experiment_results(experiments_result)
    experiemnt_result_path = pathfinder.get_experiment_results_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME)
    
    experiment_statistics_file_pickle = os.path.join(experiemnt_result_path, "experiment_statistics.pickle")
    experiment_statistics_file_csv = os.path.join(experiemnt_result_path, "experiment_statistics.csv")
    experiment_results_file_pickle = os.path.join(experiemnt_result_path, "experiment_results.pickle")
    experiment_results_file_csv = os.path.join(experiemnt_result_path, "experiment_results.csv")
        
    logger.write_pickle(experiment_statistics_file_pickle, experiment_statistics)
    logger.write_pickle(experiment_results_file_pickle, df_experiment_results)
    logger.write_csv(experiment_statistics_file_csv, experiment_statistics)
    logger.write_csv(experiment_results_file_csv, df_experiment_results)

def log_experiment_settings():
    experiment_settings_path = pathfinder.get_experiment_settings_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME)
    experiment_settings_path_file = os.path.join(experiment_settings_path, "experiment_configuration_report.txt")

    experiment_settings = experiment_settings_writer.collect_settings()
    experiment_settings_writer.write_report_to_file(settings=experiment_settings, filename=experiment_settings_path_file)

def log_simulation_output_data():
    
    time.sleep(30)
    
    
    
    data_path = pathfinder.get_simulation_data_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
    # simulation_data_output_path = pathfinder.get_simulation_data_output_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
    
    end_time = query_elk.get_max_time(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    print(f"End time: {end_time}")        
    
    
    object_states = query_elk.get_object_states_for_time_range(0, end_time, Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX, ["INDUCTION_LOOP", "SMART_PHONE", "VEHICLE", "TRAFFIC_CAMERA", "TRAFFIC_LIGHT", "EMERGENCY_CENTER"]) 
    print(f"Object states: {len(object_states)}")
    
    reports = query_elk.get_reports(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    print(f"Reports: {len(reports)}")
    
    events = query_elk.get_events(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    print(f"Events: {len(events)}")
    
    trust_transactions = query_elk.get_trust_transactions(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    trust_transactions = query_elk.remove_extra_attributes(trust_transactions)
    
    print(f"Trust transactions: {len(trust_transactions)}")
    
    debug_accident_status = query_elk.get_debug_accident_status(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    print(f"Debug accident status: {len(debug_accident_status)}")
    
    route_messages = query_elk.get_route_messages(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    print(f"Route messages: {len(route_messages)}")
            
    log_object_states_file = os.path.join(data_path, "object_states.pickle")
    log_reports_file = os.path.join(data_path, "reports.pickle")
    log_events_file = os.path.join(data_path, "events.pickle")
    log_trust_transactions_file = os.path.join(data_path, "trust_transactions.pickle")
    log_debug_accident_status_file = os.path.join(data_path, "debug_accident_status.pickle")
    log_route_messages_file = os.path.join(data_path, "route_messages.pickle")
            
    print(f"Data from Elastichseach into pickle files")
            
    logger.write_pickle(log_object_states_file, object_states)
    logger.write_pickle(log_reports_file, reports)
    logger.write_pickle(log_events_file, events)
    logger.write_pickle(log_trust_transactions_file, trust_transactions)
    logger.write_pickle(log_debug_accident_status_file, debug_accident_status)
    logger.write_pickle(log_route_messages_file, route_messages)

def log_simulation_results(simulation_results, simulation_result_path):
    simulation_result_overall_file = os.path.join(simulation_result_path, "simulation_results.pickle")
    report_file = os.path.join(simulation_result_path, "reports.pickle")
    events_file = os.path.join(simulation_result_path, "events.pickle")
    performance_file = os.path.join(simulation_result_path, "performance.pickle")
    emergency_evaluation_file = os.path.join(simulation_result_path, "emergency_evaluation.pickle")
    traffic_light_evaluation_file = os.path.join(simulation_result_path, "traffic_light_evaluation.pickle")
    
    
    
    
            
    # logger.write_pickle(simulation_result_overall_file, simulation_results)
    # logger.write_pickle(report_file, simulation_results[0])
    # logger.write_pickle(events_file, simulation_results[1])
    logger.write_pickle(performance_file, simulation_results[0])
    logger.write_pickle(emergency_evaluation_file, simulation_results[1])
    logger.write_pickle(traffic_light_evaluation_file, simulation_results[2])






def clean_output_directory():
    try:
        # shutil.rmtree('/app/output/simulation_runs')
        pass
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()