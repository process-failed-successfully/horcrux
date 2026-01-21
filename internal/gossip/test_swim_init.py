import unittest
from unittest.mock import MagicMock, patch
from internal.gossip.swim_provider import SWIMProvider
from internal.gossip.types import Node

class TestSWIMInit(unittest.TestCase):
    """Test SWIM Gossip provider initialization"""

    def test_import_module(self):
        """Step 1: Import the SWIM Gossip provider module"""
        try:
            from internal.gossip import swim_provider
            self.assertTrue(True, "Module imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import module: {e}")

    def test_initialize_with_default_config(self):
        """Step 2: Initialize the provider with default configuration"""
        try:
            provider = SWIMProvider()
            self.assertIsNotNone(provider, "Provider initialized successfully")
            self.assertEqual(provider.node_id, "default-node")
            self.assertEqual(provider.port, 8080)
            self.assertEqual(provider.gossip_interval, 1.0)
        except Exception as e:
            self.fail(f"Failed to initialize provider: {e}")

    def test_initialize_without_errors(self):
        """Step 3: Verify the provider is initialized without errors"""
        try:
            provider = SWIMProvider()
            # Verify basic attributes exist
            self.assertTrue(hasattr(provider, 'nodes'))
            self.assertTrue(hasattr(provider, 'is_running'))
            self.assertFalse(provider.is_running)
        except Exception as e:
            self.fail(f"Initialization failed with error: {e}")

    def test_stop_gracefully(self):
        """Step 4: Check that the provider can be stopped gracefully"""
        provider = SWIMProvider()
        # Start the provider
        provider.start()
        self.assertTrue(provider.is_running)

        # Stop the provider
        provider.stop()
        self.assertFalse(provider.is_running)

if __name__ == '__main__':
    unittest.main()
