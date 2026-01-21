"""
Types for SWIM Gossip Provider.
"""

import time
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class NodeStatus(Enum):
    """Status of a node in the gossip network."""
    ALIVE = "alive"
    SUSPECT = "suspect"
    FAILED = "failed"

@dataclass
class Node:
    """
    Represents a node in the gossip network.
    """
    node_id: str
    address: str
    port: int
    last_seen: float = None
    is_alive: bool = True
    incarnation: int = 0
    status: NodeStatus = NodeStatus.ALIVE

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.last_seen is None:
            self.last_seen = time.time()

    @property
    def id(self) -> str:
        """Alias for node_id for backward compatibility."""
        return self.node_id

    def to_dict(self):
        """Convert node to dictionary."""
        return {
            'node_id': self.node_id,
            'address': self.address,
            'port': self.port,
            'last_seen': self.last_seen,
            'is_alive': self.is_alive,
            'incarnation': self.incarnation,
            'status': self.status.value
        }

    @classmethod
    def from_dict(cls, data):
        """Create node from dictionary."""
        return cls(
            node_id=data['node_id'],
            address=data['address'],
            port=data['port'],
            last_seen=data.get('last_seen', time.time()),
            is_alive=data.get('is_alive', True),
            incarnation=data.get('incarnation', 0),
            status=NodeStatus(data.get('status', 'alive'))
        )

@dataclass
class Message:
    """
    Represents a gossip message.
    """
    sender: Node
    target: Optional[Node] = None
    message_type: str = "gossip"
    payload: Optional[dict] = None
    timestamp: float = None

    def __post_init__(self):
        """Initialize timestamp after creation."""
        if self.timestamp is None:
            self.timestamp = time.time()
