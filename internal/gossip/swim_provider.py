import threading
import time
import random
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import logging
import socket
import json
from .types import NodeInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SWIMGossipProvider:
    """
    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    Gossip provider for node discovery and failure detection.
    """

    def __init__(self, node_id: str, address: str, port: int, config: Optional[Dict] = None):
        """
        Initialize the SWIM Gossip provider.

        Args:
            node_id: Unique identifier for this node
            address: Network address of this node
            port: Network port of this node
            config: Optional configuration dictionary
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.config = config or {}

        # Default configuration
        self.gossip_interval = self.config.get('gossip_interval', 1.0)  # seconds
        self.probe_timeout = self.config.get('probe_timeout', 1.0)  # seconds
        self.suspicion_timeout = self.config.get('suspicion_timeout', 3.0)  # seconds
        self.max_nodes = self.config.get('max_nodes', 100)

        # Node state
        self.nodes: Dict[str, NodeInfo] = {}
        self.running = False
        self.gossip_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Initialize with self
        self._update_node(node_id, address, port, status="alive")

        logger.info(f"SWIM Gossip provider initialized for node {self.node_id}")

    def _update_node(self, node_id: str, address: str, port: int, status: str = "alive") -> None:
        """Update or add a node to the local node list."""
        with self.lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.address = address
                node.port = port
                node.status = status
                node.last_seen = time.time()
                if status == "alive":
                    node.incarnation += 1
            else:
                self.nodes[node_id] = NodeInfo(
                    node_id=node_id,
                    address=address,
                    port=port,
                    status=status,
                    incarnation=1
                )

    def _ping_node(self, node_id: str, address: str, port: int) -> bool:
        """
        Ping a node to check if it's alive.
        Returns True if node responds, False otherwise.
        """
        try:
            # Create a TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.probe_timeout)

            # Try to connect
            result = sock.connect_ex((address, port))
            sock.close()

            if result == 0:
                # Connection successful
                return True
            return False
        except Exception as e:
            logger.debug(f"Ping failed for {node_id} at {address}:{port}: {e}")
            return False

    def _check_node_failures(self) -> None:
        """Check for nodes that should be marked as failed."""
        current_time = time.time()
        with self.lock:
            for node_id, node in list(self.nodes.items()):
                if node.status == "alive" and node_id != self.node_id:
                    # Check if node hasn't been seen for suspicion_timeout
                    if current_time - node.last_seen > self.suspicion_timeout:
                        logger.info(f"Marking node {node_id} as failed (not seen for {self.suspicion_timeout}s)")
                        self._update_node(node_id, node.address, node.port, status="failed")

    def _gossip_loop(self) -> None:
        """Main gossip loop that runs in a background thread."""
        while self.running:
            try:
                # Perform gossip
                self._perform_gossip()

                # Check for failures
                self._check_node_failures()

                time.sleep(self.gossip_interval)
            except Exception as e:
                logger.error(f"Error in gossip loop: {e}")
                time.sleep(1)  # Backoff on error

    def _perform_gossip(self) -> None:
        """
        Perform a single gossip round.
        """
        # Update our own timestamp
        self._update_node(self.node_id, self.address, self.port)

        # In a real implementation, this would:
        # 1. Select a random node to gossip with
        # 2. Exchange node lists
        # 3. Update local state
        # For now, we just ping nodes to check if they're alive
        with self.lock:
            for node_id, node in list(self.nodes.items()):
                if node_id != self.node_id and node.status == "alive":
                    # Try to ping the node
                    if not self._ping_node(node_id, node.address, node.port):
                        logger.debug(f"Ping failed for {node_id}")
                        # Don't mark as failed immediately, let _check_node_failures handle it

    def start(self) -> None:
        """
        Start the SWIM Gossip provider.
        """
        if self.running:
            return

        self.running = True
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()
        logger.info(f"SWIM Gossip provider started for node {self.node_id}")

    def stop(self) -> None:
        """
        Stop the SWIM Gossip provider gracefully.
        """
        self.running = False
        if self.gossip_thread and self.gossip_thread.is_alive():
            self.gossip_thread.join(timeout=1.0)
            if self.gossip_thread.is_alive():
                logger.warning(f"Gossip thread for node {self.node_id} did not stop gracefully")
            else:
                logger.info(f"Gossip thread for node {self.node_id} stopped gracefully")
        self.gossip_thread = None
        logger.info(f"SWIM Gossip provider stopped for node {self.node_id}")

    def get_nodes(self) -> List[NodeInfo]:
        """Get the current list of known nodes."""
        with self.lock:
            return list(self.nodes.values())

    def get_node(self, node_id: str) -> Optional[NodeInfo]:
        """Get information about a specific node."""
        with self.lock:
            return self.nodes.get(node_id)

    def add_node(self, node_id: str, address: str, port: int) -> None:
        """Add a new node to the cluster."""
        self._update_node(node_id, address, port, status="alive")

    def mark_node_failed(self, node_id: str) -> None:
        """Mark a node as failed."""
        if node_id in self.nodes:
            self._update_node(node_id, self.nodes[node_id].address, self.nodes[node_id].port, status="failed")

    def remove_node(self, node_id: str) -> None:
        """Remove a node from the cluster."""
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
