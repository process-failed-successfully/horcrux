"""
Unit tests for the NodeDiscovery module.
"""

import unittest
from internal.swim.node_discovery import NodeDiscovery

class TestNodeDiscovery(unittest.TestCase):
    """
    Test cases for the NodeDiscovery class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.discovery = NodeDiscovery()

    def test_discover_nodes(self):
        """
        Test the discover_nodes method.
        """
        input_data = {'name': 'test', 'value': 123}
        expected_output = {'name': 'test', 'value': 123, 'discovered': True}
        self.assertEqual(self.discovery.discover_nodes(input_data), expected_output)

    def test_batch_discover(self):
        """
        Test the batch_discover method.
        """
        input_data_list = [
            {'name': 'test1', 'value': 1},
            {'name': 'test2', 'value': 2}
        ]
        expected_output_list = [
            {'name': 'test1', 'value': 1, 'discovered': True},
            {'name': 'test2', 'value': 2, 'discovered': True}
        ]
        self.assertEqual(self.discovery.batch_discover(input_data_list), expected_output_list)

if __name__ == '__main__':
    unittest.main()
