"""
Shared types and data structures for SWIM Gossip implementation.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional

@dataclass
class NodeInfo:
    """Represents information about a node in the cluster."""
    node_id: str
    address: str
    port: int
    status: str = "alive"
    last_seen: float = field(default_factory=time.time)
    incarnation: int = 0
