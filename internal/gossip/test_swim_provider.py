#!/usr/bin/env python3
"""
Unit tests for the SWIM Gossip provider.
"""

import unittest
import json
import time
import threading
from internal.gossip.swim_provider import SWIMGossipProvider, Node

class TestSWIMGossipProvider(unittest.TestCase):
    """
    Test cases for the SWIMGossipProvider class.
    """

    def test_initialization(self):
        """
        Test that the provider initializes correctly with default configuration.
        """
        provider = SWIMGossipProvider()
        self.assertIsInstance(provider, SWIMGossipProvider)
        self.assertEqual(provider.node_id[:5], "node_")
        self.assertEqual(provider.address, "127.0.0.1")
        self.assertEqual(provider.port, 8080)
        self.assertEqual(provider.gossip_interval, 1.0)

    def test_initialization_with_config(self):
        """
        Test initialization with custom configuration.
        """
        config = {
            "node_id": "test_node",
            "address": "192.168.1.1",
            "port": 9090,
            "gossip_interval": 2.0
        }
        provider = SWIMGossipProvider(config)
        self.assertEqual(provider.node_id, "test_node")
        self.assertEqual(provider.address, "192.168.1.1")
        self.assertEqual(provider.port, 9090)
        self.assertEqual(provider.gossip_interval, 2.0)

    def test_start_and_stop(self):
        """
        Test that the provider can be started and stopped gracefully.
        """
        provider = SWIMGossipProvider()
        provider.start()
        self.assertTrue(provider.running)
        self.assertIsNotNone(provider.gossip_thread)

        provider.stop()
        self.assertFalse(provider.running)

    def test_node_management(self):
        """
        Test node addition and updating.
        """
        provider = SWIMGossipProvider()
        initial_nodes = provider.get_nodes()
        self.assertEqual(len(initial_nodes), 1)
        self.assertEqual(initial_nodes[0]["id"], provider.node_id)

        # Add a new node
        provider._add_node("node2", "192.168.1.2", 8081)
        nodes = provider.get_nodes()
        self.assertEqual(len(nodes), 2)

        # Update node
        provider._update_node("node2")
        updated_nodes = provider.get_nodes()
        self.assertGreaterEqual(
            updated_nodes[1]["last_seen"],
            nodes[1]["last_seen"]
        )

    def test_invalid_config(self):
        """
        Test that invalid configuration raises an error.
        """
        with self.assertRaises(ValueError):
            SWIMGossipProvider("invalid_config")

if __name__ == "__main__":
    unittest.main()
