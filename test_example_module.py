"""
Unit tests for example_module.py.
"""

import pytest
from example_module import example_function

def test_example_function_valid_input():
    """Test example_function with valid inputs."""
    assert example_function("hello", 3) is True
    assert example_function("hi", 5) is False

def test_example_function_invalid_input():
    """Test example_function with invalid inputs."""
    with pytest.raises(ValueError):
        example_function(123, 3)
    with pytest.raises(ValueError):
        example_function("hello", "world")
