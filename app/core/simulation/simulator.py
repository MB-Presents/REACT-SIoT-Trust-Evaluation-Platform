import os
from pathlib import Path
import uuid

from core.models import devices
from core.models.devices.common import DeviceType
from core.models.devices.device_handler import DevicesGroupHandler
from core.models.devices.factories.behaviour_factory import DeviceBehaviourFactory
from core.models.devices.factories.computation_factory import ComputationCapabilityFactory
from core.models.devices.factories.device_factory import DeviceFactory
from core.models.devices.factories.device_profile_facade import DeviceProfileFactory
from core.models.devices.factories.service_factory import ServiceFactory
from core.models.devices.genric_iot_device import GenericDevice
from core.models.uniform.components.report_models import ReportType
from core.simulation.adapter.manager_adapter import TraciAdapter

from core.simulation.event_bus.base_event import TimeStepEvent
from core.simulation.report_manager import ReportManager
from core.models.events.simulation_events import SimulationEventManager


import cProfile
from core.simulation.simulation_context import SimulationContext

def TAKE_SCREENSHOTS(self):
    raise NotImplementedError

from experiments.settings import Settings

from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings
from scenarios.canberra_case_study.apps.events.trigger import SimulationEventHandler
from scenarios.canberra_case_study.apps.handler import ScenarioHandler
from scenarios.canberra_case_study.core.networks import NetworkConstants
from trust.transaction_exchange_scheme.trust_inference_engine import TrustManagementEngine


from typing import Any, Dict, Optional, Tuple
from experiments.evaluation import recommendations

from experiments.evaluation import operational_evaluation as performance
from experiments.evaluation.operational_evaluation import PerformanceSimulationRun
import experiments.evaluation.recommendations as recommendations
import pstats
from pstats import SortKey

from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters
from uuid import UUID



import utils.pathfinder as pathfinder

import traci

sumoCmd = [
           'sumo',
        #    'sumo-gui',
           '-c', 'scenarios/canberra_case_study/data/osm.sumocfg',
        #    '--output-prefix','Experimente/Optimale_Anzahl/TIME_',
           '--start',
        #    '--tripinfo-output', 'tripinfo.xml',x
        #    '--summary', 'summary.xml',
        #    '--emission-output', 'emission.xml',
           '--no-warnings', 'true',
           '--quit-on-end', 
           '--delay', '0']


