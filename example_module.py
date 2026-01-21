"""
Example module implementation.

This module provides functionality for [feature description].
"""

def example_function(param1: str, param2: int) -> bool:
    """
    Example function that demonstrates the feature implementation.

    Args:
        param1: A string parameter.
        param2: An integer parameter.

    Returns:
        bool: True if the operation is successful, False otherwise.
    """
    # Validate inputs
    if not isinstance(param1, str):
        raise ValueError("param1 must be a string")
    if not isinstance(param2, int):
        raise ValueError("param2 must be an integer")

    # Implement the feature logic
    result = len(param1) > param2
    return result
