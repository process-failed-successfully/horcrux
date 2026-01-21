from dataclasses import dataclass
from typing import Optional

@dataclass
class NodeInfo:
    """
    Information about a node in the cluster.
    """
    node_id: str
    address: str
    port: int
    status: str = "alive"
    incarnation: int = 1
    last_seen: float = 0.0
    failed_pings: int = 0
