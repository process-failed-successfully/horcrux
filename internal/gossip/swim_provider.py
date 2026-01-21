#!/usr/bin/env python3
"""
SWIM Gossip Provider Module

This module implements the SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
Gossip provider for node discovery in distributed systems.
"""

import json
import sys
import time
import threading
import random
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass

@dataclass
class Node:
    """Represents a node in the gossip network."""
    id: str
    address: str
    port: int
    last_seen: float
    status: str = "alive"

class SWIMGossipProvider:
    """
    SWIM Gossip Provider for node discovery and failure detection.

    SWIM is a gossip-based membership protocol that provides:
    - Node discovery
    - Failure detection
    - Scalability
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SWIM Gossip provider.

        Args:
            config: Optional configuration dictionary. If None, uses all defaults.

        Raises:
            ValueError: If configuration is invalid type (not dict or None)
        """
        # Validate config type
        if config is not None and not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary or None for defaults")

        self.config = config if config is not None else {}

        # Default configuration
        self.node_id = self.config.get("node_id", f"node_{random.randint(1000, 9999)}")
        self.address = self.config.get("address", "127.0.0.1")
        self.port = self.config.get("port", 8080)
        self.gossip_interval = self.config.get("gossip_interval", 1.0)
        self.ping_timeout = self.config.get("ping_timeout", 0.5)
        self.probe_timeout = self.config.get("probe_timeout", 1.0)

        # Validate configuration values
        self._validate_config_values()

        # Node state
        self.nodes: Dict[str, Node] = {}
        self.lock = threading.Lock()
        self.running = False
        self.gossip_thread: Optional[threading.Thread] = None

        # Initialize with self
        self._add_node(self.node_id, self.address, self.port)

    def _validate_config_values(self) -> None:
        """
        Validate individual configuration values.

        Raises:
            ValueError: If any configuration value is invalid
        """
        if not isinstance(self.node_id, str) or not self.node_id:
            raise ValueError("node_id must be a non-empty string")

        if not isinstance(self.address, str) or not self.address:
            raise ValueError("address must be a non-empty string")

        if not isinstance(self.port, int) or not (0 < self.port < 65536):
            raise ValueError("port must be an integer between 1 and 65535")

        if not isinstance(self.gossip_interval, (int, float)) or self.gossip_interval <= 0:
            raise ValueError("gossip_interval must be a positive number")

        if not isinstance(self.ping_timeout, (int, float)) or self.ping_timeout <= 0:
            raise ValueError("ping_timeout must be a positive number")

        if not isinstance(self.probe_timeout, (int, float)) or self.probe_timeout <= 0:
            raise ValueError("probe_timeout must be a positive number")

    def _add_node(self, node_id: str, address: str, port: int) -> None:
        """
        Add a node to the local node list.

        Args:
            node_id: Unique identifier for the node
            address: Network address of the node
            port: Network port of the node
        """
        with self.lock:
            self.nodes[node_id] = Node(
                id=node_id,
                address=address,
                port=port,
                last_seen=time.time(),
                status="alive"
            )

    def _update_node(self, node_id: str) -> None:
        """
        Update the last seen timestamp for a node.

        Args:
            node_id: Unique identifier for the node
        """
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id].last_seen = time.time()
                self.nodes[node_id].status = "alive"

    def _gossip_loop(self) -> None:
        """
        Main gossip loop that runs periodically to exchange node information.
        """
        while self.running:
            try:
                # Simulate gossip protocol
                self._perform_gossip()
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Error in gossip loop: {e}")
                time.sleep(1)

    def _perform_gossip(self) -> None:
        """
        Perform a single gossip round.
        """
        # In a real implementation, this would:
        # 1. Select a random node to gossip with
        # 2. Exchange node lists
        # 3. Update local state
        # For now, we just update our own timestamp
        self._update_node(self.node_id)

    def start(self) -> None:
        """
        Start the SWIM Gossip provider.
        """
        if self.running:
            return

        self.running = True
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()
        print(f"SWIM Gossip provider started for node {self.node_id}")

    def stop(self) -> None:
        """
        Stop the SWIM Gossip provider gracefully.
        """
        self.running = False
        if self.gossip_thread:
            self.gossip_thread.join(timeout=2.0)
        print(f"SWIM Gossip provider stopped for node {self.node_id}")

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Get the list of known nodes.

        Returns:
            List of node dictionaries
        """
        with self.lock:
            return [
                {
                    "id": node.id,
                    "address": node.address,
                    "port": node.port,
                    "last_seen": node.last_seen,
                    "status": node.status
                }
                for node in self.nodes.values()
            ]

    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.

        Returns:
            Dictionary containing the current configuration
        """
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "gossip_interval": self.gossip_interval,
            "ping_timeout": self.ping_timeout,
            "probe_timeout": self.probe_timeout
        }

def main():
    """
    Main entry point for testing the SWIM Gossip provider.
    """
    # Load configuration if provided
    config = {}
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)

    # Initialize the provider
    provider = SWIMGossipProvider(config)

    try:
        # Start the provider
        provider.start()

        # Print configuration
        print(f"Configuration: {json.dumps(provider.get_config(), indent=2)}")

        # Run for a few seconds
        time.sleep(3)

        # Get and print node list
        nodes = provider.get_nodes()
        print(f"Known nodes: {json.dumps(nodes, indent=2)}")

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Stop the provider
        provider.stop()

if __name__ == "__main__":
    main()
