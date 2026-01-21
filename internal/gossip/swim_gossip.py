#!/usr/bin/env python3
"""
SWIM Gossip Provider Implementation

This module provides a SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
Gossip provider for node discovery and failure detection.
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, List, Optional, Set, Tuple

class SWIMGossipProvider:
    """
    SWIM Gossip Provider for node discovery and failure detection.

    SWIM is a gossip-based membership protocol that provides:
    - Node discovery
    - Failure detection
    - Scalable membership management
    """

    def __init__(self, node_id: str, config: Optional[Dict] = None):
        """
        Initialize the SWIM Gossip provider.

        Args:
            node_id: Unique identifier for this node
            config: Configuration dictionary (optional)
        """
        self.node_id = node_id
        self.config = config or {}
        self.logger = logging.getLogger(f"SWIMGossip-{node_id}")

        # Default configuration
        self.default_config = {
            "gossip_interval": 1.0,  # seconds
            "ping_timeout": 0.5,     # seconds
            "ping_req_timeout": 1.0, # seconds
            "suspect_timeout": 2.0,  # seconds
            "max_nodes": 100,
            "seed_nodes": []
        }

        # Apply configuration
        self._apply_config()

        # Node state
        self.nodes: Dict[str, Dict] = {}  # node_id -> {address, status, timestamp}
        self.suspect_nodes: Set[str] = set()
        self.failed_nodes: Set[str] = set()

        # Internal state
        self.running = False
        self.gossip_task: Optional[asyncio.Task] = None
        self.ping_task: Optional[asyncio.Task] = None

        self.logger.info(f"SWIM Gossip provider initialized for node {node_id}")

    def _apply_config(self):
        """Apply configuration with validation."""
        # Merge default config with provided config
        self.config = {**self.default_config, **self.config}

        # Validate configuration
        if not isinstance(self.config["gossip_interval"], (int, float)) or self.config["gossip_interval"] <= 0:
            raise ValueError("gossip_interval must be a positive number")

        if not isinstance(self.config["ping_timeout"], (int, float)) or self.config["ping_timeout"] <= 0:
            raise ValueError("ping_timeout must be a positive number")

        if not isinstance(self.config["ping_req_timeout"], (int, float)) or self.config["ping_req_timeout"] <= 0:
            raise ValueError("ping_req_timeout must be a positive number")

        if not isinstance(self.config["suspect_timeout"], (int, float)) or self.config["suspect_timeout"] <= 0:
            raise ValueError("suspect_timeout must be a positive number")

        if not isinstance(self.config["max_nodes"], int) or self.config["max_nodes"] <= 0:
            raise ValueError("max_nodes must be a positive integer")

        if not isinstance(self.config["seed_nodes"], list):
            raise ValueError("seed_nodes must be a list")

        # Add self to nodes
        self.nodes[self.node_id] = {
            "address": self.config.get("address", f"127.0.0.1:{hash(self.node_id) % 10000 + 5000}"),
            "status": "alive",
            "timestamp": time.time()
        }

        # Add seed nodes
        for seed in self.config["seed_nodes"]:
            if seed != self.node_id:
                self.nodes[seed] = {
                    "address": f"127.0.0.1:{hash(seed) % 10000 + 5000}",
                    "status": "alive",
                    "timestamp": time.time()
                }

    async def start(self):
        """Start the SWIM Gossip provider."""
        if self.running:
            self.logger.warning("Provider is already running")
            return

        self.running = True
        self.logger.info("Starting SWIM Gossip provider")

        # Start gossip task
        self.gossip_task = asyncio.create_task(self._gossip_loop())

        # Start ping task
        self.ping_task = asyncio.create_task(self._ping_loop())

    async def stop(self):
        """Stop the SWIM Gossip provider gracefully."""
        if not self.running:
            self.logger.warning("Provider is not running")
            return

        self.running = False
        self.logger.info("Stopping SWIM Gossip provider")

        # Cancel tasks
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

        self.logger.info("SWIM Gossip provider stopped")

    async def _gossip_loop(self):
        """Main gossip loop."""
        while self.running:
            try:
                await self._perform_gossip()
                await asyncio.sleep(self.config["gossip_interval"])
            except Exception as e:
                self.logger.error(f"Error in gossip loop: {e}")
                await asyncio.sleep(1.0)

    async def _ping_loop(self):
        """Ping loop for failure detection."""
        while self.running:
            try:
                await self._perform_ping()
                await asyncio.sleep(self.config["ping_timeout"])
            except Exception as e:
                self.logger.error(f"Error in ping loop: {e}")
                await asyncio.sleep(1.0)

    async def _perform_gossip(self):
        """Perform gossip with a random node."""
        if len(self.nodes) < 2:
            return

        # Select a random node to gossip with
        target_node = random.choice([n for n in self.nodes.keys() if n != self.node_id])

        # Simulate gossip exchange
        self.logger.debug(f"Gossiping with node {target_node}")

        # Update timestamp
        self.nodes[self.node_id]["timestamp"] = time.time()

    async def _perform_ping(self):
        """Perform ping to detect failures."""
        if len(self.nodes) < 2:
            return

        # Select a random node to ping
        target_node = random.choice([n for n in self.nodes.keys() if n != self.node_id])

        # Simulate ping
        self.logger.debug(f"Pinging node {target_node}")

        # Update timestamp
        self.nodes[self.node_id]["timestamp"] = time.time()

    def get_nodes(self) -> Dict[str, Dict]:
        """Get the current list of nodes."""
        return self.nodes

    def get_alive_nodes(self) -> List[str]:
        """Get the list of alive nodes."""
        return [node_id for node_id, info in self.nodes.items()
                if info["status"] == "alive" and node_id not in self.suspect_nodes]

    def get_suspect_nodes(self) -> List[str]:
        """Get the list of suspect nodes."""
        return list(self.suspect_nodes)

    def get_failed_nodes(self) -> List[str]:
        """Get the list of failed nodes."""
        return list(self.failed_nodes)

    def __str__(self):
        return f"SWIMGossipProvider(node_id={self.node_id}, nodes={len(self.nodes)})"
