#!/usr/bin/env python3
"""
Unit tests for the feature implementation.
"""

import unittest
import json
from feature_implementation import FeatureImplementation

class TestFeatureImplementation(unittest.TestCase):
    """
    Test cases for the FeatureImplementation class.
    """

    def test_initialization(self):
        """
        Test that the class initializes correctly.
        """
        impl = FeatureImplementation()
        self.assertIsInstance(impl, FeatureImplementation)
        self.assertEqual(impl.config, {})

    def test_initialization_with_config(self):
        """
        Test initialization with configuration.
        """
        config = {"feature_id": "test123", "param": "value"}
        impl = FeatureImplementation(config)
        self.assertEqual(impl.config, config)

    def test_execute(self):
        """
        Test the execute method.
        """
        impl = FeatureImplementation()
        result = impl.execute()

        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("feature_id", result)

    def test_execute_with_config(self):
        """
        Test execute with configuration.
        """
        config = {"feature_id": "test456"}
        impl = FeatureImplementation(config)
        result = impl.execute()

        self.assertEqual(result["feature_id"], "test456")

if __name__ == "__main__":
    unittest.main()
