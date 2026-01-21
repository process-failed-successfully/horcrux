#!/usr/bin/env python3
"""
Gossip provider for node discovery in distributed systems.
Implements the SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
for failure detection and membership management.
"""

import json
import random
import threading
import time
import uuid
from typing import Dict, List, Optional, Any

class Node:
    """
    Represents a node in the gossip network.
    """

    def __init__(self, node_id: str, address: str, port: int):
        """
        Initialize a node.

        Args:
            node_id: Unique identifier for the node
            address: IP address of the node
            port: Port number of the node
        """
        self.id = node_id
        self.address = address
        self.port = port
        self.last_seen = time.time()
        self.status = "alive"
        self.failure_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert node to dictionary representation.

        Returns:
            Dictionary containing node information
        """
        return {
            "id": self.id,
            "address": self.address,
            "port": self.port,
            "last_seen": self.last_seen,
            "status": self.status,
            "failure_count": self.failure_count
        }

    def update_last_seen(self):
        """
        Update the last seen timestamp.
        """
        self.last_seen = time.time()

    def mark_failed(self):
        """
        Mark the node as failed.
        """
        self.status = "failed"
        self.failure_count += 1

    def mark_alive(self):
        """
        Mark the node as alive.
        """
        self.status = "alive"

class SWIMGossipProvider:
    """
    SWIM Gossip Provider for node discovery and failure detection.

    Features:
    - Node discovery
    - Failure detection
    - Periodic gossip
    - Configurable timeouts
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SWIM gossip provider.

        Args:
            config: Configuration dictionary. If None, uses defaults.
        """
        # Default configuration
        self._defaults = {
            "node_id": f"node_{random.randint(1000, 9999)}",
            "address": "127.0.0.1",
            "port": 8080,
            "gossip_interval": 1.0,
            "ping_timeout": 0.5,
            "probe_timeout": 1.0,
            "max_failure_count": 3
        }

        # Apply configuration
        if config is None:
            self.config = self._defaults
        elif isinstance(config, dict):
            self.config = {**self._defaults, **config}
        else:
            raise ValueError("Configuration must be a dictionary or None")

        # Initialize from config
        self.node_id = self.config["node_id"]
        self.address = self.config["address"]
        self.port = self.config["port"]
        self.gossip_interval = self.config["gossip_interval"]
        self.ping_timeout = self.config["ping_timeout"]
        self.probe_timeout = self.config["probe_timeout"]
        self.max_failure_count = self.config["max_failure_count"]

        # Node management
        self.nodes: Dict[str, Node] = {}
        self.lock = threading.Lock()

        # Add self to the node list
        self._add_node(self.node_id, self.address, self.port)

        # Gossip state
        self.running = False
        self.gossip_thread: Optional[threading.Thread] = None

    def _add_node(self, node_id: str, address: str, port: int) -> Node:
        """
        Add a node to the membership list (internal method).

        Args:
            node_id: Unique identifier for the node
            address: IP address of the node
            port: Port number of the node

        Returns:
            The created Node object
        """
        with self.lock:
            if node_id not in self.nodes:
                node = Node(node_id, address, port)
                self.nodes[node_id] = node
                return node
            return self.nodes[node_id]

    def add_node(self, node_id: str, address: str, port: int) -> Node:
        """
        Public method to add a node to the membership list.

        Args:
            node_id: Unique identifier for the node
            address: IP address of the node
            port: Port number of the node

        Returns:
            The created Node object
        """
        return self._add_node(node_id, address, port)

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the membership list.

        Args:
            node_id: Unique identifier for the node to remove

        Returns:
            True if node was removed, False if node didn't exist
        """
        with self.lock:
            if node_id in self.nodes and node_id != self.node_id:
                del self.nodes[node_id]
                return True
            return False

    def _update_node(self, node_id: str):
        """
        Update the last seen timestamp for a node.

        Args:
            node_id: Unique identifier for the node to update
        """
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id].update_last_seen()

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Get the list of all nodes.

        Returns:
            List of node dictionaries
        """
        with self.lock:
            return [node.to_dict() for node in self.nodes.values()]

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a specific node by ID.

        Args:
            node_id: Unique identifier for the node

        Returns:
            Node object if found, None otherwise
        """
        with self.lock:
            return self.nodes.get(node_id)

    def _detect_failures(self):
        """
        Detect failed nodes based on last seen timestamps and failure counts.
        """
        current_time = time.time()
        with self.lock:
            for node_id, node in list(self.nodes.items()):
                if node_id == self.node_id:
                    continue  # Don't check ourselves

                # Check if node hasn't been seen for too long
                time_since_seen = current_time - node.last_seen
                if node.status == "alive":
                    if time_since_seen > self.probe_timeout:
                        node.failure_count += 1
                        if node.failure_count >= self.max_failure_count:
                            node.mark_failed()
                elif node.status == "failed":
                    # Failed nodes can be removed after some time
                    if time_since_seen > self.probe_timeout * 2:
                        del self.nodes[node_id]

    def _gossip_loop(self):
        """
        Main gossip loop that runs periodically.
        """
        while self.running:
            try:
                # Detect failures
                self._detect_failures()

                # Sleep for the gossip interval
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Error in gossip loop: {e}")
                break

    def start(self):
        """
        Start the gossip provider.
        """
        if not self.running:
            self.running = True
            self.gossip_thread = threading.Thread(
                target=self._gossip_loop,
                daemon=True
            )
            self.gossip_thread.start()
            print(f"SWIM Gossip provider started for node {self.node_id}")

    def stop(self):
        """
        Stop the gossip provider.
        """
        self.running = False
        if self.gossip_thread:
            self.gossip_thread.join(timeout=1.0)
            self.gossip_thread = None
        print(f"SWIM Gossip provider stopped for node {self.node_id}")

    def __del__(self):
        """
        Cleanup when the provider is destroyed.
        """
        self.stop()
