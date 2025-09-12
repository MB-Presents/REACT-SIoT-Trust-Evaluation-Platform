


from typing import Tuple
from git import Optional
import traci

from scenarios.canberra_case_study.core.networks import NetworkConstants


class NetworkAdapter:
    
    
    def get_edges(self) -> Optional[Tuple[str]]:
        """Get all edges in the network."""
        edges = traci.edge.getIDList()

        assert isinstance(edges, tuple)
        return edges 

    def get_junctions(self) -> Optional[Tuple[str]]:
        """Get all junctions in the network."""
        junctions = traci.junction.getIDList()
        assert isinstance(junctions, tuple)
        return junctions # type: ignore

    def get_lanes(self) -> Optional[Tuple[str]]:
        """Get all lanes in the network."""
        lanes = traci.lane.getIDList()
        assert isinstance(lanes, tuple)
        return lanes # type: ignore


    def get_lane_length(self, lane_id: str) -> float:
        """Get the length of a specific lane."""
        lane_length = traci.lane.getLength(lane_id)
        assert isinstance(lane_length, float)
        return lane_length