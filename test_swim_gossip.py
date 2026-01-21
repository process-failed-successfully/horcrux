#!/usr/bin/env python3
"""
Unit tests for SWIM Gossip Provider
"""

import asyncio
import unittest
import time
from internal.gossip.swim_gossip import SWIMGossipProvider

class TestSWIMGossipProvider(unittest.TestCase):
    """Test cases for SWIM Gossip Provider."""

    def setUp(self):
        """Set up test fixtures."""
        self.node_id = "test-node-1"
        self.config = {
            "gossip_interval": 0.1,
            "ping_timeout": 0.1,
            "ping_req_timeout": 0.2,
            "suspect_timeout": 0.5,
            "max_nodes": 10,
            "seed_nodes": ["seed-node-1", "seed-node-2"]
        }

    def test_initialization(self):
        """Test that the provider initializes correctly."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        # Verify basic properties
        self.assertEqual(provider.node_id, self.node_id)
        self.assertEqual(provider.config["gossip_interval"], 0.1)
        self.assertEqual(provider.config["ping_timeout"], 0.1)

        # Verify nodes are initialized
        self.assertIn(self.node_id, provider.nodes)
        self.assertIn("seed-node-1", provider.nodes)
        self.assertIn("seed-node-2", provider.nodes)

        # Verify node count
        self.assertEqual(len(provider.nodes), 3)  # self + 2 seeds

    def test_initialization_with_default_config(self):
        """Test initialization with default configuration."""
        provider = SWIMGossipProvider(self.node_id)

        # Verify default values
        self.assertEqual(provider.config["gossip_interval"], 1.0)
        self.assertEqual(provider.config["ping_timeout"], 0.5)
        self.assertEqual(provider.config["ping_req_timeout"], 1.0)
        self.assertEqual(provider.config["suspect_timeout"], 2.0)
        self.assertEqual(provider.config["max_nodes"], 100)

        # Verify only self node is present
        self.assertEqual(len(provider.nodes), 1)
        self.assertIn(self.node_id, provider.nodes)

    def test_invalid_config(self):
        """Test that invalid configurations are rejected."""
        invalid_configs = [
            {"gossip_interval": -1},  # Negative interval
            {"ping_timeout": 0},      # Zero timeout
            {"max_nodes": -5},        # Negative max nodes
            {"seed_nodes": "not-a-list"}  # Invalid seed nodes type
        ]

        for config in invalid_configs:
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    SWIMGossipProvider(self.node_id, config)

    def test_start_stop(self):
        """Test that the provider can be started and stopped gracefully."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        # Verify provider is not running initially
        self.assertFalse(provider.running)

        # Start the provider
        asyncio.run(provider.start())

        # Verify provider is running
        self.assertTrue(provider.running)

        # Stop the provider
        asyncio.run(provider.stop())

        # Verify provider is stopped
        self.assertFalse(provider.running)

    def test_get_nodes(self):
        """Test getting the list of nodes."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        nodes = provider.get_nodes()

        # Verify nodes structure
        self.assertIn(self.node_id, nodes)
        self.assertIn("seed-node-1", nodes)
        self.assertIn("seed-node-2", nodes)

        # Verify node info structure
        for node_id, info in nodes.items():
            self.assertIn("address", info)
            self.assertIn("status", info)
            self.assertIn("timestamp", info)
            self.assertEqual(info["status"], "alive")

    def test_get_alive_nodes(self):
        """Test getting the list of alive nodes."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        alive_nodes = provider.get_alive_nodes()

        # Verify all nodes are alive initially
        self.assertEqual(len(alive_nodes), 3)
        self.assertIn(self.node_id, alive_nodes)
        self.assertIn("seed-node-1", alive_nodes)
        self.assertIn("seed-node-2", alive_nodes)

    def test_get_suspect_nodes(self):
        """Test getting the list of suspect nodes."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        suspect_nodes = provider.get_suspect_nodes()

        # Verify no suspect nodes initially
        self.assertEqual(len(suspect_nodes), 0)

    def test_get_failed_nodes(self):
        """Test getting the list of failed nodes."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        failed_nodes = provider.get_failed_nodes()

        # Verify no failed nodes initially
        self.assertEqual(len(failed_nodes), 0)

    def test_multiple_start_stop(self):
        """Test that the provider can be started and stopped multiple times."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        # First start/stop cycle
        asyncio.run(provider.start())
        self.assertTrue(provider.running)

        asyncio.run(provider.stop())
        self.assertFalse(provider.running)

        # Second start/stop cycle
        asyncio.run(provider.start())
        self.assertTrue(provider.running)

        asyncio.run(provider.stop())
        self.assertFalse(provider.running)

    def test_str_representation(self):
        """Test string representation of the provider."""
        provider = SWIMGossipProvider(self.node_id, self.config)

        str_repr = str(provider)
        self.assertIn(self.node_id, str_repr)
        self.assertIn("SWIMGossipProvider", str_repr)

if __name__ == "__main__":
    unittest.main()
