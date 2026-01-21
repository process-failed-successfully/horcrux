"""
SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
Gossip Provider for Node Discovery and Failure Detection.

This module implements a basic SWIM gossip protocol for distributed node discovery
and failure detection in a peer-to-peer network.
"""

import asyncio
import random
import time
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import json
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Node:
    """Represents a node in the gossip network."""
    node_id: str
    address: str
    port: int
    last_seen: float = field(default_factory=time.time)
    is_alive: bool = True
    incarnation: int = 0  # For detecting node restarts

    def to_dict(self) -> Dict:
        """Convert node to dictionary for serialization."""
        return {
            'node_id': self.node_id,
            'address': self.address,
            'port': self.port,
            'last_seen': self.last_seen,
            'is_alive': self.is_alive,
            'incarnation': self.incarnation
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        """Create node from dictionary."""
        return cls(
            node_id=data['node_id'],
            address=data['address'],
            port=data['port'],
            last_seen=data.get('last_seen', time.time()),
            is_alive=data.get('is_alive', True),
            incarnation=data.get('incarnation', 0)
        )

class SWIMGossipProvider:
    """
    SWIM Gossip Provider for node discovery and failure detection.

    The SWIM protocol uses periodic gossip messages to:
    1. Discover new nodes in the network
    2. Detect failed nodes
    3. Maintain a consistent view of the network
    """

    def __init__(self, node_id: str, address: str, port: int,
                 seed_nodes: Optional[List[Tuple[str, int]]] = None,
                 gossip_interval: float = 1.0,
                 ping_timeout: float = 0.5,
                 ping_req_timeout: float = 0.3,
                 failure_threshold: int = 3):
        """
        Initialize the SWIM gossip provider.

        Args:
            node_id: Unique identifier for this node
            address: Network address of this node
            port: Network port of this node
            seed_nodes: List of (address, port) tuples for initial bootstrap
            gossip_interval: Time between gossip rounds in seconds
            ping_timeout: Timeout for ping requests in seconds
            ping_req_timeout: Timeout for ping-requests in seconds
            failure_threshold: Number of failed pings before declaring node dead
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.gossip_interval = gossip_interval
        self.ping_timeout = ping_timeout
        self.ping_req_timeout = ping_req_timeout
        self.failure_threshold = failure_threshold

        # Local node representation
        self.local_node = Node(
            node_id=node_id,
            address=address,
            port=port
        )

        # Membership list: node_id -> Node
        self.membership: Dict[str, Node] = {}
        self.membership[self.node_id] = self.local_node

        # Failure detection state: node_id -> failure_count
        self.failure_counts: Dict[str, int] = {}

        # Initialize with seed nodes if provided
        if seed_nodes:
            for addr, port in seed_nodes:
                node = Node(
                    node_id=self._generate_node_id(addr, port),
                    address=addr,
                    port=port
                )
                self.membership[node.node_id] = node

        # Protocol state
        self.is_running = False
        self.gossip_task: Optional[asyncio.Task] = None
        self.ping_tasks: Dict[str, asyncio.Task] = {}

        logger.info(f"Initialized SWIM Gossip Provider for node {node_id}")

    def _generate_node_id(self, address: str, port: int) -> str:
        """Generate a deterministic node ID from address and port."""
        return hashlib.md5(f"{address}:{port}".encode()).hexdigest()

    async def start(self):
        """Start the gossip provider."""
        if self.is_running:
            logger.warning("Gossip provider is already running")
            return

        self.is_running = True
        self.gossip_task = asyncio.create_task(self._gossip_loop())
        logger.info("SWIM Gossip provider started")

    async def stop(self):
        """Stop the gossip provider gracefully."""
        if not self.is_running:
            logger.warning("Gossip provider is not running")
            return

        self.is_running = False

        # Cancel ongoing gossip task
        if self.gossip_task:
            self.gossip_task.cancel()
            try:
                await self.gossip_task
            except asyncio.CancelledError:
                pass

        # Cancel all ping tasks
        for task in self.ping_tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self.ping_tasks.clear()
        logger.info("SWIM Gossip provider stopped gracefully")

    async def _gossip_loop(self):
        """Main gossip loop that runs periodically."""
        while self.is_running:
            try:
                await self._perform_gossip_round()
                await asyncio.sleep(self.gossip_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in gossip loop: {e}")
                await asyncio.sleep(self.gossip_interval)

    async def _perform_gossip_round(self):
        """Perform a single gossip round."""
        if len(self.membership) <= 1:
            # No other nodes to gossip with
            return

        # Select a random node to gossip with
        target_node_id = random.choice(
            [nid for nid in self.membership.keys() if nid != self.node_id]
        )

        target_node = self.membership[target_node_id]

        # Prepare membership information to send
        # In a real implementation, this would be serialized and sent over network
        # For now, we'll simulate the gossip exchange

        # Simulate network communication
        try:
            # This would be replaced with actual network calls in a real implementation
            await self._simulate_gossip_exchange(target_node)

            # Update last seen time
            self.membership[target_node_id].last_seen = time.time()
            self.membership[target_node_id].is_alive = True

            # Reset failure count
            self.failure_counts.pop(target_node_id, None)

        except Exception as e:
            logger.warning(f"Gossip with {target_node_id} failed: {e}")
            # Increment failure count
            self.failure_counts[target_node_id] = self.failure_counts.get(target_node_id, 0) + 1

            # Check if we've exceeded the failure threshold
            if self.failure_counts[target_node_id] >= self.failure_threshold:
                logger.warning(f"Node {target_node_id} declared as failed")
                self.membership[target_node_id].is_alive = False

    async def _simulate_gossip_exchange(self, target_node: Node):
        """
        Simulate a gossip exchange with another node.
        In a real implementation, this would involve network communication.
        """
        # Simulate network delay
        await asyncio.sleep(0.1)

        # Simulate random failures (10% chance)
        if random.random() < 0.1:
            raise Exception("Simulated network failure")

        # In a real implementation, we would:
        # 1. Send our membership list to the target node
        # 2. Receive the target node's membership list
        # 3. Merge the membership lists

        # For simulation, we'll just update our own membership
        # with some random nodes to simulate discovery
        if random.random() < 0.3 and len(self.membership) < 10:
            # Simulate discovering a new node
            new_node_id = f"simulated_node_{len(self.membership)}"
            new_node = Node(
                node_id=new_node_id,
                address=f"192.168.1.{len(self.membership)}",
                port=8000 + len(self.membership)
            )
            self.membership[new_node_id] = new_node
            logger.info(f"Discovered new node: {new_node_id}")

    def get_membership(self) -> List[Node]:
        """Get the current membership list."""
        return list(self.membership.values())

    def get_alive_nodes(self) -> List[Node]:
        """Get the list of alive nodes."""
        return [node for node in self.membership.values() if node.is_alive]

    def get_failed_nodes(self) -> List[Node]:
        """Get the list of failed nodes."""
        return [node for node in self.membership.values() if not node.is_alive]

    def __str__(self) -> str:
        """String representation of the provider state."""
        return (f"SWIMGossipProvider(node_id={self.node_id}, "
                f"address={self.address}, port={self.port}, "
                f"alive_nodes={len(self.get_alive_nodes())}, "
                f"failed_nodes={len(self.get_failed_nodes())})")
