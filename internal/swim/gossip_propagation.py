"""
Gossip Propagation implementation for SWIM.
"""

import time
import threading
from typing import Dict, List, Optional, Set
from .gossip import GossipProtocol, GossipMessage
from .node_discovery import NodeDiscovery

class GossipPropagation(GossipProtocol):
    """
    Extended gossip protocol with propagation tracking.
    """

    def __init__(self, node_id: str, node_discovery: NodeDiscovery):
        """
        Initialize gossip propagation.

        Args:
            node_id: ID of the local node
            node_discovery: NodeDiscovery instance
        """
        super().__init__(node_id, node_discovery)
        self.propagation_log: Dict[str, Set[str]] = {}  # message_id -> set of node_ids

    def _process_message_content(self, message: GossipMessage) -> None:
        """
        Process message content and track propagation.

        Args:
            message: Gossip message
        """
        # Track that this node has received the message
        if message.message_id not in self.propagation_log:
            self.propagation_log[message.message_id] = set()

        self.propagation_log[message.message_id].add(self.node_id)

    def get_propagation_status(self, message_id: str) -> Optional[Set[str]]:
        """
        Get propagation status for a message.

        Args:
            message_id: Message ID

        Returns:
            Set of node IDs that have received the message, or None if not found
        """
        return self.propagation_log.get(message_id)

    def is_fully_propagated(self, message_id: str) -> bool:
        """
        Check if a message has been fully propagated to all nodes.

        Args:
            message_id: Message ID

        Returns:
            True if message has reached all nodes, False otherwise
        """
        received_by = self.get_propagation_status(message_id)
        if not received_by:
            return False

        all_nodes = set(node.node_id for node in self.node_discovery.get_members())
        return received_by == all_nodes
