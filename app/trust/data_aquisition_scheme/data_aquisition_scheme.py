from __future__ import annotations
from enum import Enum, auto
from typing import TYPE_CHECKING

from core.models.uniform.components.report import SendingPacket
from core.simulation import network
import core.utils.serializer as serializer




if TYPE_CHECKING:
    from core.models.devices.device_handler import DevicesGroupHandler
    
    from core.models.devices.genric_iot_device import GenericDevice
    from core.models.events.simulation_events import SimulationEventManager





def get_sensory_parameters(report : SendingPacket):

    service_providers_candidates = network.get_service_provider_candidates(report)
    selected_service_provider = serializer.get_service_provider_status(service_providers_candidates)
    service_provider_matrix = serializer.uniform_data_models(selected_service_provider)

    return service_provider_matrix