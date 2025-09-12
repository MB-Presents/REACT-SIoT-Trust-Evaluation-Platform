from __future__ import annotations
import sys
from typing import TYPE_CHECKING, Optional
from scenarios.canberra_case_study.apps.emergency_response.emergency_vehicle import EmergencyVehicle
from traci import vehicle, simulation
# import utils.logging as logger
from loguru import logger as logger

if TYPE_CHECKING:
    from core.models.uniform.components.report import SendingPacket
    from core.simulation.report_manager import ReportManager
    from core.models.devices.vehicle import Vehicle

class LoggingUtil:
    """Handles logging for accident handling operations."""
    def __init__(self):
        self._logger = logger.bind(context="accident_handler")
        self._stdout_handler_id: Optional[int] = None

    def log_dispatch(self, emergency_vehicle: EmergencyVehicle, accident_report: SendingPacket) -> None:
        self._logger.info(
            f"{simulation.getTime()} \t | Emergency Vehicle DISPATCHED | "
            f"{emergency_vehicle.emergency_veh_id} is heading to accident at lane {accident_report.object_of_interest.lane_id}"
        )

    def log_hospital_arrival(self, emergency_veh_id: str) -> None:
        self._logger.info(
            f"Emergency Vehicle {emergency_veh_id} is heading to hospital from lane "
            f"{vehicle.getLaneID(emergency_veh_id)} at time {simulation.getTime()}"
        )

    def toggle_logging_stdout(self, activate: bool = True) -> None:
        if activate and self._stdout_handler_id is None:
            self._stdout_handler_id = logger.add(
                sys.stdout, filter=lambda record: "context" in record["extra"] and record["extra"]["context"] == "accident_handler"
            )
        elif not activate and self._stdout_handler_id is not None:
            logger.remove(self._stdout_handler_id)
            self._stdout_handler_id = None