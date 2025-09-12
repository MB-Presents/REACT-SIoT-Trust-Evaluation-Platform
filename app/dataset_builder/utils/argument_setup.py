
from dataclasses import dataclass, field
import os

@dataclass
class Args:
    BUILD_DEVICE: str = field(default_factory=lambda: os.getenv("BUILD_DEVICE", "local"))
    data: str = 'wikipedia'
    bs: int = 32
    prefix: str = 'tgn-attn'
    n_degree: int = 10
    n_head: int = 2
    n_epoch: int = 25
    n_layer: int = 1
    lr: float = 0.0001
    patience: int = 5
    n_runs: int = 1
    drop_out: float = 0.1
    gpu: int = 0
    node_dim: int = 100
    time_dim: int = 100
    backprop_every: int = 1
    use_memory: bool = True
    embedding_module: str = "graph_attention"
    message_function: str = "identity"
    memory_updater: str = "gru"
    aggregator: str = "last"
    memory_update_at_end: bool = False
    message_dim: int = 100
    memory_dim: int = 20
    different_new_nodes: bool = False
    uniform: bool = False
    randomize_features: bool = False
    use_destination_embedding_in_message: bool = False
    use_source_embedding_in_message: bool = False
    dyrep: bool = False
    include_artificial_negative_samples: bool = False

    def __post_init__(self):
        if self.BUILD_DEVICE == "server":
            self.n_epoch = 1000