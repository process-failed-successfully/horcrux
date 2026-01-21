import time
import threading
import random
from typing import Dict, List, Optional
from internal.gossip.types import Node, NodeStatus

class SWIMProvider:
    """
    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    Gossip provider for node discovery and failure detection.
    """

    def __init__(self, node_id: str = "default-node", port: int = 8080,
                 gossip_interval: float = 1.0, protocol_period: float = 1.0):
        """
        Initialize the SWIM Gossip provider with configuration.

        Args:
            node_id: Unique identifier for this node
            port: Port to listen on
            gossip_interval: Interval between gossip rounds in seconds
            protocol_period: Protocol period for SWIM in seconds
        """
        self.node_id = node_id
        self.port = port
        self.gossip_interval = gossip_interval
        self.protocol_period = protocol_period

        # Node management
        self.nodes: Dict[str, Node] = {}
        self.lock = threading.Lock()
        self.is_running = False
        self.gossip_thread: Optional[threading.Thread] = None

        # Add self to the node list
        self._add_node(Node(
            id=self.node_id,
            address=f"localhost:{self.port}",
            status=NodeStatus.ALIVE,
            incarnation=0
        ))

    def _add_node(self, node: Node):
        """Add or update a node in the local node list."""
        with self.lock:
            self.nodes[node.id] = node

    def _remove_node(self, node_id: str):
        """Remove a node from the local node list."""
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]

    def start(self):
        """Start the SWIM gossip provider."""
        if self.is_running:
            return

        self.is_running = True
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()

    def stop(self):
        """Stop the SWIM gossip provider gracefully."""
        self.is_running = False
        if self.gossip_thread:
            self.gossip_thread.join(timeout=1.0)
            self.gossip_thread = None

    def _gossip_loop(self):
        """Main gossip loop that runs periodically."""
        while self.is_running:
            try:
                self._perform_gossip_round()
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Error in gossip loop: {e}")
                time.sleep(1.0)

    def _perform_gossip_round(self):
        """Perform a single gossip round."""
        # In a real implementation, this would:
        # 1. Select a random node to ping
        # 2. Perform the ping
        # 3. Update node status based on response
        # 4. Share membership information
        pass

    def get_nodes(self) -> List[Node]:
        """Get the current list of known nodes."""
        with self.lock:
            return list(self.nodes.values())

    def __str__(self):
        return f"SWIMProvider(node_id={self.node_id}, port={self.port}, nodes={len(self.nodes)})"
