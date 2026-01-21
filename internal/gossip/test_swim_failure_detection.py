#!/usr/bin/env python3
"""
Unit tests for SWIM Gossip failure detection.
"""

import unittest
import time
import threading
from internal.gossip.swim_provider import SWIMGossipProvider

class TestFailureDetection(unittest.TestCase):
    """
    Test cases for SWIM Gossip failure detection.
    """

    def test_failure_detection_basic(self):
        """
        Test basic failure detection mechanism.
        """
        # Create a provider
        provider = SWIMGossipProvider(
            node_id="test_node",
            address="127.0.0.1",
            port=9999
        )

        # Add a node that doesn't exist (will fail to ping)
        provider.add_node("dead_node", "192.168.1.1", 9998)

        # Verify node is initially alive
        nodes = provider.get_nodes()
        dead_node = [n for n in nodes if n.node_id == "dead_node"][0]
        self.assertEqual(dead_node.status, "alive")

        # Start the provider
        provider.start()

        # Wait for failure detection to kick in
        time.sleep(3)

        # Check if node is marked as failed
        nodes = provider.get_nodes()
        dead_node = [n for n in nodes if n.node_id == "dead_node"][0]
        self.assertEqual(dead_node.status, "failed")

        # Stop the provider
        provider.stop()

    def test_failure_threshold(self):
        """
        Test that failure threshold is respected.
        """
        provider = SWIMGossipProvider(
            node_id="test_node",
            address="127.0.0.1",
            port=9997
        )

        # Add a node
        provider.add_node("test_node2", "192.168.1.1", 9996)

        # Start the provider
        provider.start()

        # Wait for some failures but not enough to trigger failure detection
        time.sleep(2)

        # Check that node is still alive
        nodes = provider.get_nodes()
        test_node = [n for n in nodes if n.node_id == "test_node2"][0]
        self.assertEqual(test_node.status, "alive")

        # Stop the provider
        provider.stop()

    def test_self_node_always_alive(self):
        """
        Test that the node itself is always marked as alive.
        """
        provider = SWIMGossipProvider(
            node_id="self_node",
            address="127.0.0.1",
            port=9995
        )

        # Start the provider
        provider.start()

        # Wait for some time
        time.sleep(2)

        # Check that self node is always alive
        nodes = provider.get_nodes()
        self_node = [n for n in nodes if n.node_id == "self_node"][0]
        self.assertEqual(self_node.status, "alive")

        # Stop the provider
        provider.stop()

if __name__ == "__main__":
    unittest.main()
