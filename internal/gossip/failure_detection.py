import time
import random
from typing import Dict, List, Set, Optional
from .swim_provider import SWIMProvider

class FailureDetector:
    """
    Implements failure detection using the SWIM (Scalable Weakly-consistent
    Infection-style Process Group Membership Protocol) gossip protocol.

    This detector monitors nodes and detects failures through:
    1. Ping/Pong mechanism
    2. Indirect failure detection through gossip
    3. Suspicion mechanism with timeout
    """

    def __init__(self, swim_provider: SWIMProvider, ping_timeout: float = 1.0,
                 ping_req_timeout: float = 0.5, suspicion_timeout: float = 3.0):
        """
        Initialize the failure detector.

        Args:
            swim_provider: The SWIM provider instance
            ping_timeout: Timeout for ping responses (seconds)
            ping_req_timeout: Timeout for ping request forwarding (seconds)
            suspicion_timeout: Time before a suspected node is declared failed (seconds)
        """
        self.swim_provider = swim_provider
        self.ping_timeout = ping_timeout
        self.ping_req_timeout = ping_req_timeout
        self.suspicion_timeout = suspicion_timeout

        # Node state tracking
        self.suspected_nodes: Dict[str, float] = {}  # node_id -> suspicion_time
        self.failed_nodes: Set[str] = set()
        self.alive_nodes: Set[str] = set()

        # Protocol counters
        self.ping_count = 0
        self.pong_count = 0
        self.ping_req_count = 0
        self.ack_count = 0

    def detect_failures(self) -> List[str]:
        """
        Detect and return failed nodes.

        Returns:
            List of node IDs that have failed
        """
        current_time = time.time()
        newly_failed = []

        # Check suspected nodes that have timed out
        timed_out_suspicions = [
            node_id for node_id, suspicion_time in self.suspected_nodes.items()
            if current_time - suspicion_time > self.suspicion_timeout
        ]

        for node_id in timed_out_suspicions:
            if node_id not in self.failed_nodes:
                self.failed_nodes.add(node_id)
                self.suspected_nodes.pop(node_id, None)
                if node_id in self.alive_nodes:
                    self.alive_nodes.remove(node_id)
                newly_failed.append(node_id)
                self.swim_provider.logger.info(f"Node {node_id} declared as failed")

        return newly_failed

    def ping(self, target_node_id: str) -> bool:
        """
        Send a ping to a target node and wait for pong response.

        Args:
            target_node_id: The node ID to ping

        Returns:
            True if pong received, False otherwise
        """
        self.ping_count += 1
        try:
            # Simulate network communication
            start_time = time.time()
            response = self.swim_provider.send_ping(target_node_id, self.ping_timeout)

            if response and response.get('type') == 'pong':
                self.pong_count += 1
                self.alive_nodes.add(target_node_id)
                if target_node_id in self.suspected_nodes:
                    self.suspected_nodes.pop(target_node_id)
                return True
            return False
        except Exception as e:
            self.swim_provider.logger.warning(f"Ping to {target_node_id} failed: {str(e)}")
            return False

    def ping_req(self, target_node_id: str, suspect_node_id: str) -> bool:
        """
        Send a ping request to check another node (indirect ping).

        Args:
            target_node_id: The node to send the ping request to
            suspect_node_id: The node to check

        Returns:
            True if ack received, False otherwise
        """
        self.ping_req_count += 1
        try:
            response = self.swim_provider.send_ping_req(
                target_node_id, suspect_node_id, self.ping_req_timeout
            )

            if response and response.get('type') == 'ack':
                self.ack_count += 1
                # Node is alive, remove from suspected
                if suspect_node_id in self.suspected_nodes:
                    self.suspected_nodes.pop(suspect_node_id)
                return True
            return False
        except Exception as e:
            self.swim_provider.logger.warning(
                f"Ping request to {target_node_id} for {suspect_node_id} failed: {str(e)}"
            )
            return False

    def suspect_node(self, node_id: str):
        """
        Mark a node as suspected.

        Args:
            node_id: The node ID to suspect
        """
        if node_id not in self.failed_nodes and node_id not in self.suspected_nodes:
            self.suspected_nodes[node_id] = time.time()
            self.swim_provider.logger.warning(f"Node {node_id} suspected as failed")
            if node_id in self.alive_nodes:
                self.alive_nodes.remove(node_id)

    def handle_ping(self, sender_id: str) -> Dict:
        """
        Handle an incoming ping message.

        Args:
            sender_id: The node ID that sent the ping

        Returns:
            Pong response
        """
        # Update alive status of sender
        self.alive_nodes.add(sender_id)
        if sender_id in self.suspected_nodes:
            self.suspected_nodes.pop(sender_id)

        return {
            'type': 'pong',
            'from': self.swim_provider.node_id,
            'to': sender_id,
            'timestamp': time.time()
        }

    def handle_ping_req(self, sender_id: str, suspect_node_id: str) -> Dict:
        """
        Handle an incoming ping request.

        Args:
            sender_id: The node ID that sent the request
            suspect_node_id: The node to check

        Returns:
            Ack or Nack response
        """
        # First try to ping the suspect node directly
        if self.ping(suspect_node_id):
            # Node responded, send ack
            return {
                'type': 'ack',
                'from': self.swim_provider.node_id,
                'to': sender_id,
                'suspect': suspect_node_id,
                'status': 'alive',
                'timestamp': time.time()
            }
        else:
            # Node didn't respond, send nack
            return {
                'type': 'ack',
                'from': self.swim_provider.node_id,
                'to': sender_id,
                'suspect': suspect_node_id,
                'status': 'failed',
                'timestamp': time.time()
            }

    def get_node_status(self, node_id: str) -> str:
        """
        Get the status of a node.

        Args:
            node_id: The node ID to check

        Returns:
            One of: 'alive', 'suspected', 'failed', 'unknown'
        """
        if node_id in self.failed_nodes:
            return 'failed'
        elif node_id in self.suspected_nodes:
            return 'suspected'
        elif node_id in self.alive_nodes:
            return 'alive'
        return 'unknown'

    def get_stats(self) -> Dict:
        """
        Get statistics about the failure detector.

        Returns:
            Dictionary of statistics
        """
        return {
            'ping_count': self.ping_count,
            'pong_count': self.pong_count,
            'ping_req_count': self.ping_req_count,
            'ack_count': self.ack_count,
            'suspected_nodes': len(self.suspected_nodes),
            'failed_nodes': len(self.failed_nodes),
            'alive_nodes': len(self.alive_nodes)
        }
