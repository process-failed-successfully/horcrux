"""
Integration tests for SWIM Node Discovery.
"""

import unittest
import time
from internal.swim.node_discovery import NodeDiscovery

class TestSWIMDiscovery(unittest.TestCase):
    """Integration tests for SWIM Node Discovery."""

    def test_cluster_formation(self):
        """Test that a cluster can form with multiple nodes."""
        # Create 3 nodes
        node1 = NodeDiscovery("node1", "127.0.0.1", 8001)
        node2 = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])
        node3 = NodeDiscovery("node3", "127.0.0.1", 8003, [("127.0.0.1", 8001)])

        # Start all nodes
        node1.start()
        node2.start()
        node3.start()

        # Wait for gossip to propagate
        time.sleep(3)

        # Verify all nodes have discovered each other
        for node in [node1, node2, node3]:
            members = node.get_members()
            member_ids = {m.node_id for m in members}

            self.assertIn("node1", member_ids, f"Node1 not found in {node.node_id}'s membership")
            self.assertIn("node2", member_ids, f"Node2 not found in {node.node_id}'s membership")
            self.assertIn("node3", member_ids, f"Node3 not found in {node.node_id}'s membership")

            # All members should be alive
            alive = node.get_alive_members()
            self.assertEqual(len(alive), 3, f"Expected 3 alive members in {node.node_id}")

        # Clean up
        node1.stop()
        node2.stop()
        node3.stop()

    def test_new_node_join(self):
        """Test that new nodes can join the cluster."""
        # Create initial cluster
        node1 = NodeDiscovery("node1", "127.0.0.1", 8001)
        node2 = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])

        node1.start()
        node2.start()

        # Wait for initial discovery
        time.sleep(2)

        # Create and add a new node
        node3 = NodeDiscovery("node3", "127.0.0.1", 8003, [("127.0.0.1", 8001)])
        node3.start()

        # Wait for new node to be discovered
        time.sleep(2)

        # Verify all nodes know about the new node
        for node in [node1, node2, node3]:
            members = node.get_members()
            member_ids = {m.node_id for m in members}
            self.assertIn("node3", member_ids, f"Node3 not found in {node.node_id}'s membership")

        # Clean up
        node1.stop()
        node2.stop()
        node3.stop()

    def test_membership_consistency(self):
        """Test that membership lists are consistent across nodes."""
        # Create 3 nodes
        node1 = NodeDiscovery("node1", "127.0.0.1", 8001)
        node2 = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])
        node3 = NodeDiscovery("node3", "127.0.0.1", 8003, [("127.0.0.1", 8001)])

        # Start all nodes
        node1.start()
        node2.start()
        node3.start()

        # Wait for gossip to propagate
        time.sleep(3)

        # Get membership lists from all nodes
        members1 = {m.node_id for m in node1.get_members()}
        members2 = {m.node_id for m in node2.get_members()}
        members3 = {m.node_id for m in node3.get_members()}

        # All membership lists should be identical
        self.assertEqual(members1, members2)
        self.assertEqual(members2, members3)
        self.assertEqual(members1, members3)

        # Clean up
        node1.stop()
        node2.stop()
        node3.stop()

if __name__ == "__main__":
    unittest.main()
