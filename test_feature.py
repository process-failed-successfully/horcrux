"""
Tests for [Feature ID]
"""

import pytest
from feature_implementation import feature_function

def test_feature_function():
    """
    Test that the feature function works correctly
    """
    result = feature_function()
    assert result is True

if __name__ == "__main__":
    pytest.main([__file__])
