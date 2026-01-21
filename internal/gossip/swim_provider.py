import json
import os
import random
import socket
import threading
import time
from typing import Dict, List, Optional, Any

class SWIMGossipProvider:
    """
    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    Gossip provider for node discovery and failure detection.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SWIM Gossip provider.

        Args:
            config: Configuration dictionary for the provider.
        """
        self.config = config or {}
        self.node_id = self.config.get("node_id", f"node_{random.randint(1, 1000)}")
        self.host = self.config.get("host", "127.0.0.1")
        self.port = self.config.get("port", 8080)
        self.nodes: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.running = False
        self.gossip_thread: Optional[threading.Thread] = None

        # Add self to the node list
        self._add_node(self.node_id, self.host, self.port)

    def _add_node(self, node_id: str, host: str, port: int) -> None:
        """
        Add a node to the local node list.

        Args:
            node_id: Unique identifier for the node.
            host: Host address of the node.
            port: Port number of the node.
        """
        with self.lock:
            # Check if node already exists
            for node in self.nodes:
                if node["id"] == node_id:
                    return

            self.nodes.append({
                "id": node_id,
                "host": host,
                "port": port,
                "last_seen": time.time(),
                "status": "alive"
            })

    def add_node(self, node_id: str, host: str, port: int) -> None:
        """
        Public method to add a node to the local node list.

        Args:
            node_id: Unique identifier for the node.
            host: Host address of the node.
            port: Port number of the node.
        """
        self._add_node(node_id, host, port)

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node from the local node list.

        Args:
            node_id: Unique identifier for the node to remove.
        """
        with self.lock:
            self.nodes = [node for node in self.nodes if node["id"] != node_id]

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Get the list of known nodes.

        Returns:
            List of node dictionaries.
        """
        with self.lock:
            return [node.copy() for node in self.nodes]

    def start(self) -> None:
        """
        Start the gossip protocol.
        """
        if self.running:
            return

        self.running = True
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()

    def stop(self) -> None:
        """
        Stop the gossip protocol.
        """
        self.running = False
        if self.gossip_thread:
            self.gossip_thread.join()

    def _gossip_loop(self) -> None:
        """
        Main gossip loop for periodic node updates.
        """
        while self.running:
            self._gossip()
            time.sleep(self.config.get("gossip_interval", 1.0))

    def _gossip(self) -> None:
        """
        Perform a gossip round with a random node.
        """
        with self.lock:
            if len(self.nodes) < 2:
                return

            # Select a random node to gossip with
            target_node = random.choice(self.nodes)
            if target_node["id"] == self.node_id:
                return

            # Simulate gossip message exchange
            # In a real implementation, this would be a network call
            print(f"Gossiping with {target_node['id']}")

    def _detect_failures(self) -> None:
        """
        Detect node failures based on last seen time.
        """
        with self.lock:
            current_time = time.time()
            timeout = self.config.get("failure_timeout", 5.0)

            for node in self.nodes:
                if node["id"] == self.node_id:
                    continue

                if current_time - node["last_seen"] > timeout:
                    node["status"] = "suspected"
                    print(f"Node {node['id']} is suspected to have failed")

    def update_node(self, node_id: str, host: str, port: int) -> None:
        """
        Update an existing node's information.

        Args:
            node_id: Unique identifier for the node.
            host: Host address of the node.
            port: Port number of the node.
        """
        with self.lock:
            for node in self.nodes:
                if node["id"] == node_id:
                    node["host"] = host
                    node["port"] = port
                    node["last_seen"] = time.time()
                    node["status"] = "alive"
                    return

            # If node doesn't exist, add it
            self._add_node(node_id, host, port)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific node by ID.

        Args:
            node_id: Unique identifier for the node.

        Returns:
            Node dictionary if found, None otherwise.
        """
        with self.lock:
            for node in self.nodes:
                if node["id"] == node_id:
                    return node.copy()
            return None

    def load_config(self, config_file: str) -> None:
        """
        Load configuration from a file.

        Args:
            config_file: Path to the configuration file.
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found")

        with open(config_file, "r") as f:
            config = json.load(f)

        self.config.update(config)
        self.node_id = self.config.get("node_id", self.node_id)
        self.host = self.config.get("host", self.host)
        self.port = self.config.get("port", self.port)

    def save_config(self, config_file: str) -> None:
        """
        Save current configuration to a file.

        Args:
            config_file: Path to the configuration file.
        """
        with open(config_file, "w") as f:
            json.dump(self.config, f, indent=2)
