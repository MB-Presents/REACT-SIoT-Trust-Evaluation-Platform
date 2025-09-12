
from __future__ import annotations
from typing import TYPE_CHECKING, Dict


from typing import Dict, Tuple
from core.models.uniform.sensed_object_record import SensedDeviceRecord
from scenarios.canberra_case_study.core.scenario_config import ScenarioParameters

if TYPE_CHECKING:
    from core.models.devices.genric_iot_device import GenericDevice

class ObjectSensorRecords:

    def __init__(self):
        self.records : Dict[Tuple[float, str, str], SensedDeviceRecord] = {}

    def add_record(self, service_provider : GenericDevice, observed_device : GenericDevice):
        
        record = SensedDeviceRecord(service_provider, observed_device)
        key = (ScenarioParameters.TIME, record.service_provider_id, record.sensed_device_id)
        self.records[key] = record
        

    def get_records(self):
        return self.records
    
    
    def get_records_as_dict(self):
        return {key: record.__dict__ for key, record in self.records.items()}
