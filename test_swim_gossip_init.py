"""
Unit tests for SWIM Gossip provider initialization.
"""

import unittest
import asyncio
from internal.gossip import SWIMGossipProvider

class TestSWIMGossipInit(unittest.TestCase):
    def test_initialization(self):
        """Test that the SWIM Gossip provider initializes correctly."""
        provider = SWIMGossipProvider()
        self.assertIsNotNone(provider)
        self.assertEqual(provider.config['node_id'], provider.config['node_id'])
        self.assertIn('node_id', provider.config)
        self.assertIn('listen_port', provider.config)
        self.assertIn('gossip_interval', provider.config)

    def test_default_config(self):
        """Test that default configuration is applied when none is provided."""
        provider = SWIMGossipProvider()
        self.assertEqual(provider.config['listen_port'], 8000)
        self.assertEqual(provider.config['gossip_interval'], 1.0)

    def test_custom_config(self):
        """Test that custom configuration is applied correctly."""
        custom_config = {
            'node_id': 'test_node',
            'listen_port': 9000,
            'gossip_interval': 2.0
        }
        provider = SWIMGossipProvider(custom_config)
        self.assertEqual(provider.config['node_id'], 'test_node')
        self.assertEqual(provider.config['listen_port'], 9000)
        self.assertEqual(provider.config['gossip_interval'], 2.0)

    def test_start_stop(self):
        """Test that the provider can be started and stopped gracefully."""
        provider = SWIMGossipProvider()

        # Test start
        asyncio.run(provider.start())
        self.assertTrue(provider.running)

        # Test stop
        asyncio.run(provider.stop())
        self.assertFalse(provider.running)

    def test_node_management(self):
        """Test that the provider manages its own node correctly."""
        provider = SWIMGossipProvider()
        nodes = provider.get_nodes()
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]['status'], 'alive')

if __name__ == '__main__':
    unittest.main()
