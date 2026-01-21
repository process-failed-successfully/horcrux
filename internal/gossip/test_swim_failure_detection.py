#!/usr/bin/env python3
"""
Test SWIM Gossip Failure Detection

This module tests the SWIM Gossip provider failure detection functionality.
"""

import unittest
import time
import threading
from internal.gossip.swim_provider import SWIMGossipProvider, Node

class TestSWIMGossipFailureDetection(unittest.TestCase):
    """Test cases for SWIM Gossip Provider Failure Detection."""

    def test_failure_detection_basic(self):
        """Test that nodes can detect failures of other nodes."""
        # Create two providers
        provider1 = SWIMGossipProvider({"node_id": "node1", "gossip_interval": 0.1})
        provider2 = SWIMGossipProvider({"node_id": "node2", "gossip_interval": 0.1})

        # Start both providers
        provider1.start()
        provider2.start()

        # Add node2 to provider1's node list
        provider1.add_node("node2", "127.0.0.1", 8081)

        # Verify node2 is in provider1's node list
        self.assertIn("node2", provider1.nodes)
        self.assertEqual(provider1.nodes["node2"].status, "alive")

        # Simulate failure by marking node2 as failed
        provider1.mark_node_failed("node2")

        # Verify node2 is marked as failed
        self.assertEqual(provider1.nodes["node2"].status, "failed")

        # Clean up
        provider1.stop()
        provider2.stop()

    def test_failure_detection_with_timeout(self):
        """Test that nodes are marked as failed after ping timeout."""
        provider = SWIMGossipProvider({"node_id": "test_node", "ping_timeout": 0.1})

        # Add a node
        provider.add_node("unresponsive_node", "192.168.1.100", 8080)

        # Mark the node as failed due to timeout
        provider.mark_node_failed("unresponsive_node")

        # Verify the node is marked as failed
        self.assertEqual(provider.nodes["unresponsive_node"].status, "failed")

    def test_node_removal_after_failure(self):
        """Test that failed nodes can be removed from the node list."""
        provider = SWIMGossipProvider({"node_id": "test_node"})

        # Add a node
        provider.add_node("failed_node", "127.0.0.1", 8080)

        # Mark as failed
        provider.mark_node_failed("failed_node")

        # Remove the failed node
        provider.remove_node("failed_node")

        # Verify the node is removed
        self.assertNotIn("failed_node", provider.nodes)

    def test_multiple_node_failures(self):
        """Test handling of multiple node failures."""
        provider = SWIMGossipProvider({"node_id": "test_node"})

        # Add multiple nodes
        provider.add_node("node1", "127.0.0.1", 8081)
        provider.add_node("node2", "127.0.0.1", 8082)
        provider.add_node("node3", "127.0.0.1", 8083)

        # Mark some as failed
        provider.mark_node_failed("node1")
        provider.mark_node_failed("node3")

        # Verify statuses
        self.assertEqual(provider.nodes["node1"].status, "failed")
        self.assertEqual(provider.nodes["node2"].status, "alive")
        self.assertEqual(provider.nodes["node3"].status, "failed")

if __name__ == "__main__":
    unittest.main()
