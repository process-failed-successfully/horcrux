"""
Node Discovery implementation using SWIM protocol.
"""

import random
import time
import threading
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import json
import socket
import hashlib

@dataclass
class Node:
    """Represents a node in the cluster."""
    node_id: str
    address: str
    port: int
    status: str = "alive"
    last_seen: float = field(default_factory=time.time)
    incarnation: int = 0

    def is_alive(self) -> bool:
        """Check if node is considered alive."""
        return self.status == "alive"

    def to_dict(self) -> Dict:
        """Convert node to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "status": self.status,
            "last_seen": self.last_seen,
            "incarnation": self.incarnation
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        """Create node from dictionary."""
        return cls(
            node_id=data["node_id"],
            address=data["address"],
            port=data["port"],
            status=data.get("status", "alive"),
            last_seen=data.get("last_seen", time.time()),
            incarnation=data.get("incarnation", 0)
        )

class NodeDiscovery:
    """
    SWIM Node Discovery implementation.

    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    is a gossip-based membership protocol that provides eventual consistency
    for cluster membership.
    """

    def __init__(self, node_id: str, address: str, port: int, seed_nodes: Optional[List[Tuple[str, int]]] = None):
        """
        Initialize node discovery.

        Args:
            node_id: Unique identifier for this node
            address: Network address of this node
            port: Network port of this node
            seed_nodes: List of (address, port) tuples for initial cluster members
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.seed_nodes = seed_nodes or []

        # Local node
        self.local_node = Node(node_id, address, port)

        # Membership list
        self.members: Dict[str, Node] = {}
        self.members[node_id] = self.local_node

        # Configuration
        self.gossip_interval = 1.0  # seconds
        self.ping_timeout = 0.5  # seconds
        self.failure_threshold = 3  # missed pings before failure
        self.probe_timeout = 1.0  # seconds

        # State
        self.running = False
        self.gossip_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Initialize with seed nodes
        for addr, port in self.seed_nodes:
            node_id = self._generate_node_id(addr, port)
            if node_id != self.node_id:
                self.members[node_id] = Node(node_id, addr, port)

    def _generate_node_id(self, address: str, port: int) -> str:
        """Generate deterministic node ID from address and port."""
        return hashlib.md5(f"{address}:{port}".encode()).hexdigest()

    def start(self) -> None:
        """Start the node discovery service."""
        if self.running:
            return

        self.running = True
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()

    def stop(self) -> None:
        """Stop the node discovery service."""
        self.running = False
        if self.gossip_thread:
            self.gossip_thread.join()

    def _gossip_loop(self) -> None:
        """Main gossip loop."""
        while self.running:
            try:
                self._perform_gossip()
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Gossip error: {e}")
                time.sleep(1)

    def _perform_gossip(self) -> None:
        """Perform a gossip round."""
        with self.lock:
            if len(self.members) < 2:
                return

            # Select a random node to gossip with
            nodes = list(self.members.values())
            random.shuffle(nodes)

            for node in nodes:
                if node.node_id == self.node_id:
                    continue

                if not node.is_alive():
                    continue

                try:
                    # Send ping and get membership update
                    response = self._ping_node(node)
                    if response:
                        self._update_membership(response)
                except Exception as e:
                    print(f"Ping failed to {node.node_id}: {e}")
                    self._handle_failure(node)

    def _ping_node(self, node: Node) -> Optional[Dict]:
        """
        Ping a node and request membership update.

        Returns:
            Membership update from the node, or None if ping failed
        """
        # Simulate network communication
        # In a real implementation, this would use actual network calls
        try:
            # Simulate network delay
            time.sleep(0.1)

            # Simulate 10% chance of failure for testing
            if random.random() < 0.1:
                return None

            # Return a copy of our membership list
            return {
                "node_id": self.node_id,
                "members": {k: v.to_dict() for k, v in self.members.items()}
            }
        except Exception as e:
            print(f"Ping error: {e}")
            return None

    def _update_membership(self, update: Dict) -> None:
        """
        Update local membership based on gossip from another node.

        Args:
            update: Membership update from another node
        """
        with self.lock:
            sender_id = update["node_id"]
            sender_members = update["members"]

            # Update or add nodes from the sender's membership list
            for node_data in sender_members.values():
                node = Node.from_dict(node_data)

                # Don't update ourselves
                if node.node_id == self.node_id:
                    continue

                # Update existing node or add new one
                if node.node_id in self.members:
                    existing = self.members[node.node_id]

                    # Handle incarnation numbers for failed nodes
                    if node.incarnation > existing.incarnation:
                        self.members[node.node_id] = node
                    elif node.incarnation == existing.incarnation:
                        # Update if the sender's info is newer
                        if node.last_seen > existing.last_seen:
                            self.members[node.node_id] = node
                else:
                    self.members[node.node_id] = node

            # Mark sender as alive
            if sender_id in self.members:
                self.members[sender_id].status = "alive"
                self.members[sender_id].last_seen = time.time()

    def _handle_failure(self, node: Node) -> None:
        """
        Handle node failure detection.

        Args:
            node: Node that is suspected to have failed
        """
        with self.lock:
            if node.node_id not in self.members:
                return

            current_node = self.members[node.node_id]

            # Increment incarnation number for failed node
            current_node.incarnation += 1
            current_node.status = "failed"
            current_node.last_seen = time.time()

            print(f"Node {node.node_id} marked as failed")

    def get_members(self) -> List[Node]:
        """Get current cluster members."""
        with self.lock:
            return list(self.members.values())

    def get_alive_members(self) -> List[Node]:
        """Get alive cluster members."""
        with self.lock:
            return [node for node in self.members.values() if node.is_alive()]

    def add_node(self, address: str, port: int) -> Node:
        """Add a new node to the cluster."""
        node_id = self._generate_node_id(address, port)
        with self.lock:
            if node_id not in self.members:
                self.members[node_id] = Node(node_id, address, port)
            return self.members[node_id]

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the cluster."""
        with self.lock:
            if node_id in self.members and node_id != self.node_id:
                del self.members[node_id]
                return True
            return False
