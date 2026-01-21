"""
Failure detection module for SWIM Gossip provider.
"""

import time
from typing import Dict, Optional
from .types import NodeInfo

class FailureDetector:
    """
    Handles failure detection for nodes in the SWIM Gossip protocol.
    """

    def __init__(self, provider):
        """
        Initialize the failure detector.

        Args:
            provider: The SWIM Gossip provider instance
        """
        self.provider = provider
        self.failure_threshold = provider.config.get('failure_threshold', 3)
        self.ping_timeout = provider.config.get('ping_timeout', 0.5)

    def check_node_health(self, node_id: str) -> bool:
        """
        Check if a node is healthy.

        Args:
            node_id: The node ID to check

        Returns:
            True if the node is healthy, False otherwise
        """
        node = self.provider.get_node(node_id)
        if not node:
            return False

        # In a real implementation, this would ping the node
        # For now, we'll simulate based on last_seen
        time_since_seen = time.time() - node.last_seen
        if time_since_seen > self.ping_timeout * self.failure_threshold:
            return False

        return True

    def mark_failed_nodes(self) -> None:
        """
        Check all nodes and mark those that have failed.
        """
        nodes = self.provider.get_nodes()
        for node in nodes:
            if node.node_id == self.provider.node_id:
                continue  # Skip self

            if not self.check_node_health(node.node_id):
                self.provider.mark_node_failed(node.node_id)
