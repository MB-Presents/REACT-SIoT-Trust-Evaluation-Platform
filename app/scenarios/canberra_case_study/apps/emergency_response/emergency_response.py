from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union



from core.models.devices.common import DeviceRecordType, DeviceType
from core.models.devices.genric_iot_device import DeviceBehaviour, GenericDevice

from core.simulation.logging import ObjectType


from core.simulation.simulation_context import SimulationContext
import utils.logging as logger


if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler
    from core.models.uniform.components.report import SendingPacket


class EmergencyResponseCenter(GenericDevice):

    def __init__(self, 
                 device_id : str,
                 device_type=DeviceType.EMERGENCY_CENTER, 
                 color : Tuple[float, float, float]=(0.0, 0.0, 0.0),
                 config : Dict[str, Union[Tuple[int, int, int], str]]={},
                 simulation_context : Optional[SimulationContext]= None ):

        super().__init__(
            device_id=device_id,
            device_type=DeviceType.EMERGENCY_CENTER,
            device_behaviour=DeviceBehaviour.TRUSTWORTHY,
            profile_config=config,
            color=(0, 0, 0),
            simulation_context=simulation_context)
        
        self.with_position((550.0, 900.0))
        

        
        # self.report_manager_component : ReportManager = ReportManager()
        
        # self.report_manager_component = EmergencyReportManagementService(self)
        # self.emergency_vehicle_management_service = EmergencyVehicleManagementService(self)

        
        # self.accident_handler = AccidentHandler()
        
        
        
    # def process_reports(self, report_manager: ReportManager, simulation_event_mananger: SimulationEventManager):
        
    #     unverified_reports = report_manager.get_unverified_reports_by_situation(Situation.EMERGENCY_REPORT)
    #     accident_report: SendingPacket

        

    #     for id, accident_report in unverified_reports.items():
    #         if not self.report_manager_component.is_emergency_report(accident_report):
    #             continue


    #         if not Settings.VERIFY_ACCIDENT_REPORT_AUTHENTICITY:
    #             accident_report.trustworthiness = VerificationState.AUTHENTIC
    
    #         self.report_manager_component.handle_unverified_requests(accident_report,  simulation_event_mananger)
    #         self.report_manager_component.handle_verified_report(accident_report, simulation_event_mananger)
            
    
    
    def to_dict(self)-> Dict[str, Any]:
        device_dict = super().to_dict()
        device_dict['record_type'] = DeviceRecordType.STATUS.name
        return device_dict


    def log(self):
    
        try:            
            message = self.to_dict()
            
            logger.info(ObjectType.EMERGENCY_CENTER.name, message, logger.LoggingBehaviour.STATUS)      
        
        except Exception as e:
            logger.error(ObjectType.EMERGENCY_CENTER.name, str(e))
            print(e)
            
        