class Simulator:

    def __init__(self) -> None:
        
        self._initialize_sumo()

        self.context = SimulationContext()
        self._register_factories()
        
        self.devices = DevicesGroupHandler(context=self.context)
        self.report_manager : ReportManager = ReportManager(self.context)
        self.simulation_event_manager : SimulationEventManager = SimulationEventManager(self.context)
       
        self._initialize_device_groups()
        
        self.eventhandler  = SimulationEventHandler(self.context)
        self.eventhandler.toggle_logging_stdout(False)


        self.scenario = ScenarioHandler(self.context)
        self.tm_engine = TrustManagementEngine(self.context)
        
        
        self._subscribe_to_events()
        
        self.context._current_time
        
        

    def _initialize_sumo(self):
        traci_adapter = TraciAdapter()
    
        traci_adapter.start(sumoCmd)
        traci_adapter.subscription.subscribe_simulation()

        NetworkConstants.EDGES = traci_adapter.network.get_edges()
        NetworkConstants.JUNCTIONS = traci_adapter.network.get_junctions()
        NetworkConstants.LANES = traci_adapter.network.get_lanes()

        AccidentSettings.EMERGENCY_DROP_OFF_LENGTH = traci_adapter.network.get_lane_length(AccidentSettings.EMERGENCY_DROP_OFF_LANE)
        
        AccidentSettings.EMERGENCY_DROP_OFF_LANE_POSITION = AccidentSettings.EMERGENCY_DROP_OFF_LENGTH - 20

           
           
    def _subscribe_to_events(self):
        """Subscribe to simulation-wide events"""
        event_bus = self.context.get_event_bus()
        
        # Subscribe to time step events for logging and coordination
        event_bus.subscribe(TimeStepEvent, self._handle_time_step)
        event_bus.subscribe(TimeStepEvent, self._update_dynamic_devices)
            
    def _handle_time_step(self, event: TimeStepEvent):
        """Handle time step events for simulation coordination"""
        # Update current time
        time  = traci.simulation.getTime()
        assert isinstance(time, float), "Simulation time should be a float"
        self.context._current_time = time

        # Log time step if needed
        if event.step % 100 == 0:  # Log every 100 steps
            print(f"Simulation step: {event.step}, Time: {self.context._current_time:.2f}s")


            
            
            
            
            

    def _register_factories(self):
        """Register all factories with the simulation context"""

        service_factory = ServiceFactory(self.context)
        self.context.register_service_factory(service_factory)

        device_behaviour_factory = DeviceBehaviourFactory()
        self.context.register_device_behaviour_factory(device_behaviour_factory)

        device_profile_factory = DeviceProfileFactory()
        self.context.register_device_profile_factory(device_profile_factory)

        computation_capability_factory = ComputationCapabilityFactory()
        self.context.register_computation_capability_factory(computation_capability_factory)
        
    def _initialize_device_groups(self):
        """Initialize device groups"""
        device_types = [
            DeviceType.TRAFFIC_CAMERA,
            DeviceType.INDUCTION_LOOP, 
            DeviceType.TRAFFIC_LIGHT,
            DeviceType.EMERGENCY_CENTER,
            DeviceType.EMERGENCY_VEHICLE
        ]
        
        for device_type in device_types:
            self.devices.add_group(device_type)


    def _update_dynamic_devices(self):
        """Update dynamic devices (vehicles and smartphones) from TraCI"""
        # Subscribe to TraCI data for dynamic devices
        self.devices.subscribe(DeviceType.VEHICLE)
        self.devices.subscribe(DeviceType.TRAFFIC_CAMERA) 
        self.devices.subscribe(DeviceType.INDUCTION_LOOP)
        
        # Update device groups with new TraCI data
        self.devices.update_by_group(DeviceType.SMART_PHONE)
        self.devices.update_by_group(DeviceType.VEHICLE)
        self.devices.update_by_group(DeviceType.TRAFFIC_CAMERA)
        self.devices.update_by_group(DeviceType.INDUCTION_LOOP)
        self.devices.update_by_group(DeviceType.TRAFFIC_LIGHT)
    
    def _process_scenario_events(self):
        """Process scenario-specific events"""
        # Collision events
        self.eventhandler.trigger_collision(self.simulation_event_manager)
        self.eventhandler.update_collisions(self.simulation_event_manager)
        
        # Accident reporting events
        self.eventhandler.report_false_accident(
            self.simulation_event_manager, 
            self.report_manager
        )
        self.eventhandler.report_accidents(
            self.simulation_event_manager, 
            self.report_manager, 
            self.devices
        )
        
        # # TODO: Check if the emergency center is in update List.
        # emergency_center = self.devices.get_device("emergency_center")
        # if emergency_center:
        #     emergency_center.process_reports(
        #         self.report_manager, 
        #         self.simulation_event_manager
        #     )
        #     emergency_center.accident_handler.schedule_emergency_response(
        #         self.report_manager
        #     )
        
        # Traffic light priority requests
        self.eventhandler.request_fake_traffic_light_priority(
            self.report_manager, 
            self.simulation_event_manager
        )

    def _update_scenario_state(self):
        """Update scenario and logging state"""
        # Update scenario events and accidents
        self.scenario.update_events(self.simulation_event_manager)
        self.scenario.update_accidents(self.report_manager)
        
        # Log device states
        self.devices.log_by_group(DeviceType.EMERGENCY_VEHICLE)
        
        # Log managers
        self.scenario.log(self.report_manager)
        self.scenario.log(self.simulation_event_manager)
    
    def _process_trust_management(self):
        """Process trust management operations"""
        devices = self.devices.get_devices()
        assert all(isinstance(device, GenericDevice) and isinstance(key, str) for key, device in devices.items())
        
        # Exchange transactions between devices
        self.tm_engine.exchangeTransactions(devices) # type: ignore




    def _log_device_states(self):
        """Log all device group states"""
        device_types_to_log = [
            DeviceType.TRAFFIC_CAMERA,
            DeviceType.INDUCTION_LOOP,
            DeviceType.SMART_PHONE,
            DeviceType.VEHICLE,
            DeviceType.EMERGENCY_CENTER,
            DeviceType.TRAFFIC_LIGHT
        ]
        
        for device_type in device_types_to_log:
            self.devices.log_by_group(device_type)
    
    def _take_screenshot_if_needed(self):
        """Take simulation screenshot if GUI is enabled"""
        if hasattr(Settings, 'TAKE_SCREENSHOTS') and Settings.TAKE_SCREENSHOTS:
            screenshot_dir = pathfinder.get_simulation_data_screenshot_path(
                Settings.SELECTED_TRUST_MODEL, 
                Settings.EXPERIMENT_NAME, 
                Settings.SIMULATION_RUN_INDEX
            )
            screenshot_file_path = os.path.join(screenshot_dir, f"{self.context._current_time}.png")
            # traci.gui.screenshot("View #0", screenshot_file_path, 693, 540)

    def _simulation_step(self):
        """Execute one complete simulation step"""
        # Get current simulation time
        simulation_time = traci.simulation.getTime()
        assert isinstance(simulation_time, float)
        self.context._current_time = simulation_time
        
        # Publish time step event - all components will react
        step_number = int(simulation_time * 10)  # Assuming 0.1s time steps
        self.context.get_event_bus().publish(TimeStepEvent(
            event_id=str(uuid.uuid4()),
            timestamp=simulation_time
        ))
        
        # Update dynamic devices from TraCI
        self._update_dynamic_devices()
        
        # Update report manager
        self.report_manager.update()
        
        # Process scenario events
        self._process_scenario_events()
        
        # Update scenario state and logging
        self._update_scenario_state()
        
        # Process trust management
        self._process_trust_management()
        
        # Log all device states
        self._log_device_states()
        
        # Take screenshot if needed
        self._take_screenshot_if_needed()
        
        # Execute TraCI simulation step
        traci.simulationStep()
    
    def run(self) -> Tuple[PerformanceSimulationRun, Dict[Any,Any], Dict[Any,Any]]:
        """Run the complete simulation"""
        print("Starting traffic simulation...")
        
        try:
            # Main simulation loop
            while (
                self.context._current_time <= Settings.MAX_SIMULATION_DURATION and 
                not self.scenario.is_finished(self.report_manager, self.simulation_event_manager)
            ):
                self._simulation_step()
            
            # Evaluate simulation results
            accuracy_emergency_report = recommendations.evaluate(
                self.report_manager, 
                ReportType.EmergencyReport
            )
            accuracy_traffic_light = recommendations.evaluate(
                self.report_manager, 
                ReportType.TraffiCPriorityRequest
            )
            performance_application = performance.evaluate(self.report_manager)
            
            print("Simulation completed successfully!")
            
            return (performance_application, accuracy_emergency_report, accuracy_traffic_light)
        
        finally:
            # Always close TraCI connection
            traci.close()
    
    def get_simulation_statistics(self) -> dict:
        """Get comprehensive simulation statistics"""
        all_devices = self.devices.get_devices()
        device_counts = {}
        
        for device_type in DeviceType:
            device_counts[device_type.value] = len(
                self.devices.get_devices_by_group(device_type)
            )
        
        return {
            'total_devices': len(all_devices),
            'device_counts': device_counts,
            'simulation_time': self.context._current_time,
            'total_reports': len(self.report_manager.get_simulation_reports()) if hasattr(self.report_manager, 'get_simulation_reports') else 0
        }




