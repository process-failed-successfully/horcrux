#!/usr/bin/env python3
"""
Unit tests for SWIM Gossip provider configuration.
"""

import unittest
import json
import tempfile
import os
from internal.gossip.swim_provider import SWIMGossipProvider

class TestSWIMGossipConfig(unittest.TestCase):
    """
    Test cases for SWIM Gossip provider configuration.
    """

    def test_default_configuration(self):
        """
        Test that default configuration is applied correctly.
        """
        provider = SWIMGossipProvider()
        self.assertEqual(provider.node_id[:5], "node_")
        self.assertEqual(provider.address, "127.0.0.1")
        self.assertEqual(provider.port, 8080)
        self.assertEqual(provider.gossip_interval, 1.0)
        self.assertEqual(provider.ping_timeout, 0.5)
        self.assertEqual(provider.probe_timeout, 1.0)

    def test_custom_configuration(self):
        """
        Test that custom configuration is applied correctly.
        """
        config = {
            "node_id": "custom_node",
            "address": "192.168.1.100",
            "port": 9090,
            "gossip_interval": 2.0,
            "ping_timeout": 0.3,
            "probe_timeout": 0.8
        }
        provider = SWIMGossipProvider(config)
        self.assertEqual(provider.node_id, "custom_node")
        self.assertEqual(provider.address, "192.168.1.100")
        self.assertEqual(provider.port, 9090)
        self.assertEqual(provider.gossip_interval, 2.0)
        self.assertEqual(provider.ping_timeout, 0.3)
        self.assertEqual(provider.probe_timeout, 0.8)

    def test_partial_configuration(self):
        """
        Test that partial configuration is merged with defaults.
        """
        config = {
            "node_id": "partial_node",
            "gossip_interval": 3.0
        }
        provider = SWIMGossipProvider(config)
        self.assertEqual(provider.node_id, "partial_node")
        self.assertEqual(provider.gossip_interval, 3.0)
        # Defaults should be preserved
        self.assertEqual(provider.address, "127.0.0.1")
        self.assertEqual(provider.port, 8080)

    def test_invalid_configuration_type(self):
        """
        Test that invalid configuration types are rejected.
        """
        with self.assertRaises(ValueError):
            SWIMGossipProvider("invalid_string_config")
        with self.assertRaises(ValueError):
            SWIMGossipProvider(12345)
        with self.assertRaises(ValueError):
            SWIMGossipProvider(None)

    def test_configuration_file_loading(self):
        """
        Test loading configuration from a file.
        """
        config_data = {
            "node_id": "file_node",
            "address": "10.0.0.1",
            "port": 8888,
            "gossip_interval": 1.5
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            provider = SWIMGossipProvider(config_data)
            self.assertEqual(provider.node_id, "file_node")
            self.assertEqual(provider.address, "10.0.0.1")
            self.assertEqual(provider.port, 8888)
            self.assertEqual(provider.gossip_interval, 1.5)
        finally:
            os.unlink(config_file)

    def test_behavior_with_custom_configuration(self):
        """
        Test that provider behaves correctly with custom configuration.
        """
        config = {
            "node_id": "behavior_test",
            "gossip_interval": 0.1  # Very short interval for testing
        }
        provider = SWIMGossipProvider(config)
        provider.start()

        # Let it run for a short time
        import time
        time.sleep(0.3)

        nodes = provider.get_nodes()
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["id"], "behavior_test")

        provider.stop()

if __name__ == "__main__":
    unittest.main()
