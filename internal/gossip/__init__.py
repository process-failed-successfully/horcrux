"""
SWIM Gossip Provider Implementation

This module provides a SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
gossip provider for node discovery and failure detection.
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, List, Optional, Tuple

class SWIMGossipProvider:
    """
    SWIM Gossip Provider for node discovery and failure detection.

    SWIM is a gossip-based membership protocol that provides:
    - Node discovery
    - Failure detection
    - Scalability
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the SWIM Gossip provider.

        Args:
            config: Configuration dictionary. If None, uses default configuration.
        """
        self.config = config or {
            'node_id': f"node_{random.randint(1000, 9999)}",
            'listen_port': 8000,
            'gossip_interval': 1.0,
            'ping_timeout': 0.5,
            'ping_req_timeout': 0.3,
            'suspect_timeout': 2.0,
            'max_nodes': 100,
            'seed_nodes': []
        }

        self.logger = logging.getLogger(f"SWIMGossip-{self.config['node_id']}")
        self.logger.setLevel(logging.INFO)

        # Node state
        self.nodes: Dict[str, Dict] = {}  # node_id -> {address, status, timestamp}
        self.suspect_nodes: Dict[str, float] = {}  # node_id -> suspect_time
        self.running = False
        self.gossip_task: Optional[asyncio.Task] = None
        self.ping_task: Optional[asyncio.Task] = None

        # Initialize with self
        self._add_node(self.config['node_id'], {
            'address': f"127.0.0.1:{self.config['listen_port']}",
            'status': 'alive',
            'timestamp': time.time()
        })

        self.logger.info(f"SWIM Gossip provider initialized with node_id: {self.config['node_id']}")

    def _add_node(self, node_id: str, node_data: Dict):
        """Add or update a node in the membership list."""
        self.nodes[node_id] = {
            'address': node_data['address'],
            'status': node_data['status'],
            'timestamp': time.time()
        }

    async def start(self):
        """Start the SWIM gossip protocol."""
        if self.running:
            self.logger.warning("Provider is already running")
            return

        self.running = True
        self.logger.info("Starting SWIM gossip protocol")

        # Start periodic gossip
        self.gossip_task = asyncio.create_task(self._periodic_gossip())

        # Start periodic ping
        self.ping_task = asyncio.create_task(self._periodic_ping())

    async def stop(self):
        """Stop the SWIM gossip protocol gracefully."""
        if not self.running:
            self.logger.warning("Provider is not running")
            return

        self.running = False
        self.logger.info("Stopping SWIM gossip protocol")

        if self.gossip_task:
            self.gossip_task.cancel()
            try:
                await self.gossip_task
            except asyncio.CancelledError:
                pass

        if self.ping_task:
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass

        self.logger.info("SWIM gossip protocol stopped")

    async def _periodic_gossip(self):
        """Periodically send gossip messages to random nodes."""
        while self.running:
            try:
                await self._gossip()
                await asyncio.sleep(self.config['gossip_interval'])
            except Exception as e:
                self.logger.error(f"Error in periodic gossip: {e}")
                await asyncio.sleep(self.config['gossip_interval'])

    async def _periodic_ping(self):
        """Periodically ping random nodes for failure detection."""
        while self.running:
            try:
                await self._ping_random_node()
                await asyncio.sleep(self.config['ping_timeout'])
            except Exception as e:
                self.logger.error(f"Error in periodic ping: {e}")
                await asyncio.sleep(self.config['ping_timeout'])

    async def _gossip(self):
        """Send gossip message to a random node."""
        if len(self.nodes) < 2:
            return

        # Select a random node (not self)
        target_node_id = random.choice([nid for nid in self.nodes if nid != self.config['node_id']])
        target_node = self.nodes[target_node_id]

        # In a real implementation, this would send a gossip message
        # For now, we'll just log it
        self.logger.debug(f"Sending gossip to {target_node_id}")

    async def _ping_random_node(self):
        """Ping a random node for failure detection."""
        if len(self.nodes) < 2:
            return

        # Select a random node (not self)
        target_node_id = random.choice([nid for nid in self.nodes if nid != self.config['node_id']])
        target_node = self.nodes[target_node_id]

        # In a real implementation, this would send a ping
        # For now, we'll just log it
        self.logger.debug(f"Pinging {target_node_id}")

    def get_nodes(self) -> List[Dict]:
        """Get the list of known nodes."""
        return list(self.nodes.values())

    def get_alive_nodes(self) -> List[Dict]:
        """Get the list of alive nodes."""
        return [node for node in self.nodes.values() if node['status'] == 'alive']

    def get_suspect_nodes(self) -> List[Dict]:
        """Get the list of suspect nodes."""
        return [node for node in self.nodes.values() if node['status'] == 'suspect']