def run_simulation() -> Tuple[PerformanceSimulationRun, Dict[Any,Any], Dict[Any,Any]] | None:
    """Run a single simulation instance"""
    try:
        simulator = Simulator()
        result = simulator.run()
        
        # Print simulation statistics
        stats = simulator.get_simulation_statistics()
        print(f"Simulation Statistics:")
        print(f"  Total devices: {stats['total_devices']}")
        print(f"  Final simulation time: {stats['simulation_time']:.2f}s")
        print(f"  Device breakdown:")
        for device_type, count in stats['device_counts'].items():
            if count > 0:
                print(f"    {device_type}: {count}")
        
        return result
        
    except Exception as e:
        print(f"Simulation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_experiment_run() -> Tuple[PerformanceSimulationRun, Dict[Any,Any], Dict[Any,Any]] | None:
    """Start experiment run with profiling"""
    result = None
    profiler = None
    
    try:
        # Set up profiling
        profile_path = pathfinder.get_profiler_path(
            Settings.SELECTED_TRUST_MODEL, 
            Settings.EXPERIMENT_NAME, 
            Settings.SIMULATION_RUN_INDEX
        )

        Path(profile_path).mkdir(parents=True, exist_ok=True)
        

        
        profiler = cProfile.Profile()
        print("Starting profiled simulation run...")
        
        # Run simulation with profiling
        result = profiler.runcall(run_simulation)
        
        print("Simulation run completed!")
        
    except Exception as e:
        print(f"Experiment run error: {e}")
        import traceback
        traceback.print_exc()
        result = None
    
    finally:
        if profiler:
            # Save profiling results
            try:
                output = os.path.join(profile_path, "output.dat")    
                profiler.dump_stats(output)
                
                # Generate different profiling reports
                output_time = os.path.join(profile_path, "output_time.txt")
                output_calls = os.path.join(profile_path, "output_calls.txt")
                output_cumulative_times = os.path.join(profile_path, "output_cumulative_times.txt")
                
                # Time-sorted stats
                with open(output_time, "w") as f:
                    p = pstats.Stats(output, stream=f)
                    p.sort_stats("time").print_stats()
                
                # Call count-sorted stats
                with open(output_calls, "w") as f:
                    p = pstats.Stats(output, stream=f)
                    p.sort_stats("calls").print_stats()
                
                # Cumulative time-sorted stats
                with open(output_cumulative_times, "w") as f:
                    p = pstats.Stats(output, stream=f)
                    p.sort_stats(SortKey.CUMULATIVE).print_stats()
                
                print(f"Profiling results saved to: {profile_path}")
                
            except Exception as e:
                print(f"Error saving profiling results: {e}")
    
    return result



# def start_experiment_run():
#     result = None
#     try:
        
#         profile_path = pathfinder.get_profiler_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
#         profiler = cProfile.Profile()
#         result = profiler.runcall(run_simulation)
        
#     except Exception as e:
#         print(e)
#         return None

    
#     finally:
        
#         output = os.path.join(profile_path, "output.dat")    
#         profiler.dump_stats(output)
        
#         output_time = os.path.join(profile_path, "output_time.txt")
#         output_calls = os.path.join(profile_path, "output_calls.txt")
#         output_cumulative_times = os.path.join(profile_path, "output_cumulative_times.txt")
        
        
#         with open(output_time, "w") as f:
#             p = pstats.Stats(output, stream=f)
#             p.sort_stats("time").print_stats()

#         with open(output_calls, "w") as f:
#             p = pstats.Stats(output, stream=f)
#             p.sort_stats("calls").print_stats()

#         with open(output_cumulative_times, "w") as f:
#             p = pstats.Stats(output, stream=f)
#             p.sort_stats(SortKey.CUMULATIVE).print_stats()
    
#     return result



# def run_simulation() -> Tuple[ReportManager, SimulationEventManager, PerformanceSimulationRun, dict, dict] : 

#     traci_adapter = TraciAdapter()
    
#     traci_adapter.start(sumoCmd)
#     traci_adapter.subscription.subscribe_simulation
    
#     # result = traci.start(sumoCmd)                   # port 5000
#     # traci.simulation.subscribe()


    


#     NetworkConstants.EDGES = traci_adapter.network.get_edges()
#     NetworkConstants.JUNCTIONS = traci_adapter.network.get_junctions()
#     NetworkConstants.LANES = traci_adapter.network.get_lanes()

#     AccidentSettings.EMERGENCY_DROP_OFF_LENGTH = traci_adapter.network.get_lane_length(AccidentSettings.EMERGENCY_DROP_OFF_LANE)
    
#     AccidentSettings.EMERGENCY_DROP_OFF_LANE_POSITION = AccidentSettings.EMERGENCY_DROP_OFF_LENGTH - 20


#     _ctx = SimulationContext()
#     devices: DevicesGroupHandler = DevicesGroupHandler(context=_ctx)

#     report_manager : ReportManager = ReportManager(devices)
#     simulation_event_manager : SimulationEventManager = SimulationEventManager(devices)
    
#     devices.add_group(DeviceType.TRAFFIC_CAMERA)
#     # devices.add_group(DeviceType.INDUCTION_LOOP)
#     # devices.add_group(DeviceType.SMART_PHONE)
#     # devices.add_group(DeviceType.VEHICLE)   
#     # devices.add_group(DeviceType.EMERGENCY_VEHICLE)
#     # devices.add_group(DeviceType.TRAFFIC_LIGHT)
#     # devices.add_group(DeviceType.EMERGENCY_CENTER)
    
    
    
#     # emergency_center : EmergencyResponseCenter = EmergencyResponseCenter(report_manager=report_manager,
#     #                                                                      simulation_event_manager=simulation_event_manager, 
#     #                                                                      devices=devices)

#     # traffic_cameras : Traffic_Camera_Manager = Traffic_Camera_Manager(devices)
#     # induction_loops : Induction_Loop_Manager = Induction_Loop_Manager(devices)
#     # smart_phones : Smart_Phone_Manager = Smart_Phone_Manager(devices)
#     # vehicles : Vehicle_Manager = Vehicle_Manager(devices)
#     # traffic_light_manager : TrafficLightManager = TrafficLightManager(devices)
    
    
    
    
#     # devices.add_group(DeviceType.VEHICLE, vehicles)
#     # devices.add_group(DeviceType.SMART_PHONE, smart_phones)
#     # devices.add_group(DeviceType.TRAFFIC_CAMERA, traffic_cameras)
#     # devices.add_group(DeviceType.INDUCTION_LOOP, induction_loops)
#     # devices.add_group(DeviceType.TRAFFIC_LIGHT, traffic_light_manager)
#     # devices.add_group(DeviceType.EMERGENCY_CENTER, emergency_center)
    
#     eventhandler  = SimulationEventHandler()
#     eventhandler.toggle_logging_stdout(False)
    
#     scenario = ScenarioHandler()
    
#     tm_engine = TrustManagementEngine()
    
#     TIME : float = ScenarioParameters.TIME
    
    
#     # while (ScenarioParameters.TIME <= Settings.MAX_SIMULATION_DURATION and not scenario.is_finished(report_manager,simulation_event_manager)) and ScenarioParameters.TIME <= 1000:
#     while TIME <= Settings.MAX_SIMULATION_DURATION and not scenario.is_finished(report_manager,simulation_event_manager):

#         simulation_time = traci.simulation.getTime()
#         assert isinstance(simulation_time, float)
#         TIME = simulation_time

#         devices.subscribe(DeviceType.VEHICLE)
#         devices.subscribe(DeviceType.TRAFFIC_CAMERA)
#         devices.subscribe(DeviceType.INDUCTION_LOOP)
        
        
#         devices.update_by_group(DeviceType.SMART_PHONE)
#         devices.update_by_group(DeviceType.VEHICLE)
#         devices.update_by_group(DeviceType.TRAFFIC_CAMERA)
#         devices.update_by_group(DeviceType.INDUCTION_LOOP)
#         devices.update_by_group(DeviceType.TRAFFIC_LIGHT)

#         report_manager.update()

#         # Scenario Events
#         eventhandler.trigger_collision(simulation_event_manager)
#         eventhandler.update_collisions(simulation_event_manager)
        
#         eventhandler.report_false_accident(simulation_event_manager, report_manager)
#         eventhandler.report_accidents(simulation_event_manager, report_manager, devices)

#         devices.get_device(key="emergency_center").process_reports(report_manager, simulation_event_manager)
#         devices.get_device(key="emergency_center").accident_handler.schedule_emergency_response(report_manager)
        
#         scenario.update_events(simulation_event_manager)
#         scenario.update_accidents(report_manager)
        
#         # Traffic Light System Event       
#         eventhandler.request_fake_traffic_light_priority(report_manager, simulation_event_manager)
#         traffic_light_manager.process_traffic_requests(report_manager,simulation_event_manager)
        
#         # scenario.log(emergency_center.emergency_vehicles_manager.get_emergency_vehicles())
#         devices.log_by_group(DeviceType.EMERGENCY_VEHICLE)
        
#         scenario.log(report_manager)
#         scenario.log(simulation_event_manager)
        
    
#         all_devices_dict = devices.get_devices()
#         # tm_engine.visualise_trust_network(all_devices_dict, is_transaction_exchange=False)
        
#         tm_engine.exchangeTransactions(all_devices_dict)
                
#         # DEBUG: Only requried as soon as I have a trust inference model
#         # tm_engine.visualise_trust_network(all_devices_dict, is_transaction_exchange=True)

#         devices.log_by_group(DeviceType.TRAFFIC_CAMERA)
#         devices.log_by_group(DeviceType.INDUCTION_LOOP)
#         devices.log_by_group(DeviceType.SMART_PHONE)
#         devices.log_by_group(DeviceType.VEHICLE)
#         devices.log_by_group(DeviceType.EMERGENCY_CENTER)
#         devices.log_by_group(DeviceType.TRAFFIC_LIGHT)
        
        
#         screenshot_dir = pathfinder.get_simulation_data_screenshot_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME, Settings.SIMULATION_RUN_INDEX)
#         screenshot_file_path = os.path.join(screenshot_dir, f"{TIME}.png")
#         # traci.gui.screenshot("View #0", screenshot_file_path,693, 540)
        
        
#         traci.simulationStep()
        
    
#     accuracy_emergency_report = recommendations.evaluate(report_manager, ReportType.EmergencyReport)
#     accuracy_traffic_light = recommendations.evaluate(report_manager, ReportType.TraffiCPriorityRequest)
#     performance_application = performance.evaluate(report_manager)
    
#     traci.close()

#     simulation_results = (performance_application, accuracy_emergency_report, accuracy_traffic_light)
    
#     return simulation_results




