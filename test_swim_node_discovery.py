"""
Tests for SWIM Node Discovery.
"""

import unittest
import time
import threading
from internal.swim.node_discovery import NodeDiscovery, Node

class TestNodeDiscovery(unittest.TestCase):
    """Test SWIM Node Discovery functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.node1 = NodeDiscovery("node1", "127.0.0.1", 8001)
        self.node2 = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])
        self.node3 = NodeDiscovery("node3", "127.0.0.1", 8003, [("127.0.0.1", 8001)])

    def tearDown(self):
        """Clean up test fixtures."""
        self.node1.stop()
        self.node2.stop()
        self.node3.stop()

    def test_initial_membership(self):
        """Test that nodes start with correct initial membership."""
        # Node1 should only know about itself
        members = self.node1.get_members()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].node_id, "node1")

        # Node2 should know about itself and node1
        members = self.node2.get_members()
        self.assertEqual(len(members), 2)
        node_ids = {m.node_id for m in members}
        self.assertIn("node2", node_ids)
        self.assertIn("node1", node_ids)

    def test_node_discovery(self):
        """Test that nodes can discover each other."""
        # Start all nodes
        self.node1.start()
        self.node2.start()
        self.node3.start()

        # Wait for gossip to propagate
        time.sleep(2)

        # Check that all nodes have discovered each other
        for node in [self.node1, self.node2, self.node3]:
            members = node.get_members()
            member_ids = {m.node_id for m in members}
            self.assertIn("node1", member_ids)
            self.assertIn("node2", member_ids)
            self.assertIn("node3", member_ids)

    def test_alive_members(self):
        """Test filtering of alive members."""
        self.node1.start()
        self.node2.start()

        # Wait for discovery
        time.sleep(2)

        # All members should be alive initially
        alive = self.node1.get_alive_members()
        self.assertEqual(len(alive), 2)

        # Simulate failure (this would happen naturally in the gossip protocol)
        # For testing, we'll manually mark a node as failed
        with self.node1.lock:
            if "node2" in self.node1.members:
                self.node1.members["node2"].status = "failed"

        alive = self.node1.get_alive_members()
        self.assertEqual(len(alive), 1)
        self.assertEqual(alive[0].node_id, "node1")

    def test_add_remove_nodes(self):
        """Test adding and removing nodes."""
        # Add a new node
        new_node = self.node1.add_node("127.0.0.1", 8004)
        self.assertEqual(new_node.node_id, self.node1._generate_node_id("127.0.0.1", 8004))

        # Verify node was added
        members = self.node1.get_members()
        self.assertEqual(len(members), 2)

        # Remove the node
        result = self.node1.remove_node(new_node.node_id)
        self.assertTrue(result)

        # Verify node was removed
        members = self.node1.get_members()
        self.assertEqual(len(members), 1)

        # Try to remove non-existent node
        result = self.node1.remove_node("nonexistent")
        self.assertFalse(result)

    def test_node_serialization(self):
        """Test node serialization and deserialization."""
        node = Node("test", "127.0.0.1", 8001, "alive", time.time(), 1)
        node_dict = node.to_dict()

        # Verify all fields are present
        self.assertIn("node_id", node_dict)
        self.assertIn("address", node_dict)
        self.assertIn("port", node_dict)
        self.assertIn("status", node_dict)
        self.assertIn("last_seen", node_dict)
        self.assertIn("incarnation", node_dict)

        # Test deserialization
        new_node = Node.from_dict(node_dict)
        self.assertEqual(new_node.node_id, node.node_id)
        self.assertEqual(new_node.address, node.address)
        self.assertEqual(new_node.port, node.port)
        self.assertEqual(new_node.status, node.status)
        self.assertEqual(new_node.incarnation, node.incarnation)

if __name__ == "__main__":
    unittest.main()
