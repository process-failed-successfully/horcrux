"""
Node Discovery Module for SWIM Gossip Protocol

This module implements node discovery functionality for the SWIM gossip protocol,
which is used for distributed node discovery and failure detection.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time

@dataclass
class Node:
    """
    Represents a node in the SWIM cluster.
    """
    id: str
    address: str
    port: int
    status: str = "alive"
    last_seen: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class SWIMNodeDiscovery:
    """
    A class that handles node discovery in a SWIM gossip protocol cluster.

    The SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    is used for distributed node discovery and failure detection.
    """

    def __init__(self, node_id: str, address: str, port: int):
        """
        Initialize the SWIMNodeDiscovery.

        Args:
            node_id: Unique identifier for this node
            address: Network address of this node
            port: Network port of this node
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.membership_list: Dict[str, Node] = {}

        # Add self to membership list
        self_node = Node(
            id=self.node_id,
            address=self.address,
            port=self.port,
            status="alive",
            last_seen=time.time()
        )
        self.membership_list[self.node_id] = self_node

    def get_membership_list(self) -> List[Node]:
        """
        Get the current membership list.

        Returns:
            List of all nodes in the cluster
        """
        return list(self.membership_list.values())

    def add_node(self, node: Node) -> None:
        """
        Add a node to the membership list.

        Args:
            node: Node to add
        """
        if node.id not in self.membership_list:
            self.membership_list[node.id] = node

    def _add_node(self, node: Node) -> None:
        """
        Internal method to add a node (used by gossip provider).

        Args:
            node: Node to add
        """
        self.membership_list[node.id] = node

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by ID.

        Args:
            node_id: ID of the node to retrieve

        Returns:
            Node if found, None otherwise
        """
        return self.membership_list.get(node_id)

    def _update_node(self, node: Node) -> None:
        """
        Internal method to update a node (used by gossip provider).

        Args:
            node: Node with updated information
        """
        if node.id in self.membership_list:
            existing_node = self.membership_list[node.id]
            # Update fields
            existing_node.status = node.status
            existing_node.last_seen = node.last_seen
            existing_node.metadata = node.metadata

    def get_alive_nodes(self) -> List[Node]:
        """
        Get the list of alive nodes.

        Returns:
            List of nodes with 'alive' status
        """
        return [node for node in self.membership_list.values() if node.status == "alive"]

    def join_cluster(self, seed_address: str, seed_port: int) -> bool:
        """
        Join a cluster by connecting to a seed node.

        Args:
            seed_address: Address of the seed node
            seed_port: Port of the seed node

        Returns:
            True if join was successful, False otherwise
        """
        # In a real implementation, this would connect to the seed node
        # and exchange membership information
        # For now, we'll simulate by adding a seed node
        seed_node = Node(
            id=f"{seed_address}:{seed_port}",
            address=seed_address,
            port=seed_port,
            status="alive",
            last_seen=time.time()
        )
        self.add_node(seed_node)
        return True

    def discover_nodes(self) -> List[Node]:
        """
        Discover nodes in the cluster.

        Returns:
            List of discovered nodes
        """
        return self.get_alive_nodes()

    def batch_discover(self, input_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Discover multiple nodes in batch.

        Args:
            input_data_list: List of input data dictionaries

        Returns:
            List of output data with discovery status added
        """
        if not isinstance(input_data_list, list):
            raise ValueError("Input data must be a list")

        return [self.discover_nodes(data) for data in input_data_list]
