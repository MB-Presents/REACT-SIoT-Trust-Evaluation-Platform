from __future__ import annotations
from enum import Enum, auto
from typing import TYPE_CHECKING

import data_models.serializer as serializer
from network_manager import network_manager


if TYPE_CHECKING:
    from data_models.iot_devices.device_handler import Devices_Group_Handler
    from data_models.report_management.report.report import SendingPacket
    from data_models.iot_devices.genric_iot_device import GenericDevice
    from data_models.events.simulation_events import SimulationEventManager





def get_sensory_parameters(report : SendingPacket):

    service_providers_candidates = network_manager.get_service_provider_candidates(report)
    selected_service_provider = serializer.get_service_provider_status(service_providers_candidates)
    service_provider_matrix = serializer.uniform_data_models(selected_service_provider)

    return service_provider_matrix