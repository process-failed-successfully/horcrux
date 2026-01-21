from enum import Enum
from typing import Dict, Any

class NodeStatus(Enum):
    """Status of a node in the gossip network."""
    ALIVE = "alive"
    SUSPECT = "suspect"
    FAILED = "failed"

class Node:
    """Represents a node in the gossip network."""

    def __init__(self, node_id: str, address: str, port: int, status: NodeStatus = NodeStatus.ALIVE, last_seen: float = None):
        """
        Initialize a node.

        Args:
            node_id: Unique identifier for the node
            address: Network address of the node
            port: Port number of the node
            status: Status of the node (default: ALIVE)
            last_seen: Timestamp of last contact (default: current time)
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.status = status
        self.last_seen = last_seen if last_seen is not None else time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "status": self.status.value,
            "last_seen": self.last_seen
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Create node from dictionary representation."""
        return cls(
            node_id=data["node_id"],
            address=data["address"],
            port=data["port"],
            status=NodeStatus(data["status"]),
            last_seen=data["last_seen"]
        )

    def __str__(self) -> str:
        return f"Node({self.node_id}, {self.address}:{self.port}, {self.status.value})"

    def __repr__(self) -> str:
        return self.__str__()

class Message:
    """Represents a message in the gossip network."""

    def __init__(self, sender_id: str, message_type: str, payload: Dict[str, Any]):
        """
        Initialize a message.

        Args:
            sender_id: ID of the sending node
            message_type: Type of message
            payload: Message payload
        """
        self.sender_id = sender_id
        self.message_type = message_type
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "sender_id": self.sender_id,
            "message_type": self.message_type,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary representation."""
        return cls(
            sender_id=data["sender_id"],
            message_type=data["message_type"],
            payload=data["payload"]
        )
