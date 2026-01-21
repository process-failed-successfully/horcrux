"""
Feature 1 Implementation

This module implements the first feature as described in feature_list.json.
"""

def feature_1_function(input_data):
    """
    Implements the core functionality for feature 1.

    Args:
        input_data: The input data for processing

    Returns:
        The processed result
    """
    # Implement the feature logic here
    if not input_data:
        raise ValueError("Input data cannot be empty")

    # Process the data
    result = process_data(input_data)

    return result

def process_data(data):
    """
    Helper function to process the input data.

    Args:
        data: The data to process

    Returns:
        The processed data
    """
    # Simple processing example
    return f"Processed: {data}"
