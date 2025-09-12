from threading import Lock
from typing import Optional
from core.models.devices.common import DeviceType

class DeviceIDGenerator:
    """
    Singleton class to generate unique device map IDs in a thread-safe manner.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(DeviceIDGenerator, cls).__new__(cls)
            cls._instance._counter = 0  # Initialize counter
        return cls._instance

    def get_next_id(self) -> int:
        """
        Generate the next unique ID in a thread-safe way.
        Returns: A unique integer ID.
        """
        with self._lock:
            self._counter += 1
            return self._counter