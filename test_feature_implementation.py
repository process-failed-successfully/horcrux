#!/usr/bin/env python3
"""
Unit tests for feature_implementation.py
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open
from feature_implementation import FeatureManager

class TestFeatureManager(unittest.TestCase):
    """
    Test cases for the FeatureManager class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        # Create a temporary feature list file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(json.dumps({
            "features": [
                {
                    "id": "test_feature_1",
                    "description": "Test feature 1",
                    "status": "pending",
                    "passes": False
                },
                {
                    "id": "test_feature_2",
                    "description": "Test feature 2",
                    "status": "done",
                    "passes": True
                }
            ]
        }).encode())
        self.temp_file.close()

        self.manager = FeatureManager(self.temp_file.name)

    def tearDown(self):
        """
        Clean up test fixtures.
        """
        os.unlink(self.temp_file.name)

    def test_load_features(self):
        """
        Test that features are loaded correctly.
        """
        features = self.manager.features
        self.assertEqual(len(features["features"]), 2)
        self.assertEqual(features["features"][0]["id"], "test_feature_1")
        self.assertEqual(features["features"][1]["id"], "test_feature_2")

    def test_get_failing_features(self):
        """
        Test that failing features are identified correctly.
        """
        failing = self.manager.get_failing_features()
        self.assertEqual(len(failing), 1)
        self.assertEqual(failing[0]["id"], "test_feature_1")

    def test_implement_feature(self):
        """
        Test feature implementation.
        """
        # Implement the failing feature
        result = self.manager.implement_feature("test_feature_1")
        self.assertTrue(result)

        # Verify the feature was marked as done
        feature = next(
            (f for f in self.manager.features["features"]
             if f["id"] == "test_feature_1"),
            None
        )
        self.assertIsNotNone(feature)
        self.assertEqual(feature["status"], "done")
        self.assertTrue(feature["passes"])

    def test_verify_feature(self):
        """
        Test feature verification.
        """
        # Verify a passing feature
        result = self.manager.verify_feature("test_feature_2")
        self.assertTrue(result)

        # Verify a failing feature
        result = self.manager.verify_feature("test_feature_1")
        self.assertFalse(result)

    def test_nonexistent_feature(self):
        """
        Test handling of nonexistent features.
        """
        result = self.manager.implement_feature("nonexistent")
        self.assertFalse(result)

        result = self.manager.verify_feature("nonexistent")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
