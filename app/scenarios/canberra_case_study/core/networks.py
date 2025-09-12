
from dataclasses import dataclass
from typing import Optional, Tuple

import traci



@dataclass
class NetworkConstants:
    EDGES : Optional[Tuple[str]] = None
    JUNCTIONS : Optional[Tuple[str]] = None
    LANES : Optional[Tuple[str]] = None

