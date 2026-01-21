"""
SWIM Gossip Provider for Horcrux integration.
"""

from typing import Dict, List, Optional, Tuple
from ..swim.node_discovery import NodeDiscovery
from ..swim.gossip import GossipProtocol
from ..swim.gossip_propagation import GossipPropagation

class SWIMGossipProvider:
    """
    SWIM Gossip Provider for Horcrux cluster management.
    """

    def __init__(self, node_id: str, address: str, port: int, seed_nodes: Optional[List[Tuple[str, int]]] = None):
        """
        Initialize SWIM gossip provider.

        Args:
            node_id: Unique identifier for this node
            address: Network address of this node
            port: Network port of this node
            seed_nodes: List of (address, port) tuples for initial cluster members
        """
        self.node_id = node_id
        self.address = address
        self.port = port

        # Initialize SWIM components
        self.node_discovery = NodeDiscovery(node_id, address, port, seed_nodes)
        self.gossip_protocol = GossipProtocol(node_id, self.node_discovery)
        self.gossip_propagation = GossipPropagation(node_id, self.node_discovery)

    def start(self) -> None:
        """Start the SWIM gossip provider."""
        self.node_discovery.start()
        self.gossip_protocol.start()
        self.gossip_propagation.start()

    def stop(self) -> None:
        """Stop the SWIM gossip provider."""
        self.node_discovery.stop()
        self.gossip_protocol.stop()
        self.gossip_propagation.stop()

    def get_members(self) -> List[Dict]:
        """
        Get current cluster members.

        Returns:
            List of member dictionaries
        """
        members = self.node_discovery.get_members()
        return [member.to_dict() for member in members]

    def get_alive_members(self) -> List[Dict]:
        """
        Get alive cluster members.

        Returns:
            List of alive member dictionaries
        """
        members = self.node_discovery.get_alive_members()
        return [member.to_dict() for member in members]

    def inject_gossip_message(self, content: Dict) -> Dict:
        """
        Inject a gossip message into the cluster.

        Args:
            content: Message content

        Returns:
            Created message dictionary
        """
        message = self.gossip_protocol.inject_message(content)
        return message.to_dict()

    def get_gossip_message(self, message_id: str) -> Optional[Dict]:
        """
        Get a gossip message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message dictionary if found, None otherwise
        """
        message = self.gossip_protocol.get_message(message_id)
        return message.to_dict() if message else None

    def get_propagation_status(self, message_id: str) -> Optional[Dict]:
        """
        Get propagation status for a message.

        Args:
            message_id: Message ID

        Returns:
            Propagation status dictionary
        """
        nodes = self.gossip_propagation.get_propagation_status(message_id)
        if nodes:
            return {"message_id": message_id, "received_by": list(nodes)}
        return None

    def is_fully_propagated(self, message_id: str) -> bool:
        """
        Check if a message has been fully propagated.

        Args:
            message_id: Message ID

        Returns:
            True if fully propagated, False otherwise
        """
        return self.gossip_propagation.is_fully_propagated(message_id)

    def add_seed_node(self, address: str, port: int) -> None:
        """
        Add a seed node to the cluster.

        Args:
            address: Node address
            port: Node port
        """
        self.node_discovery.add_node(address, port)

    def configure(self, config: Dict) -> None:
        """
        Configure the SWIM provider.

        Args:
            config: Configuration dictionary
        """
        if 'gossip_interval' in config:
            self.node_discovery.gossip_interval = config['gossip_interval']
            self.gossip_protocol.gossip_interval = config['gossip_interval']

        if 'ping_timeout' in config:
            self.node_discovery.ping_timeout = config['ping_timeout']

        if 'failure_threshold' in config:
            self.node_discovery.failure_threshold = config['failure_threshold']
