"""
Node discovery module for SWIM gossip protocol.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time
import random
import asyncio

@dataclass
class Node:
    """Represents a node in the cluster."""
    id: str
    address: str
    port: int
    status: str = "alive"
    last_seen: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

class NodeDiscovery:
    """
    Basic node discovery class for testing purposes.
    This provides simple discovery functionality.
    """

    def discover_nodes(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover nodes from input data.

        Args:
            input_data: Input data containing node information

        Returns:
            Input data with discovery flag added
        """
        result = input_data.copy()
        result['discovered'] = True
        return result

    def batch_discover(self, input_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Discover nodes from a batch of input data.

        Args:
            input_data_list: List of input data containing node information

        Returns:
            List of input data with discovery flags added
        """
        return [self.discover_nodes(data) for data in input_data_list]

class SWIMNodeDiscovery:
    """
    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    implementation for node discovery in a cluster.
    """

    def __init__(self, node_id: str, node_address: str, node_port: int, seed_nodes: Optional[List[Dict]] = None):
        """
        Initialize the SWIM node discovery.

        Args:
            node_id: Unique identifier for this node
            node_address: Network address of this node
            node_port: Network port of this node
            seed_nodes: List of seed nodes to bootstrap the cluster
        """
        self.node = Node(id=node_id, address=node_address, port=node_port)
        self.membership: Dict[str, Node] = {}
        self.membership[self.node.id] = self.node

        # Add seed nodes if provided
        if seed_nodes:
            for seed in seed_nodes:
                seed_node = Node(
                    id=seed['id'],
                    address=seed['address'],
                    port=seed['port']
                )
                self.membership[seed_node.id] = seed_node

        # Protocol parameters
        self.protocol_period = 1.0  # seconds
        self.ping_timeout = 0.5  # seconds
        self.ping_req_timeout = 0.3  # seconds
        self.running = False
        self.task = None

    async def start(self):
        """Start the SWIM protocol."""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._run_protocol())

    async def stop(self):
        """Stop the SWIM protocol."""
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass

    async def _run_protocol(self):
        """Main protocol loop."""
        while self.running:
            await self._perform_protocol_round()
            await asyncio.sleep(self.protocol_period)

    async def _perform_protocol_round(self):
        """Perform one round of the SWIM protocol."""
        # Select a random node to ping
        if len(self.membership) > 1:
            target_node = random.choice(list(self.membership.values()))
            if target_node.id != self.node.id:
                await self._ping(target_node)

    async def _ping(self, target_node: Node):
        """
        Ping a target node to check if it's alive.

        Args:
            target_node: The node to ping
        """
        try:
            # Simulate network ping
            # In a real implementation, this would be an actual network call
            await asyncio.wait_for(self._simulate_network_ping(target_node), timeout=self.ping_timeout)

            # Update last seen time
            target_node.last_seen = time.time()
            target_node.status = "alive"

        except asyncio.TimeoutError:
            # Node didn't respond, mark as suspect
            target_node.status = "suspect"
            target_node.last_seen = time.time()

    async def _simulate_network_ping(self, target_node: Node):
        """
        Simulate a network ping to the target node.
        In a real implementation, this would be an actual network call.
        """
        # Simulate network delay
        await asyncio.sleep(0.1)

        # Simulate occasional failures
        if random.random() < 0.05:  # 5% chance of failure
            raise asyncio.TimeoutError("Simulated network timeout")

    def get_membership_list(self) -> List[Node]:
        """
        Get the current membership list.

        Returns:
            List of nodes in the cluster
        """
        return list(self.membership.values())

    def get_alive_nodes(self) -> List[Node]:
        """
        Get the list of alive nodes.

        Returns:
            List of alive nodes
        """
        return [node for node in self.membership.values() if node.status == "alive"]

    def get_suspect_nodes(self) -> List[Node]:
        """
        Get the list of suspect nodes.

        Returns:
            List of suspect nodes
        """
        return [node for node in self.membership.values() if node.status == "suspect"]

    async def add_node(self, node_id: str, address: str, port: int):
        """
        Add a new node to the cluster.

        Args:
            node_id: Unique identifier for the new node
            address: Network address of the new node
            port: Network port of the new node
        """
        if node_id not in self.membership:
            new_node = Node(id=node_id, address=address, port=port)
            self.membership[node_id] = new_node
            print(f"Added new node: {node_id}")

    def remove_node(self, node_id: str):
        """
        Remove a node from the cluster.

        Args:
            node_id: Unique identifier of the node to remove
        """
        if node_id in self.membership:
            del self.membership[node_id]
            print(f"Removed node: {node_id}")

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by its ID.

        Args:
            node_id: Unique identifier of the node

        Returns:
            The node if found, None otherwise
        """
        return self.membership.get(node_id)
