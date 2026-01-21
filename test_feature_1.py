"""
Unit tests for Feature 1
"""

import unittest
from feature_1 import feature_1_function, process_data

class TestFeature1(unittest.TestCase):
    """Test cases for Feature 1 implementation"""

    def test_feature_1_function_valid_input(self):
        """Test feature_1_function with valid input"""
        result = feature_1_function("test data")
        self.assertEqual(result, "Processed: test data")

    def test_feature_1_function_empty_input(self):
        """Test feature_1_function with empty input"""
        with self.assertRaises(ValueError):
            feature_1_function("")

    def test_process_data(self):
        """Test the process_data helper function"""
        result = process_data("sample")
        self.assertEqual(result, "Processed: sample")

if __name__ == "__main__":
    unittest.main()
