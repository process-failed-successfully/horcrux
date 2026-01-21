"""
Comprehensive unit tests for SWIM Node Discovery module.
"""

import unittest
import time
import threading
from internal.swim.node_discovery import SWIMNodeDiscovery, Node

class TestSWIMNodeDiscovery(unittest.TestCase):
    """Test cases for SWIMNodeDiscovery class."""

    def setUp(self):
        """Set up test fixtures."""
        self.node_id = "test_node_1"
        self.address = "127.0.0.1"
        self.port = 9001
        self.discovery = SWIMNodeDiscovery(self.node_id, self.address, self.port)

    def test_initialization(self):
        """Test that SWIMNodeDiscovery initializes correctly."""
        self.assertEqual(self.discovery.node_id, self.node_id)
        self.assertEqual(self.discovery.address, self.address)
        self.assertEqual(self.discovery.port, self.port)
        self.assertEqual(len(self.discovery.get_membership_list()), 1)  # Should have local node
        self.assertEqual(self.discovery.get_node_count(), 1)

    def test_add_node(self):
        """Test adding a node to the membership list."""
        new_node = Node(
            node_id="node2",
            address="127.0.0.1",
            port=9002,
            status="alive"
        )

        self.discovery.add_node(new_node)
        self.assertEqual(self.discovery.get_node_count(), 2)

        nodes = self.discovery.get_membership_list()
        node_ids = [node.node_id for node in nodes]
        self.assertIn("node2", node_ids)

    def test_remove_node(self):
        """Test removing a node from the membership list."""
        # Add a node first
        new_node = Node("node2", "127.0.0.1", 9002)
        self.discovery.add_node(new_node)
        self.assertEqual(self.discovery.get_node_count(), 2)

        # Remove the node
        self.discovery.remove_node("node2")
        self.assertEqual(self.discovery.get_node_count(), 1)

        nodes = self.discovery.get_membership_list()
        node_ids = [node.node_id for node in nodes]
        self.assertNotIn("node2", node_ids)

    def test_get_alive_nodes(self):
        """Test getting only alive nodes."""
        # Add alive node
        alive_node = Node("node2", "127.0.0.1", 9002, status="alive")
        self.discovery.add_node(alive_node)

        # Add failed node
        failed_node = Node("node3", "127.0.0.1", 9003, status="failed")
        self.discovery.add_node(failed_node)

        alive_nodes = self.discovery.get_alive_nodes()
        self.assertEqual(len(alive_nodes), 2)  # Local node + node2
        self.assertEqual(alive_nodes[0].status, "alive")
        self.assertEqual(alive_nodes[1].status, "alive")

    def test_join_cluster(self):
        """Test joining a cluster via seed node."""
        # This is a simulated test since we don't have actual network
        result = self.discovery.join_cluster("127.0.0.1", 9002)
        self.assertTrue(result)
        self.assertEqual(self.discovery.get_node_count(), 2)

    def test_generate_node_id(self):
        """Test node ID generation."""
        node_id1 = self.discovery._generate_node_id("127.0.0.1", 9001)
        node_id2 = self.discovery._generate_node_id("127.0.0.1", 9001)
        node_id3 = self.discovery._generate_node_id("127.0.0.1", 9002)

        # Same address:port should generate same ID
        self.assertEqual(node_id1, node_id2)
        # Different port should generate different ID
        self.assertNotEqual(node_id1, node_id3)

    def test_process_gossip(self):
        """Test processing gossip from another node."""
        # Create remote membership
        remote_node = Node("remote_node", "127.0.0.1", 9002)
        remote_membership = {
            "remote_node": remote_node,
            self.node_id: self.discovery.local_node
        }

        # Process gossip
        self.discovery._process_gossip("remote_node", remote_membership)

        # Check that remote node was added
        self.assertEqual(self.discovery.get_node_count(), 2)
        nodes = self.discovery.get_membership_list()
        node_ids = [node.node_id for node in nodes]
        self.assertIn("remote_node", node_ids)

    def test_start_stop(self):
        """Test starting and stopping the discovery service."""
        # Start the service
        self.discovery.start()
        self.assertTrue(self.discovery.running)
        self.assertIsNotNone(self.discovery.gossip_thread)

        # Stop the service
        self.discovery.stop()
        self.assertFalse(self.discovery.running)

        # Thread should be joined
        if self.discovery.gossip_thread:
            self.discovery.gossip_thread.join(timeout=1)
            self.assertFalse(self.discovery.gossip_thread.is_alive())

    def test_is_healthy(self):
        """Test cluster health check."""
        # With only local node, should be healthy
        self.assertTrue(self.discovery.is_healthy())

        # Add another alive node
        self.discovery.add_node(Node("node2", "127.0.0.1", 9002))
        self.assertTrue(self.discovery.is_healthy())

        # Remove all nodes except local (should still be healthy)
        self.discovery.remove_node("node2")
        self.assertTrue(self.discovery.is_healthy())

    def test_node_serialization(self):
        """Test node serialization and deserialization."""
        original_node = Node(
            node_id="test_node",
            address="127.0.0.1",
            port=9001,
            status="alive",
            incarnation=5
        )

        # Serialize to dict
        node_dict = original_node.to_dict()
        self.assertEqual(node_dict['node_id'], "test_node")
        self.assertEqual(node_dict['port'], 9001)
        self.assertEqual(node_dict['incarnation'], 5)

        # Deserialize from dict
        restored_node = Node.from_dict(node_dict)
        self.assertEqual(restored_node.node_id, original_node.node_id)
        self.assertEqual(restored_node.port, original_node.port)
        self.assertEqual(restored_node.incarnation, original_node.incarnation)

if __name__ == '__main__':
    unittest.main()
