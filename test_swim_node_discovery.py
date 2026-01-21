"""
Unit tests for the NodeDiscovery module.
"""

import unittest
from internal.swim.node_discovery import SWIMNodeDiscovery, Node

class TestNodeDiscovery(unittest.TestCase):
    """
    Test cases for the SWIMNodeDiscovery class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.discovery = SWIMNodeDiscovery("test-node", "127.0.0.1", 8000)

    def test_initialization(self):
        """
        Test that SWIMNodeDiscovery initializes correctly.
        """
        self.assertEqual(self.discovery.node_id, "test-node")
        self.assertEqual(self.discovery.address, "127.0.0.1")
        self.assertEqual(self.discovery.port, 8000)
        self.assertEqual(len(self.discovery.get_membership_list()), 1)  # Should have itself

    def test_add_node(self):
        """
        Test adding a node to the membership list.
        """
        new_node = Node("node2", "127.0.0.1", 8001)
        self.discovery.add_node(new_node)
        self.assertEqual(len(self.discovery.get_membership_list()), 2)

    def test_get_alive_nodes(self):
        """
        Test getting alive nodes.
        """
        alive_nodes = self.discovery.get_alive_nodes()
        self.assertEqual(len(alive_nodes), 1)
        self.assertEqual(alive_nodes[0].node_id, "test-node")

    def test_join_cluster(self):
        """
        Test joining a cluster.
        """
        result = self.discovery.join_cluster("127.0.0.1", 8001)
        self.assertTrue(result)
        self.assertEqual(len(self.discovery.get_membership_list()), 2)

if __name__ == '__main__':
    unittest.main()
