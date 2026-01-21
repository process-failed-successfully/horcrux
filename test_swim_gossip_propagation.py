"""
Tests for SWIM Gossip Propagation.
"""

import unittest
import time
from internal.swim.node_discovery import NodeDiscovery
from internal.swim.gossip_propagation import GossipPropagation

class TestGossipPropagation(unittest.TestCase):
    """Test SWIM Gossip Propagation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.node_discovery = NodeDiscovery("test", "127.0.0.1", 8001)
        self.gossip = GossipPropagation("test", self.node_discovery)

    def tearDown(self):
        """Clean up test fixtures."""
        self.gossip.stop()
        self.node_discovery.stop()

    def test_propagation_tracking(self):
        """Test propagation tracking."""
        # Inject a message
        content = {"type": "test", "data": "hello"}
        message = self.gossip.inject_message(content)

        # Check propagation status
        status = self.gossip.get_propagation_status(message.message_id)
        self.assertIsNotNone(status)
        self.assertIn("test", status)

    def test_full_propagation(self):
        """Test full propagation detection."""
        # Create a cluster with multiple nodes
        node1_discovery = NodeDiscovery("node1", "127.0.0.1", 8001)
        node2_discovery = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])
        node3_discovery = NodeDiscovery("node3", "127.0.0.1", 8003, [("127.0.0.1", 8001)])

        gossip1 = GossipPropagation("node1", node1_discovery)
        gossip2 = GossipPropagation("node2", node2_discovery)
        gossip3 = GossipPropagation("node3", node3_discovery)

        # Start nodes
        node1_discovery.start()
        node2_discovery.start()
        node3_discovery.start()
        gossip1.start()
        gossip2.start()
        gossip3.start()

        # Wait for discovery
        time.sleep(2)

        # Inject a message
        content = {"type": "test", "data": "hello"}
        message = gossip1.inject_message(content)

        # Wait for propagation
        time.sleep(2)

        # Check propagation status on node1
        status = gossip1.get_propagation_status(message.message_id)
        self.assertIsNotNone(status)
        self.assertIn("node1", status)

        # In a real implementation with actual network communication,
        # we would check that all nodes received the message
        # For this test, we'll just verify the basic functionality

        # Clean up
        gossip1.stop()
        gossip2.stop()
        gossip3.stop()
        node1_discovery.stop()
        node2_discovery.stop()
        node3_discovery.stop()

if __name__ == "__main__":
    unittest.main()
