import time
import random
import logging
from typing import Dict, List, Set, Optional, Any
from .failure_detection import FailureDetector

class SWIMProvider:
    """
    SWIM (Scalable Weakly-consistent Infection-style Process Group Membership Protocol)
    Gossip provider for node discovery and failure detection.
    """

    def __init__(self, node_id: str, seed_nodes: Optional[List[str]] = None,
                 gossip_interval: float = 1.0, logger: Optional[logging.Logger] = None):
        """
        Initialize the SWIM provider.

        Args:
            node_id: Unique identifier for this node
            seed_nodes: List of seed node IDs for initial discovery
            gossip_interval: Interval between gossip rounds (seconds)
            logger: Logger instance
        """
        self.node_id = node_id
        self.seed_nodes = seed_nodes or []
        self.gossip_interval = gossip_interval
        self.logger = logger or logging.getLogger(__name__)

        # Node membership
        self.members: Dict[str, Dict[str, Any]] = {}  # node_id -> metadata
        self.members[self.node_id] = {
            'id': self.node_id,
            'status': 'alive',
            'last_seen': time.time(),
            'incarnation': 1
        }

        # Failure detection
        self.failure_detector = FailureDetector(self)

        # Protocol state
        self.running = False
        self.last_gossip_time = 0

        self.logger.info(f"SWIM provider initialized for node {self.node_id}")

    def start(self):
        """Start the SWIM provider."""
        if self.running:
            self.logger.warning("SWIM provider already running")
            return

        self.running = True
        self.last_gossip_time = time.time()

        # Add seed nodes if any
        for seed_node in self.seed_nodes:
            if seed_node != self.node_id:
                self.members[seed_node] = {
                    'id': seed_node,
                    'status': 'unknown',
                    'last_seen': 0,
                    'incarnation': 1
                }

        self.logger.info(f"SWIM provider started for node {self.node_id}")

    def stop(self):
        """Stop the SWIM provider."""
        self.running = False
        self.logger.info(f"SWIM provider stopped for node {self.node_id}")

    def send_ping(self, target_node_id: str, timeout: float) -> Optional[Dict]:
        """
        Simulate sending a ping to a target node.

        Args:
            target_node_id: The node ID to ping
            timeout: Timeout for the ping

        Returns:
            Response dictionary or None
        """
        # In a real implementation, this would send a network message
        # For testing, we simulate the behavior

        # Check if target node exists in our membership
        if target_node_id in self.members:
            # Simulate network delay
            time.sleep(random.uniform(0.01, 0.1))

            # 90% chance of success for testing
            if random.random() < 0.9:
                return {
                    'type': 'pong',
                    'from': target_node_id,
                    'to': self.node_id,
                    'timestamp': time.time()
                }

        return None

    def send_ping_req(self, target_node_id: str, suspect_node_id: str, timeout: float) -> Optional[Dict]:
        """
        Simulate sending a ping request to check another node.

        Args:
            target_node_id: The node to send the request to
            suspect_node_id: The node to check
            timeout: Timeout for the request

        Returns:
            Response dictionary or None
        """
        # In a real implementation, this would send a network message
        # For testing, we simulate the behavior

        if target_node_id in self.members:
            time.sleep(random.uniform(0.01, 0.1))

            # 85% chance of success for testing
            if random.random() < 0.85:
                # Check if suspect node is alive
                if suspect_node_id in self.members:
                    return {
                        'type': 'ack',
                        'from': target_node_id,
                        'to': self.node_id,
                        'suspect': suspect_node_id,
                        'status': 'alive',
                        'timestamp': time.time()
                    }
                else:
                    return {
                        'type': 'ack',
                        'from': target_node_id,
                        'to': self.node_id,
                        'suspect': suspect_node_id,
                        'status': 'failed',
                        'timestamp': time.time()
                    }

        return None

    def gossip_round(self):
        """
        Perform a single gossip round:
        1. Select a random node to gossip with
        2. Exchange membership information
        3. Detect failures
        """
        if not self.running:
            return

        current_time = time.time()
        if current_time - self.last_gossip_time < self.gossip_interval:
            return

        self.last_gossip_time = current_time

        # Select a random node to gossip with (excluding self)
        available_nodes = [n for n in self.members.keys() if n != self.node_id]
        if not available_nodes:
            return

        target_node = random.choice(available_nodes)

        # Simulate gossip exchange
        self.logger.debug(f"Gossiping with node {target_node}")

        # Check if target node is responsive
        if not self.failure_detector.ping(target_node):
            self.failure_detector.suspect_node(target_node)
        else:
            # Node is alive, update membership
            self.members[target_node]['status'] = 'alive'
            self.members[target_node]['last_seen'] = current_time

        # Detect failures
        failed_nodes = self.failure_detector.detect_failures()
        for node_id in failed_nodes:
            if node_id in self.members:
                self.members[node_id]['status'] = 'failed'
                self.logger.warning(f"Node {node_id} marked as failed")

        # Clean up failed nodes periodically
        self._cleanup_failed_nodes()

    def _cleanup_failed_nodes(self):
        """Remove failed nodes from membership after some time."""
        current_time = time.time()
        to_remove = []

        for node_id, metadata in self.members.items():
            if metadata['status'] == 'failed':
                # Remove nodes that have been failed for more than 10 seconds
                if current_time - metadata.get('last_seen', 0) > 10:
                    to_remove.append(node_id)

        for node_id in to_remove:
            self.members.pop(node_id, None)
            self.logger.info(f"Removed failed node {node_id} from membership")

    def add_node(self, node_id: str):
        """
        Add a node to the membership list.

        Args:
            node_id: The node ID to add
        """
        if node_id not in self.members and node_id != self.node_id:
            self.members[node_id] = {
                'id': node_id,
                'status': 'unknown',
                'last_seen': 0,
                'incarnation': 1
            }
            self.logger.info(f"Added node {node_id} to membership")

    def get_members(self) -> List[str]:
        """
        Get the list of member node IDs.

        Returns:
            List of node IDs
        """
        return list(self.members.keys())

    def get_alive_members(self) -> List[str]:
        """
        Get the list of alive member node IDs.

        Returns:
            List of node IDs
        """
        return [node_id for node_id, metadata in self.members.items()
                if metadata['status'] == 'alive']

    def get_failure_detector_stats(self) -> Dict:
        """
        Get failure detector statistics.

        Returns:
            Dictionary of statistics
        """
        return self.failure_detector.get_stats()

    def run(self, duration: float = 10.0):
        """
        Run the SWIM provider for a specified duration.

        Args:
            duration: Duration to run (seconds)
        """
        self.start()
        start_time = time.time()

        try:
            while self.running and (time.time() - start_time) < duration:
                self.gossip_round()
                time.sleep(0.1)
        finally:
            self.stop()
