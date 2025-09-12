import time
from typing import List, Tuple, Any
from pathlib import Path
from core.simulation import simulator
from experiments.design.experiments_registry import EXPERIMENTS
from experiments.settings import Settings
from scenarios.canberra_case_study.simulation.simulation_config import SimulationConfiguration
from utils import query_elk
import utils.postprocessing.experiment_setting as experiment_settings_writer
import utils.logging as logger
import experiments.handler as experiment_manager
import utils.pathfinder as pathfinder
import experiments.process_experiment_results as process_results


def run_all_experiments() -> None:
    """
    Main entry point for executing all experiments in the registry.
    """
    # Precondition checks
    assert EXPERIMENTS is not None, "EXPERIMENTS registry must be initialized"
    assert len(EXPERIMENTS) > 0, "EXPERIMENTS registry must contain at least one experiment"
    assert hasattr(SimulationConfiguration, 'PERCENTAGE_OF_MALICIOUS_VEHICLES'), \
        "SimulationConfiguration must have PERCENTAGE_OF_MALICIOUS_VEHICLES attribute"
    
    original_malicious_vehicle_percentage = SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES
    
    try:
        _execute_standard_experiment_suite()
        _execute_robustness_experiment_suite()
    finally:
        # Ensure configuration is reset even if an error occurs
        SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES = original_malicious_vehicle_percentage
    
    # Postcondition check
    assert SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES == original_malicious_vehicle_percentage, \
        "Malicious vehicle percentage must be restored to original value"


def _execute_standard_experiment_suite() -> None:
    """
    Execute all standard experiments from the EXPERIMENTS registry.
    
    For each experiment configuration, runs the specified number of simulation runs
    and logs all results and settings.
    """
    # Precondition checks
    assert EXPERIMENTS, "EXPERIMENTS registry must be populated"
    assert all(config is not None for config in EXPERIMENTS), \
        "All experiment configurations must be non-None"
    
    experiments_completed = 0
    
    for experiment_configuration in EXPERIMENTS:
        assert experiment_configuration is not None, "Experiment configuration cannot be None"
        
        experiment_manager.configure_experiment_settings(experiment_configuration)
        
        # Verify settings were configured properly
        assert Settings.EXPERIMENT_NAME, "Experiment name must be set after configuration"
        assert Settings.SELECTED_TRUST_MODEL, "Trust model must be set after configuration"
        assert Settings.MAX_NUMBER_SIMULATION_RUNS > 0, "Max simulation runs must be positive"
        
        print(f"Running Experiment: {Settings.EXPERIMENT_NAME} with trust model: "
              f"{Settings.SELECTED_TRUST_MODEL} with {Settings.MAX_NUMBER_SIMULATION_RUNS} runs")
        
        standard_malicious_vehicle_percentage = 0.3
        simulation_results = _execute_simulation_run_batch(
            max_simulation_runs=Settings.MAX_NUMBER_SIMULATION_RUNS,
            malicious_vehicle_percentage=standard_malicious_vehicle_percentage
        )
        
        _persist_experiment_configuration_settings()
        _persist_aggregated_experiment_results(simulation_results)
        
        experiments_completed += 1
    
    # Postcondition check
    assert experiments_completed == len(EXPERIMENTS), \
        f"Expected {len(EXPERIMENTS)} experiments, completed {experiments_completed}"


def _execute_robustness_experiment_suite() -> None:
    """
    Execute robustness experiments with varying percentages of malicious vehicles.
    """
    # Precondition checks
    assert Settings.EXPERIMENT_NAME, "Original experiment name must be set"
    assert hasattr(SimulationConfiguration, 'PERCENTAGE_OF_MALICIOUS_VEHICLES'), \
        "SimulationConfiguration must have malicious vehicle percentage attribute"
    
    original_experiment_name = Settings.EXPERIMENT_NAME
    robustness_experiment_base_name = "ROBUSTNESS_EXPERIMENT"
    minimum_malicious_percentage = 0.3
    maximum_malicious_percentage = 0.4
    percentage_increment_step = 0.1
    robustness_simulation_runs_per_configuration = 3
    default_malicious_percentage = 0.2
    
    current_malicious_percentage = minimum_malicious_percentage
    robustness_experiments_completed = 0
    
    try:
        while current_malicious_percentage < maximum_malicious_percentage:
            current_malicious_percentage += percentage_increment_step
            
            # Verify percentage is within valid range
            assert 0 <= current_malicious_percentage <= 1, \
                f"Malicious percentage {current_malicious_percentage} must be between 0 and 1"
            
            SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES = current_malicious_percentage
            Settings.EXPERIMENT_NAME = f"{robustness_experiment_base_name}_MALICIOUS_DEGREE{current_malicious_percentage:.1f}"
            
            print(f"Running Experiment: {Settings.EXPERIMENT_NAME} with trust model: "
                  f"{Settings.SELECTED_TRUST_MODEL} with {robustness_simulation_runs_per_configuration} runs")
            
            simulation_results = _execute_simulation_run_batch(
                max_simulation_runs=robustness_simulation_runs_per_configuration,
                malicious_vehicle_percentage=current_malicious_percentage
            )
            
            _persist_experiment_configuration_settings()
            _persist_aggregated_experiment_results(simulation_results)
            
            robustness_experiments_completed += 1
            
    finally:
        Settings.EXPERIMENT_NAME = original_experiment_name
        SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES = default_malicious_percentage
    
    # Postcondition checks
    assert Settings.EXPERIMENT_NAME == original_experiment_name, \
        "Original experiment name must be restored"
    assert SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES == default_malicious_percentage, \
        "Malicious vehicle percentage must be reset to default"
    assert robustness_experiments_completed > 0, \
        "At least one robustness experiment must be completed"


