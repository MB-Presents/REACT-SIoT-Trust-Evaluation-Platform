
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from data_models.report_management.report.report_models import AuthenticityRole, ReporterType






if TYPE_CHECKING:
    from data_models.iot_devices.vehicle import Vehicle
    from data_models.iot_devices.smart_phone import SmartPhone

from typing import List, Union
from data.simulation.scenario_constants import Constants as sc
from traci import poi 




class SendersEntity:

    
    def __init__(self, reporter: Union[SmartPhone,Vehicle], authenticity : AuthenticityRole, reporting_time : float) -> None:
        
        self.device = reporter
        
        self.id = self.device._id
        self.poi_id : str = self.id + "_" + sc.TIME_STRING
        self.authenticity : AuthenticityRole = authenticity
        self.reporting_time : float = reporting_time
        
        if self.device._id.startswith("ped"):
            reporter_type = ReporterType.PEDESTRIAN
        else:
            reporter_type = ReporterType.VEHICLE    
        
        
        self.type = reporter_type
        
    def draw_reporter_location(self, authenticity=AuthenticityRole.AUTHENTIC) -> None:
            
        type: str = 'accident_reporter_location'
        
        
        
        x : float = self.device._position[0]
        y: float = self.device._position[1]
        
        # x : float = self.location[0]
        # y: float = self.location[1]
        
        if authenticity == AuthenticityRole.AUTHENTIC:        
            color : List[Tuple] = (0.0, 255.0, 0.0, 255.0)
        
        if authenticity == AuthenticityRole.UNAUTHENTIC:
            color = (0.0, 255.0, 0.0, 255.0)
        
        if self.poi_id not in poi.getIDList():
            poi.add(self.poi_id,x,y,color,type, layer=5, width=50000,height=50000)


