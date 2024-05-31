from __future__ import annotations
import random
from typing import TYPE_CHECKING, Dict


import itertools
from data_models.iot_devices.common import DeviceRecordType, DeviceType
from data_models.iot_devices.genric_iot_device import DeviceBehaviour, GenericDevice
from data_models.report_management.report.report_models import Situation
from data_models.events.simulation_events import SimulationEventManager, VerificationState
from data_models.simulation.logging import ObjectType
from experiments.settings import Settings
from scenario.emergency_response.accident_handler import AccidentHandler
from data_models.services.report_manager_unit import ReportManagementComponent

from scenario.emergency_response.emergency_vehicle import EmergencyVehicleManager
import utils.logging as logger

import data.simulation.dummy_data as emergency_profiles

if TYPE_CHECKING:
    from data_models.iot_devices.device_handler import Devices_Group_Handler
    from data_models.report_management.report.report import SendingPacket
    from data_models.report_management.report_manager import ReportManager


class EmergencyResponseCenter(GenericDevice):

    authenticity_evidence_counter: int = itertools.count()

    def __init__(self, report_manager: ReportManager, simulation_event_manager: SimulationEventManager, devices):
        
        
        super().__init__(   device_id="Emergency Response",
                            position=[550.0, 900.0], 
                            device_type=DeviceType.EMERGENCY_CENTER, 
                            device_behaviour=DeviceBehaviour.TRUSTWORTHY,
                            manufacturer='Motorola Solutions',
                            model='Motorola Center 1',
                            firmware_version='1.0.0',
                            hardware_version='1.0.0',
                            serial_number='123456789',
                            date_of_manufacture='2020-01-01',
                            last_maintenance_date='2020-01-01',
                            next_maintenance_date='2020-01-01',
                            color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                         )
        
        
        # emergency_profiles.device_profiles['emergency_center']
        self._id = "Emergency Response"    
        self.position = [550.0, 900.0]
        
        self.devices : Devices_Group_Handler = devices
        
        self.report_manager_component = ReportManagementComponent(self,devices)
        self.emergency_vehicles_manager : EmergencyVehicleManager = EmergencyVehicleManager(devices)
        
        self.report_manager = report_manager
        self.simulation_event_manager = simulation_event_manager
        self.accident_handler = AccidentHandler(self.emergency_vehicles_manager,self.report_manager, simulation_event_manager)
        
        
        
    def process_reports(self, report_manager: ReportManager, simulation_event_mananger: SimulationEventManager):
        
        unverified_reports = report_manager.get_unverified_reports_by_situation(Situation.EMERGENCY_REPORT)
        accident_report: SendingPacket

        for id, accident_report in unverified_reports.items():
            if not self.report_manager_component.is_emergency_report(accident_report):
                continue


            if not Settings.VERIFY_ACCIDENT_REPORT_AUTHENTICITY:
                accident_report.trustworthiness = VerificationState.AUTHENTIC
    
            self.report_manager_component.handle_unverified_requests(accident_report,  simulation_event_mananger)
            self.report_manager_component.handle_verified_report(accident_report, simulation_event_mananger)
            
    
    
    def to_dict(self):
        device_dict = super().to_dict()
        device_dict['record_type'] = DeviceRecordType.STATUS.name
        return device_dict


    def log(self):
    
        try:            
            message = self.to_dict()
            
            logger.info(ObjectType.EMERGENCY_CENTER, message, logger.LoggingBehaviour.STATUS)      
        
        except Exception as e:
            logger.error(e)
            print(e)
            
        