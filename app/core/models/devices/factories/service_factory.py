
from __future__ import annotations
# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Any, Generic, Union
    


from typing import Dict
from core.models.interfaces.service_registry import IServiceRegistry
from core.models.devices.common import DeviceType, Service
from core.simulation.simulation_context import SimulationContext


if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.interfaces.service import IService
    from core.models.devices.traffic_camera import TrafficCamera
    from core.models.devices.smart_phone import SmartPhone
    from core.models.devices.vehicle import Vehicle
    from core.models.devices.induction_loop import InductionLoop
    from core.models.devices.traffic_light import TrafficLightSystem
    from scenarios.canberra_case_study.apps.emergency_response.emergency_response import EmergencyResponseCenter
    from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
    from core.models.services.base_service import BaseService
    
    

from core.models.services.induction_loop.vehicle_object_count_service import VehicleObjectCountService
from core.models.services.phones.object_position_detection import ObjectPositionDetectionService
from core.models.services.phones.objects_proximity_service import ObjectProximityService
from core.models.services.traffic_camera.vehicle_detection_service import VehicleDetectionService
from core.models.services.vehicle.vehicle_object_detection import VehicleObjectDetectionService
from core.models.services.vehicle.vehicle_status_service import VehicleStatusService
from core.models.services.emergency_center.emergency_report_management_service import EmergencyReportManagementService
from core.models.services.emergency_center.vehicle_management_service import EmergencyManagementService

class ServiceFactory:
    

    def __init__(self, simulation_context: SimulationContext):
        self.simulation_context = simulation_context
        self._service_classes = self._register_service_classes()
        
        
    def _register_service_classes(self) -> Dict[DeviceType, Dict[Service, Any]]:
        self._services_profiles : Dict[DeviceType, Dict[Service, BaseService]] = {
            DeviceType.VEHICLE: {
                Service.Object_Detection_Service: VehicleObjectDetectionService(),
                Service.Vehicle_Status_Service: VehicleStatusService()

            },
            DeviceType.SMART_PHONE: {
                Service.Object_Position_Service : ObjectPositionDetectionService(),
                Service.Object_Proximity_Service : ObjectProximityService()
            },
            DeviceType.INDUCTION_LOOP: {
                Service.Inductive_Vehicle_Detection_Service : VehicleObjectCountService()
            },
            DeviceType.TRAFFIC_CAMERA: {
                Service.Vehicle_Detection_Service : VehicleDetectionService()
            },
            DeviceType.EMERGENCY_VEHICLE: {
                Service.Object_Detection_Service: VehicleObjectDetectionService(),
                Service.Vehicle_Status_Service: VehicleStatusService()
            },
            DeviceType.EMERGENCY_CENTER: {
                # Add services specific to Emergency Response Center if any
                Service.Emergency_Report_Management_Service: EmergencyReportManagementService(),
                Service.Emergency_Vehicle_Management_Service: EmergencyManagementService()
            },
            DeviceType.TRAFFIC_LIGHT: {
                # Add services specific to Traffic Light System if any
            }
            

        }
        
        return self._services_profiles

    def create_services_for_device(self, device: GenericDevice) -> Dict[Service, IService]:
        """Create service instances with dependency injection"""
        device_type = device.get_device_type()
        service_classes = self._service_classes.get(device_type, {})
        
        services = {}
        for service_type, service_class in service_classes.items():
            # Inject context into service constructor
            service_instance = service_class(self.simulation_context, device)
            services[service_type] = service_instance
            
        return services
        

