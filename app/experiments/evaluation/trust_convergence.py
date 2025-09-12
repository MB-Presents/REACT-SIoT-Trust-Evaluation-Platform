from typing import Tuple
from core.models.events.simulation_events import SimulationEventManager
from core.models.devices.device_handler import DevicesGroupHandler
from core.models.devices.genric_iot_device import GenericDevice
from core.models.uniform.components.report_models import ReportType
from core.simulation.report_manager import ReportManager
from trust.data_models.relationship.data_models.relationship import Relationship
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters










def compute_number_of_overall_network_relationship_over_time(devices : DevicesGroupHandler, report_manager : ReportManager, simulation_event : SimulationEventManager, time_step : int):
    
    device_dict = devices.get_devices()
    
    average_relationship_number_per_time = {}
    
    
    trust_convergence_metrics_per_time_step = {}
    
    # Measured in trust score variance / per standard deviation
    average_trust_stability = {}
    
    # Measures in stablity of trust over time considering frequency and recency of interactions
    average_trsut_stability_index = {}

    # tiem to trust convergence measured in to reach a state of equilibirum of a predefined threshold of stablity
    average_trust_convergence_time = {}
    
    # Measure the density of the network with respect to trust
    average_network_density_with_respect_to_trust = {}


    
    device_id : str
    device : GenericDevice
    
    
    
    for device_id, device in device_dict.items():
            
        trust_convergence_metrics_per_time_step[device_id] = {}
        
        trust_convergence_metrics = get_trust_convergence_metrics(device, simulation_event, time_step)
        
            
            
            
    
    
    
    
    # for time in range(0, ScenarioParameters.TIME, 1):
        
    #     relationships_per_time_step[time] = {}
        
    #     for device_id, device in device_dict.items():
            
    #         relationships_per_time_step[time][device_id] = {}
            
            
    #         relationships_per_time_step[time][device_id][Relationship.TRUST] = {}
            
            
            
    #         for device_id, device in device_dict.items():
        
    #             relationships_per_time_step[time] = {}
        
            
    #             for transation_id, transaction in device.transaction_controller.transaction_manager.trust_transactions.items():
            

        
def get_trust_convergence_metrics(device: GenericDevice):
    
    
    
    
    trust_convergence_metrics = {}
    
    trust_convergence_metrics["trust_stability"] = get_trust_stability(transaction, simulation_event, time_step)
    trust_convergence_metrics["trust_stability_index"] = get_trust_stability_index(transaction, simulation_event, time_step)
    trust_convergence_metrics["trust_convergence_time"] = get_trust_convergence_time(transaction, simulation_event, time_step)
    trust_convergence_metrics["network_density_with_respect_to_trust"] = get_network_density_with_respect_to_trust(transaction, simulation_event, time_step)
    
    return trust_convergence_metrics
            