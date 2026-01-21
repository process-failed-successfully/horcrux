"""
Unit tests for the GossipPropagation module.
"""

import unittest
from internal.swim.gossip_propagation import GossipPropagation

class TestGossipPropagation(unittest.TestCase):
    """
    Test cases for the GossipPropagation class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.propagation = GossipPropagation()

    def test_propagate_message(self):
        """
        Test the propagate_message method.
        """
        input_data = {'name': 'test', 'value': 123}
        expected_output = {'name': 'test', 'value': 123, 'propagated': True}
        self.assertEqual(self.propagation.propagate_message(input_data), expected_output)

    def test_batch_propagate(self):
        """
        Test the batch_propagate method.
        """
        input_data_list = [
            {'name': 'test1', 'value': 1},
            {'name': 'test2', 'value': 2}
        ]
        expected_output_list = [
            {'name': 'test1', 'value': 1, 'propagated': True},
            {'name': 'test2', 'value': 2, 'propagated': True}
        ]
        self.assertEqual(self.propagation.batch_propagate(input_data_list), expected_output_list)

if __name__ == '__main__':
    unittest.main()
