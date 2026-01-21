#!/usr/bin/env python3
"""
SWIM Gossip Provider implementation.
"""

import asyncio
import time
import random
from typing import Dict, List, Tuple, Optional
from internal.gossip.types import Node, NodeStatus

class SWIMGossipProvider:
    """
    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    Gossip Provider for node discovery and failure detection.
    """

    def __init__(self, node_id: str, host: str = "127.0.0.1", port: int = 8000,
                 seed_nodes: Optional[List[Tuple[str, int]]] = None,
                 config: Optional[Dict] = None):
        """
        Initialize the SWIM Gossip Provider.

        Args:
            node_id: Unique identifier for this node
            host: Host address to bind to
            port: Port to listen on
            seed_nodes: List of (host, port) tuples for initial seed nodes
            config: Configuration dictionary
        """
        self.node_id = node_id
        self.host = host
        self.port = port
        self.running = False
        self.gossip_task = None

        # Default configuration
        self.config = {
            "gossip_interval": 1.0,
            "ping_timeout": 0.5,
            "ping_req_timeout": 1.0,
            "suspect_timeout": 2.0,
            "max_nodes": 100,
            "seed_nodes": seed_nodes or []
        }

        # Override with custom config if provided
        if config:
            self.config.update(config)

        # Initialize node membership
        self.nodes = {
            self.node_id: Node(
                id=self.node_id,
                address=self.host,
                port=self.port,
                status=NodeStatus.ALIVE,
                incarnation=0,
                last_seen=time.time()
            )
        }

        # Add seed nodes
        for seed_host, seed_port in self.config["seed_nodes"]:
            seed_id = f"{seed_host}:{seed_port}"
            if seed_id not in self.nodes:
                self.nodes[seed_id] = Node(
                    id=seed_id,
                    address=seed_host,
                    port=seed_port,
                    status=NodeStatus.ALIVE,
                    incarnation=0,
                    last_seen=time.time()
                )

    async def start(self):
        """
        Start the gossip provider.
        """
        if self.running:
            return

        self.running = True
        self.gossip_task = asyncio.create_task(self._run_gossip_loop())

    async def stop(self):
        """
        Stop the gossip provider.
        """
        if not self.running:
            return

        self.running = False
        if self.gossip_task:
            self.gossip_task.cancel()
            try:
                await self.gossip_task
            except asyncio.CancelledError:
                pass
        self.gossip_task = None

    async def _run_gossip_loop(self):
        """
        Main gossip loop that periodically sends gossip messages.
        """
        while self.running:
            try:
                await self._gossip()
                await asyncio.sleep(self.config["gossip_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in gossip loop: {e}")
                await asyncio.sleep(self.config["gossip_interval"])

    async def _gossip(self):
        """
        Perform a single gossip round.
        """
        if len(self.nodes) < 2:
            return

        # Select a random node to gossip with
        target_node_id = random.choice(list(self.nodes.keys()))
        if target_node_id == self.node_id:
            return

        target_node = self.nodes[target_node_id]
        if target_node.status != NodeStatus.ALIVE:
            return

        # In a real implementation, we would send a gossip message to the target node
        # For now, we'll simulate receiving gossip from the target node
        await self._handle_gossip(target_node_id, list(self.nodes.values()))

    async def _handle_gossip(self, sender_id: str, nodes: List[Node]):
        """
        Handle incoming gossip from another node.

        Args:
            sender_id: ID of the node sending the gossip
            nodes: List of nodes from the sender's membership
        """
        # Update our membership with the sender's information
        for node in nodes:
            if node.id not in self.nodes:
                self.nodes[node.id] = node
            else:
                # Update existing node if the sender's info is newer
                existing = self.nodes[node.id]
                if node.last_seen > existing.last_seen:
                    self.nodes[node.id] = node

    def get_membership(self) -> Dict[str, Node]:
        """
        Get the current membership view.

        Returns:
            Dictionary of node_id -> Node
        """
        return self.nodes

    def get_alive_nodes(self) -> List[str]:
        """
        Get list of alive node IDs.

        Returns:
            List of node IDs that are alive
        """
        return [node_id for node_id, node in self.nodes.items()
                if node.status == NodeStatus.ALIVE]

    def get_suspect_nodes(self) -> List[str]:
        """
        Get list of suspect node IDs.

        Returns:
            List of node IDs that are suspect
        """
        return [node_id for node_id, node in self.nodes.items()
                if node.status == NodeStatus.SUSPECT]

    def get_failed_nodes(self) -> List[str]:
        """
        Get list of failed node IDs.

        Returns:
            List of node IDs that are failed
        """
        return [node_id for node_id, node in self.nodes.items()
                if node.status == NodeStatus.FAILED]

    def __str__(self):
        """
        String representation of the provider.
        """
        return f"SWIMGossipProvider(node_id={self.node_id}, nodes={len(self.nodes)})"
