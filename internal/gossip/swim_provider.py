import time
import threading
import random
from typing import Dict, List, Optional, Callable
from .types import Node, Message

class SWIMGossipProvider:
    """
    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    Gossip provider for node discovery and failure detection.
    """

    def __init__(self, node_id: str, host: str, port: int, config: Optional[Dict] = None):
        """
        Initialize the SWIM Gossip provider.

        Args:
            node_id: Unique identifier for this node
            host: Host address for this node
            port: Port number for this node
            config: Optional configuration dictionary
        """
        self.node_id = node_id
        self.host = host
        self.port = port
        self.config = config or {}
        self.running = False
        self.members: Dict[str, Node] = {}
        self.lock = threading.Lock()

        # Default configuration
        self.gossip_interval = self.config.get('gossip_interval', 1.0)
        self.failure_timeout = self.config.get('failure_timeout', 3.0)
        self.probe_timeout = self.config.get('probe_timeout', 1.0)

        # Add self to members
        self._add_node(Node(node_id, host, port, time.time()))

    def _add_node(self, node: Node) -> None:
        """Add a node to the membership list."""
        with self.lock:
            self.members[node.id] = node

    def _remove_node(self, node_id: str) -> None:
        """Remove a node from the membership list."""
        with self.lock:
            if node_id in self.members:
                del self.members[node_id]

    def start(self) -> None:
        """Start the gossip provider."""
        if self.running:
            return

        self.running = True
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()

    def stop(self) -> None:
        """Stop the gossip provider gracefully."""
        self.running = False
        if hasattr(self, 'gossip_thread'):
            self.gossip_thread.join(timeout=1.0)

    def _gossip_loop(self) -> None:
        """Main gossip loop."""
        while self.running:
            try:
                self._perform_gossip()
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Error in gossip loop: {e}")
                time.sleep(1.0)

    def _perform_gossip(self) -> None:
        """Perform a single gossip round."""
        if not self.members:
            return

        # Select a random node to gossip with
        nodes = list(self.members.values())
        if len(nodes) == 1:
            return  # Only self in the list

        target = random.choice(nodes)
        if target.id == self.node_id:
            return  # Don't gossip with self

        # In a real implementation, this would send a gossip message
        # For now, we'll just simulate it
        print(f"Gossiping with {target.id}")

    def get_members(self) -> List[Node]:
        """Get the current list of members."""
        with self.lock:
            return list(self.members.values())

    def is_running(self) -> bool:
        """Check if the provider is running."""
        return self.running
