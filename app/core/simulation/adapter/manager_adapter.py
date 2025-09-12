from typing import List, Tuple
import traci

from core.simulation.adapter.network_adapter import NetworkAdapter
from core.simulation.adapter.subscription_adapter import SubscriptionAdapter


class TraciAdapter:

    _instance = None
    _is_initialized = False


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.subscription = SubscriptionAdapter()
        self.network = NetworkAdapter()


    def start(self, command: List[str]) -> Tuple[str]:

        assert all(isinstance(arg, str) for arg in command), "All command arguments must be strings."
        result = traci.start(command)
        
        assert isinstance(result, tuple), "The result of traci.start() must be a tuple."
        assert result is not None, "The result of traci.start() must be empty."
        
        return result  # type: ignore
    
    