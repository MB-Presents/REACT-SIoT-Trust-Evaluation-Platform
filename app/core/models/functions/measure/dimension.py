from __future__ import annotations
from typing import Dict, TYPE_CHECKING



import numpy as np
from core.models.devices.common import DeviceType

from core.models.interfaces.function import IFunction

if TYPE_CHECKING:
    from core.models.devices.vehicle import Vehicle
    

class ObjectDimensionFunction(IFunction):
    
    def __init__(self):
        from core.models.devices.device_handler import DevicesGroupHandler
        self.device_group_handler = DevicesGroupHandler()
    
    
    def execute(self, veh_id) -> Dict[str, float]:


        vehicles: Dict[str, Vehicle] = self.device_group_handler.get_devices_by_group(DeviceType.VEHICLE)


        if veh_id not in vehicles:
            return {'width': np.nan, 'length': np.nan, 'height': np.nan}
        
        vehicle = vehicles[veh_id]
        return {
            'width': vehicle._width,
            'length': vehicle._length,
            'height': vehicle._height
        }
        