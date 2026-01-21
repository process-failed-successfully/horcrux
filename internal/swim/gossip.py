"""
SWIM Gossip Provider

Implements the gossip protocol for disseminating membership information.
"""

import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from .node_discovery import Node, NodeDiscovery

class GossipProvider:
    """
    Gossip protocol implementation for SWIM.
    """

    def __init__(self, node_discovery: NodeDiscovery):
        """
        Initialize the GossipProvider.

        Args:
            node_discovery: NodeDiscovery instance
        """
        self.node_discovery = node_discovery
        self.gossip_interval = 1.0  # seconds

    def gossip(self) -> Dict[str, Any]:
        """
        Perform a gossip round and return the gossip message.

        Returns:
            Gossip message containing membership information
        """
        # Get a random subset of nodes to gossip about
        nodes = self.node_discovery.discover_nodes()
        if len(nodes) <= 1:
            return {"nodes": []}

        # Select a random node to gossip about
        gossip_node = random.choice(nodes)
        if gossip_node.id == self.node_discovery.node_id:
            # Don't gossip about ourselves
            gossip_node = random.choice([n for n in nodes if n.id != self.node_discovery.node_id])

        return {
            "sender": self.node_discovery.node_id,
            "timestamp": time.time(),
            "node": asdict(gossip_node)
        }

    def receive_gossip(self, gossip_msg: Dict[str, Any]) -> None:
        """
        Receive and process a gossip message.

        Args:
            gossip_msg: Gossip message to process
        """
        node_data = gossip_msg.get('node', {})
        if not node_data:
            return

        node = Node(
            id=node_data['id'],
            address=node_data['address'],
            port=node_data['port'],
            status=node_data.get('status', 'alive'),
            last_seen=node_data.get('last_seen', time.time()),
            metadata=node_data.get('metadata', {})
        )

        # Update or add the node
        existing_node = self.node_discovery.get_node(node.id)
        if existing_node:
            self.node_discovery._update_node(node)
        else:
            self.node_discovery._add_node(node)

    def propagate_gossip(self, gossip_msg: Dict[str, Any], target_nodes: List[str]) -> None:
        """
        Propagate gossip to target nodes.

        Args:
            gossip_msg: Gossip message to propagate
            target_nodes: List of node IDs to propagate to
        """
        # In a real implementation, this would send the message over the network
        # For testing purposes, we'll simulate it by directly calling receive_gossip
        for node_id in target_nodes:
            if node_id != self.node_discovery.node_id:
                # Simulate network transmission
                time.sleep(0.01)
                self.receive_gossip(gossip_msg)