def _execute_simulation_run_batch(max_simulation_runs: int, malicious_vehicle_percentage: float) -> List[Any]:
    """
    Execute a batch of simulation runs for the current experiment configuration.
    """
    # Precondition checks
    assert max_simulation_runs > 0, f"max_simulation_runs must be positive, got {max_simulation_runs}"
    assert 0 <= malicious_vehicle_percentage <= 1, \
        f"malicious_vehicle_percentage must be between 0 and 1, got {malicious_vehicle_percentage}"
    assert hasattr(Settings, 'SIMULATION_RUN_INDEX'), \
        "Settings must have SIMULATION_RUN_INDEX attribute"
    
    successful_simulation_results = []
    Settings.SIMULATION_RUN_INDEX = 0
    SimulationConfiguration.PERCENTAGE_OF_MALICIOUS_VEHICLES = malicious_vehicle_percentage
    
    while Settings.SIMULATION_RUN_INDEX < max_simulation_runs:
        _reset_logging_system_indices()
        
        single_simulation_result = simulator.start_experiment_run()
        
        if single_simulation_result is None:
            print(f"Simulation run {Settings.SIMULATION_RUN_INDEX} failed, retrying...")
            continue
        
        _persist_single_simulation_run_results(single_simulation_result)
        successful_simulation_results.append(single_simulation_result)
        _collect_and_persist_elasticsearch_simulation_data()
        
        Settings.SIMULATION_RUN_INDEX += 1
    
    # Postcondition checks
    assert len(successful_simulation_results) <= max_simulation_runs, \
        f"Cannot have more results ({len(successful_simulation_results)}) than max runs ({max_simulation_runs})"
    assert all(result is not None for result in successful_simulation_results), \
        "All simulation results must be non-None"
    assert Settings.SIMULATION_RUN_INDEX == len(successful_simulation_results), \
        f"Simulation run index ({Settings.SIMULATION_RUN_INDEX}) must equal successful results count ({len(successful_simulation_results)})"
    
    return successful_simulation_results


def _reset_logging_system_indices() -> None:
    """
    Reset logging indices for a new simulation run.
    """
    # Precondition checks
    simulation_logger = logger.get_logger()
    assert simulation_logger is not None, "Logger must be initialized"
    assert hasattr(simulation_logger, 'delete_index'), "Logger must have delete_index method"
    assert hasattr(simulation_logger, 'create_index'), "Logger must have create_index method"
    
    simulation_logger.delete_index()
    simulation_logger.create_index()
    
    # Postcondition verification would require logger state inspection
    # which may not be available in the interface


def _persist_aggregated_experiment_results(experiment_results_list: List[Any]) -> None:
    """
    Process and save aggregated experiment results to files.
    """
    # Precondition checks
    assert experiment_results_list, "experiment_results_list cannot be empty"
    assert Settings.SELECTED_TRUST_MODEL, "Trust model must be selected"
    assert Settings.EXPERIMENT_NAME, "Experiment name must be set"
    
    aggregated_experiment_statistics, processed_dataframe_results = \
        process_results.get_experiment_results(experiment_results_list)
    
    experiment_results_directory_path = Path(pathfinder.get_experiment_results_path(
        Settings.SELECTED_TRUST_MODEL, 
        Settings.EXPERIMENT_NAME
    ))
    
    # Define file paths using pathlib
    statistics_pickle_file_path = experiment_results_directory_path / "experiment_statistics.pickle"
    statistics_csv_file_path = experiment_results_directory_path / "experiment_statistics.csv"
    results_pickle_file_path = experiment_results_directory_path / "experiment_results.pickle"
    results_csv_file_path = experiment_results_directory_path / "experiment_results.csv"
    
    # Save files
    logger.write_pickle(str(statistics_pickle_file_path), aggregated_experiment_statistics)
    logger.write_pickle(str(results_pickle_file_path), processed_dataframe_results)
    logger.write_csv(str(statistics_csv_file_path), aggregated_experiment_statistics)
    logger.write_csv(str(results_csv_file_path), processed_dataframe_results)
    
    # Postcondition checks
    assert statistics_pickle_file_path.exists(), f"Statistics pickle file was not created: {statistics_pickle_file_path}"
    assert results_pickle_file_path.exists(), f"Results pickle file was not created: {results_pickle_file_path}"
    assert statistics_pickle_file_path.stat().st_size > 0, "Statistics pickle file is empty"
    assert results_pickle_file_path.stat().st_size > 0, "Results pickle file is empty"


