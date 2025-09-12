
from typing import List, Tuple







class ObjectOfInterest:

    object_id: str 
    location: Tuple[float, float]
    edge_id: str 
    lane_position: float 
    lane_id: str 

    def __init__(self, object_id: str, location: Tuple[float, float], edge_id: str = "", lane_position: float = 0.0, lane_id: str = "") -> None:

        self.object_id: str = object_id
        self.location: Tuple[float, float] = location
        self.edge_id: str = edge_id
        self.lane_position: float = lane_position
        self.lane_id: str = lane_id

        pass

   