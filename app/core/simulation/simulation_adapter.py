from __future__ import annotations
from typing import TYPE_CHECKING

from git import Object
import traci
from core.simulation.logging import ObjectType
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
from scenarios.canberra_case_study.apps.emergency_response.constants import AccidentSettings
from traci import vehicle, simulation, TraCIException
import utils.logging as logger

if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket
    from core.simulation.report_manager import ReportManager
    from core.models.devices.vehicle import Vehicle

class SimulationAdapter:
    """Handles interactions with the TraCI simulation API."""
    @staticmethod
    def set_vehicle_route(emergency_vehicle: EmergencyVehicle, accident_report: SendingPacket) -> None:
        try:
            vehicle.changeTarget(emergency_vehicle.emergency_veh_id, accident_report.object_of_interest.edge_id)
            emergency_vehicle.set_stop(
                accident_report.object_of_interest.edge_id,
                accident_report.object_of_interest.lane_position,
                laneIndex=0,
                parking_duration=AccidentSettings.PARKING_TIME_ACCIDENT
            )
        except TraCIException as e:
            logger.error(ObjectType.EMERGENCY_CENTER.name, f"TraCI error setting route for vehicle {emergency_vehicle.emergency_veh_id}: {str(e)}")
            raise

    @staticmethod
    def set_hospital_route(emergency_vehicle: EmergencyVehicle, emergency_drop_off: str, emergency_drop_off_position: float, parking_time: int) -> None:
        try:
            
            assert emergency_drop_off != emergency_vehicle._edge_id, "Emergency vehicle is already at the emergency drop-off location."
            assert parking_time > 0, "Parking time must be a positive integer."
            # assert 0 <= emergency_drop_off_position <= 1000, "Lane position must be between 0 and 1000 meters."
            
            # if emergency_vehicle._edge_id == emergency_drop_off:
                
            #     vehicle.changeTarget(emergency_vehicle.emergency_veh_id, "333934001")
                
            #     route = simulation.findRoute(emergency_vehicle.emergency_veh_id, emergency_vehicle._edge_id, "333934001", "passenger")
            #     vehicle.setRoute(emergency_vehicle.emergency_veh_id, route.edges + [emergency_drop_off])
            # else:
            vehicle.changeTarget(emergency_vehicle.emergency_veh_id, emergency_drop_off)
            emergency_vehicle.set_stop(selected_edge=emergency_drop_off, lane_position=emergency_drop_off_position, laneIndex=0, parking_duration=parking_time)
        except TraCIException as e:
            logger.error(ObjectType.EMERGENCY_CENTER.name, f"TraCI error setting hospital route for vehicle {emergency_vehicle.emergency_veh_id}: {str(e)}")
            raise




    @staticmethod
    def get_distance_to_hospital(accident: SendingPacket) -> float:
        try:
            distance = simulation.getDistanceRoad(
                edgeID1=accident.object_of_interest.edge_id,
                pos1=accident.object_of_interest.lane_position,
                edgeID2=AccidentSettings.EMERGENCY_DROP_OFF,
                pos2=AccidentSettings.EMERGENCY_DROP_OFF_LANE_POSITION
            )
            
            assert isinstance(distance, float), "Distance to hospital must be a float."
            assert distance >= 0, "Distance to hospital cannot be negative."
            
            return distance
            
        except TraCIException as e:
            logger.error(ObjectType.EMERGENCY_CENTER.name, f"TraCI error calculating distance to hospital: {str(e)}")
            raise

    @staticmethod
    def get_distance_to_accident(accident: SendingPacket) -> float:
        try:
            distance = simulation.getDistanceRoad(
                edgeID1=AccidentSettings.EMERGENCY_DROP_OFF,
                pos1=AccidentSettings.EMERGENCY_DROP_OFF_LANE_POSITION,
                edgeID2=accident.object_of_interest.edge_id,
                pos2=accident.object_of_interest.lane_position
            )
            assert isinstance(distance, float), "Distance to accident must be a float."
            assert distance >= 0, "Distance to accident cannot be negative."
            return distance
            
            
        except TraCIException as e:
            logger.error(ObjectType.EMERGENCY_CENTER.name, f"TraCI error calculating distance to accident: {str(e)}")
            raise