def _persist_experiment_configuration_settings() -> None:
    """
    Save current experiment configuration to a report file.
    """
    # Precondition checks
    assert Settings.SELECTED_TRUST_MODEL, "Trust model must be selected"
    assert Settings.EXPERIMENT_NAME, "Experiment name must be set"
    
    experiment_settings_directory_path = Path(pathfinder.get_experiment_settings_path(
        Settings.SELECTED_TRUST_MODEL, 
        Settings.EXPERIMENT_NAME
    ))
    
    configuration_report_file_path = experiment_settings_directory_path / "experiment_configuration_report.txt"
    
    current_experiment_settings = experiment_settings_writer.collect_settings()
    assert current_experiment_settings is not None, "Collected settings cannot be None"
    
    experiment_settings_writer.write_report_to_file(
        settings=current_experiment_settings, 
        filename=str(configuration_report_file_path)
    )
    
    # Postcondition checks
    assert configuration_report_file_path.exists(), \
        f"Configuration report file was not created: {configuration_report_file_path}"
    assert configuration_report_file_path.stat().st_size > 0, \
        "Configuration report file is empty"


def _collect_and_persist_elasticsearch_simulation_data() -> None:
    """
    Collect simulation data from Elasticsearch and save to pickle files.
    """
    # Wait for Elasticsearch data to be fully indexed
    elasticsearch_indexing_delay_seconds = 30
    time.sleep(elasticsearch_indexing_delay_seconds)
    
    # Precondition checks
    assert Settings.EXPERIMENT_ID, "Experiment ID must be set"
    assert Settings.SIMULATION_RUN_INDEX is not None, "Simulation run index must be set"
    assert Settings.SELECTED_TRUST_MODEL, "Trust model must be set"
    assert Settings.EXPERIMENT_NAME, "Experiment name must be set"
    
    simulation_data_directory_path = Path(pathfinder.get_simulation_data_path(
        Settings.SELECTED_TRUST_MODEL, 
        Settings.EXPERIMENT_NAME, 
        Settings.SIMULATION_RUN_INDEX
    ))
    
    # Query data from Elasticsearch
    simulation_end_timestamp = query_elk.get_max_time(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    assert simulation_end_timestamp is not None, "Simulation end time must be available"
    print(f"Simulation end time: {simulation_end_timestamp}")
    
    monitored_entity_types = ["INDUCTION_LOOP", "SMART_PHONE", "VEHICLE", "TRAFFIC_CAMERA", "TRAFFIC_LIGHT", "EMERGENCY_CENTER"]
    simulation_start_timestamp = 0
    
    collected_object_states = query_elk.get_object_states_for_time_range(
        simulation_start_timestamp, simulation_end_timestamp, 
        Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX, monitored_entity_types
    )
    
    collected_reports = query_elk.get_reports(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    collected_events = query_elk.get_events(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    collected_trust_transactions = query_elk.get_trust_transactions(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    cleaned_trust_transactions = query_elk.remove_extra_attributes(collected_trust_transactions)
    collected_debug_accident_status = query_elk.get_debug_accident_status(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    collected_route_messages = query_elk.get_route_messages(Settings.EXPERIMENT_ID, Settings.SIMULATION_RUN_INDEX)
    
    # Verify data collection
    assert isinstance(collected_object_states, list), "Object states must be a list"
    assert isinstance(collected_reports, list), "Reports must be a list"
    assert isinstance(collected_events, list), "Events must be a list"
    assert isinstance(cleaned_trust_transactions, list), "Trust transactions must be a list"
    assert isinstance(collected_debug_accident_status, list), "Debug accident status must be a list"
    assert isinstance(collected_route_messages, list), "Route messages must be a list"
    
    # Print collection metrics
    print(f"Collected data counts:")
    print(f"  Object states: {len(collected_object_states)}")
    print(f"  Reports: {len(collected_reports)}")
    print(f"  Events: {len(collected_events)}")
    print(f"  Trust transactions: {len(cleaned_trust_transactions)}")
    print(f"  Debug accident status: {len(collected_debug_accident_status)}")
    print(f"  Route messages: {len(collected_route_messages)}")
    
    # Save data to pickle files using pathlib
    simulation_data_files_mapping = {
        "object_states.pickle": collected_object_states,
        "reports.pickle": collected_reports,
        "events.pickle": collected_events,
        "trust_transactions.pickle": cleaned_trust_transactions,
        "debug_accident_status.pickle": collected_debug_accident_status,
        "route_messages.pickle": collected_route_messages
    }
    
    created_files_count = 0
    for data_filename, collected_data in simulation_data_files_mapping.items():
        data_file_path = simulation_data_directory_path / data_filename
        logger.write_pickle(str(data_file_path), collected_data)
        
        # Postcondition check for each file
        assert data_file_path.exists(), f"Data file {data_filename} was not created at {data_file_path}"
        assert data_file_path.stat().st_size > 0, f"Data file {data_filename} is empty"
        created_files_count += 1
    
    # Final postcondition checks
    assert created_files_count == len(simulation_data_files_mapping), \
        f"Expected {len(simulation_data_files_mapping)} files, created {created_files_count}"
    
    print("All simulation data saved to pickle files")


def _persist_single_simulation_run_results(single_simulation_results: Tuple[Any, Any, Any]) -> None:
    """
    Save results from a single simulation run to pickle files.
    """
    # Precondition checks
    assert isinstance(single_simulation_results, (tuple, list)), \
        f"single_simulation_results must be a tuple or list, got {type(single_simulation_results)}"
    assert len(single_simulation_results) == 3, \
        f"single_simulation_results must contain exactly 3 elements, got {len(single_simulation_results)}"
    assert Settings.SELECTED_TRUST_MODEL, "Trust model must be set"
    assert Settings.EXPERIMENT_NAME, "Experiment name must be set"
    assert Settings.SIMULATION_RUN_INDEX is not None, "Simulation run index must be set"
    
    performance_data, emergency_evaluation_data, traffic_light_evaluation_data = single_simulation_results
    
    # Verify individual result components are not None
    assert performance_data is not None, "Performance data cannot be None"
    assert emergency_evaluation_data is not None, "Emergency evaluation data cannot be None"
    assert traffic_light_evaluation_data is not None, "Traffic light evaluation data cannot be None"
    
    simulation_results_directory_path = Path(pathfinder.get_simulation_results_path(
        Settings.SELECTED_TRUST_MODEL, 
        Settings.EXPERIMENT_NAME, 
        Settings.SIMULATION_RUN_INDEX
    ))
    
    # Define file paths using pathlib
    performance_data_file_path = simulation_results_directory_path / "performance.pickle"
    emergency_evaluation_file_path = simulation_results_directory_path / "emergency_evaluation.pickle"
    traffic_light_evaluation_file_path = simulation_results_directory_path / "traffic_light_evaluation.pickle"
    
    # Save results
    logger.write_pickle(str(performance_data_file_path), performance_data)
    logger.write_pickle(str(emergency_evaluation_file_path), emergency_evaluation_data)
    logger.write_pickle(str(traffic_light_evaluation_file_path), traffic_light_evaluation_data)
    
    # Postcondition checks
    simulation_result_files = [
        performance_data_file_path,
        emergency_evaluation_file_path,
        traffic_light_evaluation_file_path
    ]
    
    for result_file_path in simulation_result_files:
        assert result_file_path.exists(), f"Result file was not created: {result_file_path}"
        assert result_file_path.stat().st_size > 0, f"Result file is empty: {result_file_path}"


def _clean_output_directory_if_needed() -> None:
    """
    Clean the output directory by removing old simulation runs.
    """
    output_directory_path = Path('/app/output/simulation_runs')
    
    try:
        # Implementation currently disabled for safety
        # if output_directory_path.exists():
        #     shutil.rmtree(output_directory_path)
        #     assert not output_directory_path.exists(), "Output directory should be removed"
        pass
    except Exception as cleanup_error:
        print(f"Error cleaning output directory: {cleanup_error}")


def main() -> None:
    """
    Main entry point for the experiment execution system.
    
    Wrapper function that calls the main experiment runner and handles
    any top-level errors gracefully.
    
    Postconditions:
        - All experiments are attempted
        - System exits gracefully even if errors occur
    """
    try:
        run_all_experiments()
        print("All experiments completed successfully")
    except Exception as main_error:
        print(f"Error during experiment execution: {main_error}")
        raise


if __name__ == "__main__":
    main()