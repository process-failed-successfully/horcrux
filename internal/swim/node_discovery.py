"""
SWIM Node Discovery Module

This module implements node discovery functionality for the SWIM Gossip protocol.
It allows nodes to discover each other in a cluster and maintain a consistent
membership list.
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
    """Represents a node in the cluster"""
    node_id: str
    address: str
    port: int
    status: str = "alive"
    last_seen: float = field(default_factory=time.time)
    incarnation: int = 0

    def to_dict(self) -> Dict:
        """Convert node to dictionary for serialization"""
        return {
            'node_id': self.node_id,
            'address': self.address,
            'port': self.port,
            'status': self.status,
            'last_seen': self.last_seen,
            'incarnation': self.incarnation
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        """Create node from dictionary"""
        return cls(
            node_id=data['node_id'],
            address=data['address'],
            port=data['port'],
            status=data.get('status', 'alive'),
            last_seen=data.get('last_seen', time.time()),
            incarnation=data.get('incarnation', 0)
        )

class SWIMNodeDiscovery:
    """
    SWIM Node Discovery Implementation

    This class implements the SWIM (Scalable Weakly-consistent Infection-style
    Process Group Membership Protocol) for node discovery in a distributed cluster.
    """

    def __init__(self, node_id: str, address: str, port: int, seed_nodes: Optional[List[Tuple[str, int]]] = None):
        """
        Initialize SWIM node discovery

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
        self.membership: Dict[str, Node] = {}
        self.membership[self.node_id] = self.local_node

        # Configuration
        self.gossip_interval = 1.0  # seconds
        self.ping_timeout = 0.5  # seconds
        self.failure_threshold = 3  # number of failed pings before declaring failure

        # Failure detection counters
        self.failure_counts: Dict[str, int] = {}

        # Lock for thread safety
        self.lock = threading.Lock()

        # Running flag
        self.running = False
        self.gossip_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the SWIM node discovery service"""
        if self.running:
            return

        self.running = True

        # Join seed nodes if provided
        if self.seed_nodes:
            for addr, port in self.seed_nodes:
                self.join_cluster(addr, port)

        # Start gossip thread
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()

    def stop(self) -> None:
        """Stop the SWIM node discovery service"""
        self.running = False
        if self.gossip_thread:
            self.gossip_thread.join()

    def join_cluster(self, seed_address: str, seed_port: int) -> bool:
        """
        Join the cluster using a seed node

        Args:
            seed_address: Address of seed node
            seed_port: Port of seed node

        Returns:
            bool: True if join was successful
        """
        try:
            # Create a temporary node for the seed
            seed_node = Node(
                node_id=self._generate_node_id(seed_address, seed_port),
                address=seed_address,
                port=seed_port
            )

            # Send join request to seed node
            # In a real implementation, this would be a network call
            # For testing purposes, we'll simulate it

            with self.lock:
                # Add seed node to membership
                self.membership[seed_node.node_id] = seed_node
                self.failure_counts[seed_node.node_id] = 0

            return True
        except Exception as e:
            print(f"Failed to join cluster via {seed_address}:{seed_port}: {e}")
            return False

    def get_membership_list(self) -> List[Node]:
        """
        Get the current membership list

        Returns:
            List of Node objects representing the cluster membership
        """
        with self.lock:
            return list(self.membership.values())

    def get_alive_nodes(self) -> List[Node]:
        """
        Get list of alive nodes

        Returns:
            List of Node objects that are alive
        """
        with self.lock:
            return [node for node in self.membership.values() if node.status == "alive"]

    def _gossip_loop(self) -> None:
        """Main gossip loop that runs in a background thread"""
        while self.running:
            try:
                self._perform_gossip()
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Error in gossip loop: {e}")
                time.sleep(1)  # Backoff on error

    def _perform_gossip(self) -> None:
        """Perform a round of gossip"""
        with self.lock:
            alive_nodes = [node for node in self.membership.values() if node.status == "alive"]

        # Select a random node to gossip with
        if len(alive_nodes) > 1:
            target_node = random.choice(alive_nodes)
            if target_node.node_id != self.node_id:
                self._gossip_with_node(target_node)

    def _gossip_with_node(self, target_node: Node) -> None:
        """
        Perform gossip with a specific node

        Args:
            target_node: Node to gossip with
        """
        # In a real implementation, this would involve network communication
        # For testing, we'll simulate the gossip exchange

        # Update last seen time
        with self.lock:
            if target_node.node_id in self.membership:
                self.membership[target_node.node_id].last_seen = time.time()
                self.failure_counts[target_node.node_id] = 0

        # Simulate receiving gossip from target node
        # This would include the target node's membership list
        self._process_gossip(target_node.node_id, self.membership)

    def _process_gossip(self, sender_id: str, remote_membership: Dict[str, Node]) -> None:
        """
        Process gossip received from another node

        Args:
            sender_id: ID of the node that sent the gossip
            remote_membership: Membership list from the remote node
        """
        with self.lock:
            # Update or add nodes from remote membership
            for node_id, remote_node in remote_membership.items():
                if node_id not in self.membership:
                    # New node discovered
                    self.membership[node_id] = remote_node
                    self.failure_counts[node_id] = 0
                else:
                    # Update existing node
                    local_node = self.membership[node_id]

                    # Update if remote node has newer information
                    if remote_node.incarnation > local_node.incarnation:
                        self.membership[node_id] = remote_node
                        self.failure_counts[node_id] = 0

                    # Update last seen if remote is newer
                    if remote_node.last_seen > local_node.last_seen:
                        local_node.last_seen = remote_node.last_seen
                        self.failure_counts[node_id] = 0

    def _generate_node_id(self, address: str, port: int) -> str:
        """
        Generate a unique node ID from address and port

        Args:
            address: Node address
            port: Node port

        Returns:
            str: Generated node ID
        """
        return hashlib.md5(f"{address}:{port}".encode()).hexdigest()

    def add_node(self, node: Node) -> None:
        """
        Add a node to the membership list

        Args:
            node: Node to add
        """
        with self.lock:
            self.membership[node.node_id] = node
            self.failure_counts[node.node_id] = 0

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node from the membership list

        Args:
            node_id: ID of node to remove
        """
        with self.lock:
            if node_id in self.membership:
                del self.membership[node_id]
            if node_id in self.failure_counts:
                del self.failure_counts[node_id]

    def get_node_count(self) -> int:
        """
        Get the number of nodes in the cluster

        Returns:
            int: Number of nodes
        """
        with self.lock:
            return len(self.membership)

    def is_healthy(self) -> bool:
        """
        Check if the cluster is healthy

        Returns:
            bool: True if cluster is healthy
        """
        with self.lock:
            alive_count = sum(1 for node in self.membership.values() if node.status == "alive")
            return alive_count > 0

    def __str__(self) -> str:
        """String representation of the SWIM node discovery"""
        with self.lock:
            return f"SWIMNodeDiscovery(node_id={self.node_id}, members={len(self.membership)})"
