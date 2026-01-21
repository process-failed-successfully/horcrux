"""
Tests for SWIM Failure Detection.
"""

import unittest
import time
from internal.swim.node_discovery import NodeDiscovery

class TestSWIMFailureDetection(unittest.TestCase):
    """Test SWIM Failure Detection functionality."""

    def test_failure_detection(self):
        """Test that node failures are detected."""
        # Create 3 nodes
        node1 = NodeDiscovery("node1", "127.0.0.1", 8001)
        node2 = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])
        node3 = NodeDiscovery("node3", "127.0.0.1", 8003, [("127.0.0.1", 8001)])

        # Start all nodes
        node1.start()
        node2.start()
        node3.start()

        # Wait for discovery
        time.sleep(2)

        # Verify all nodes are alive
        for node in [node1, node2, node3]:
            alive = node.get_alive_members()
            self.assertEqual(len(alive), 3)

        # Simulate failure by stopping node3
        node3.stop()

        # Wait for failure detection (in simulation, this happens immediately)
        time.sleep(2)

        # Check that node3 is marked as failed in other nodes
        # Note: In our simulation, failure detection is immediate when we manually stop
        # In a real implementation, this would take several ping cycles
        for node in [node1, node2]:
            members = node.get_members()
            failed_nodes = [m for m in members if not m.is_alive()]

            # We expect node3 to be marked as failed
            # (This may not work perfectly in simulation, but tests the concept)
            self.assertGreater(len(failed_nodes), 0)

        # Clean up
        node1.stop()
        node2.stop()

    def test_node_recovery(self):
        """Test that recovered nodes are detected."""
        # Create 2 nodes
        node1 = NodeDiscovery("node1", "127.0.0.1", 8001)
        node2 = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])

        # Start nodes
        node1.start()
        node2.start()

        # Wait for discovery
        time.sleep(2)

        # Simulate failure by stopping node2
        node2.stop()
        time.sleep(1)

        # Restart node2
        node2 = NodeDiscovery("node2", "127.0.0.1", 8002, [("127.0.0.1", 8001)])
        node2.start()
        time.sleep(2)

        # Check that node2 is back in membership
        members = node1.get_members()
        member_ids = {m.node_id for m in members}
        self.assertIn("node2", member_ids)

        # Clean up
        node1.stop()
        node2.stop()

if __name__ == "__main__":
    unittest.main()
