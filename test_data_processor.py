"""
Unit tests for the DataProcessor module.
"""

import unittest
from data_processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """
    Test cases for the DataProcessor class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.processor = DataProcessor()

    def test_process_data(self):
        """
        Test the process_data method.
        """
        input_data = {'name': 'test', 'value': 123}
        expected_output = {'name': 'test', 'value': 123, 'processed': True}
        self.assertEqual(self.processor.process_data(input_data), expected_output)

    def test_batch_process(self):
        """
        Test the batch_process method.
        """
        input_data_list = [
            {'name': 'test1', 'value': 1},
            {'name': 'test2', 'value': 2}
        ]
        expected_output_list = [
            {'name': 'test1', 'value': 1, 'processed': True},
            {'name': 'test2', 'value': 2, 'processed': True}
        ]
        self.assertEqual(self.processor.batch_process(input_data_list), expected_output_list)

if __name__ == '__main__':
    unittest.main()
