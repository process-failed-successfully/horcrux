"""
Unit tests for ExampleFeature
"""

import unittest
from unittest.mock import patch
from example_feature import ExampleFeature

class TestExampleFeature(unittest.TestCase):
    """Test cases for ExampleFeature class."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_config = {"param": "value"}
        self.feature = ExampleFeature(self.valid_config)

    def test_initialization(self):
        """Test that ExampleFeature initializes correctly."""
        self.assertIsInstance(self.feature, ExampleFeature)
        self.assertEqual(self.feature.config, self.valid_config)

    def test_initialization_with_default_config(self):
        """Test initialization with default config."""
        feature = ExampleFeature()
        self.assertIsInstance(feature, ExampleFeature)
        self.assertEqual(feature.config, {})

    def test_invalid_config(self):
        """Test that invalid config raises ValueError."""
        with self.assertRaises(ValueError):
            ExampleFeature("invalid config")

    def test_process_valid_input(self):
        """Test processing with valid input."""
        result = self.feature.process("test input")
        self.assertEqual(result, "Processed: test input")

    def test_process_none_input(self):
        """Test that None input raises ValueError."""
        with self.assertRaises(ValueError):
            self.feature.process(None)

    @patch('example_feature.logger')
    def test_process_logs_info(self, mock_logger):
        """Test that processing logs info message."""
        self.feature.process("test")
        mock_logger.info.assert_called_with("Processing input data")

if __name__ == "__main__":
    unittest.main()
