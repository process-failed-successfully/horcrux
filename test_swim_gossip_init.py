"""
Tests for SWIM Gossip initialization and basic functionality.
"""

import unittest
import time
from internal.swim.node_discovery import NodeDiscovery
from internal.swim.gossip import GossipProtocol

class TestSWIMGossipInit(unittest.TestCase):
    """Test SWIM Gossip initialization and basic functionality."""

    def test_gossip_initialization(self):
        """Test that gossip protocol initializes correctly."""
        node_discovery = NodeDiscovery("test", "127.0.0.1", 8001)
        gossip = GossipProtocol("test", node_discovery)

        # Verify initial state
        self.assertFalse(gossip.running)
        self.assertEqual(gossip.node_id, "test")
        self.assertEqual(len(gossip.message_store), 0)
        self.assertEqual(len(gossip.message_queue), 0)

        # Start gossip
        gossip.start()
        self.assertTrue(gossip.running)

        # Stop gossip
        gossip.stop()
        self.assertFalse(gossip.running)

        # Clean up
        node_discovery.stop()

    def test_message_injection(self):
        """Test message injection and retrieval."""
        node_discovery = NodeDiscovery("test", "127.0.0.1", 8001)
        gossip = GossipProtocol("test", node_discovery)
        gossip.start()

        # Inject a message
        content = {"type": "test", "data": "hello world"}
        message = gossip.inject_message(content)

        # Verify message properties
        self.assertEqual(message.sender_id, "test")
        self.assertEqual(message.content, content)
        self.assertGreater(message.timestamp, 0)
        self.assertEqual(message.ttl, 5)

        # Verify message is stored
        self.assertEqual(len(gossip.message_store), 1)
        self.assertEqual(len(gossip.message_queue), 1)

        # Retrieve message
        retrieved = gossip.get_message(message.message_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.message_id, message.message_id)

        # Clean up
        gossip.stop()
        node_discovery.stop()

    def test_multiple_messages(self):
        """Test handling of multiple messages."""
        node_discovery = NodeDiscovery("test", "127.0.0.1", 8001)
        gossip = GossipProtocol("test", node_discovery)
        gossip.start()

        # Inject multiple messages
        messages = []
        for i in range(5):
            content = {"type": "test", "data": f"message {i}"}
            message = gossip.inject_message(content)
            messages.append(message)

        # Verify all messages are stored
        self.assertEqual(len(gossip.message_store), 5)
        self.assertEqual(len(gossip.message_queue), 5)

        # Verify all messages can be retrieved
        for message in messages:
            retrieved = gossip.get_message(message.message_id)
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.content, message.content)

        # Clean up
        gossip.stop()
        node_discovery.stop()

if __name__ == "__main__":
    unittest.main()
