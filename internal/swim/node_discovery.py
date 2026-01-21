"""
SWIM Node Discovery Module

This module provides functionality to discover nodes in the cluster using the SWIM Gossip provider.
"""

import json
import random
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from threading import Lock

@dataclass
class Node:
    """Represents a node in the cluster."""
    id: str
    address: str
    port: int
    status: str = "alive"
    last_seen: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class NodeDiscovery:
    """
    A class to handle node discovery tasks using the SWIM Gossip provider.
    """

    def __init__(self, node_id: str = "default-node", seed_nodes: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the NodeDiscovery.

        Args:
            node_id: Unique identifier for this node
            seed_nodes: List of seed nodes to bootstrap the cluster
        """
        self.node_id = node_id
        self.membership: Dict[str, Node] = {}
        self.lock = Lock()

        # Add self to membership
        self._add_node(Node(
            id=self.node_id,
            address="localhost",
            port=8080,
            status="alive"
        ))

        # Add seed nodes if provided
        if seed_nodes:
            for seed in seed_nodes:
                self._add_node(Node(
                    id=seed['id'],
                    address=seed.get('address', 'localhost'),
                    port=seed.get('port', 8080)
                ))

    def _add_node(self, node: Node) -> None:
        """Add a node to the membership list."""
        with self.lock:
            self.membership[node.id] = node

    def _update_node(self, node: Node) -> None:
        """Update an existing node in the membership list."""
        with self.lock:
            if node.id in self.membership:
                self.membership[node.id].last_seen = time.time()
                self.membership[node.id].status = node.status
                self.membership[node.id].metadata.update(node.metadata)

    def discover_nodes(self) -> List[Node]:
        """
        Discover nodes in the cluster and return the discovered nodes.

        Returns:
            List of discovered nodes.
        """
        with self.lock:
            return list(self.membership.values())

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a specific node by ID.

        Args:
            node_id: ID of the node to retrieve

        Returns:
            Node object if found, None otherwise
        """
        with self.lock:
            return self.membership.get(node_id)

    def update_node_status(self, node_id: str, status: str) -> bool:
        """
        Update the status of a node.

        Args:
            node_id: ID of the node to update
            status: New status (alive, suspect, dead)

        Returns:
            True if node was found and updated, False otherwise
        """
        with self.lock:
            if node_id in self.membership:
                self.membership[node_id].status = status
                self.membership[node_id].last_seen = time.time()
                return True
            return False

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the membership list.

        Args:
            node_id: ID of the node to remove

        Returns:
            True if node was found and removed, False otherwise
        """
        with self.lock:
            if node_id in self.membership:
                del self.membership[node_id]
                return True
            return False

    def get_alive_nodes(self) -> List[Node]:
        """
        Get all alive nodes in the cluster.

        Returns:
            List of alive nodes
        """
        with self.lock:
            return [node for node in self.membership.values() if node.status == "alive"]

    def get_cluster_size(self) -> int:
        """
        Get the current size of the cluster.

        Returns:
            Number of nodes in the cluster
        """
        with self.lock:
            return len(self.membership)
