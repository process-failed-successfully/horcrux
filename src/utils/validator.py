"""
Data validation utilities module.

This module provides functions for validating various types of input data.
"""

from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(f"{field + ':' if field else ''} {message}")

def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: The email address to validate

    Returns:
        bool: True if valid, False otherwise

    Raises:
        ValidationError: If email is empty or invalid format
    """
    if not email:
        raise ValidationError("Email cannot be empty", "email")

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format", "email")

    return True

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that required fields are present in a dictionary.

    Args:
        data: Dictionary containing the data to validate
        required_fields: List of field names that are required

    Returns:
        bool: True if all required fields are present

    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    return True

def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """
    Validate string length constraints.

    Args:
        value: String to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length (optional)

    Returns:
        bool: True if length constraints are satisfied

    Raises:
        ValidationError: If length constraints are not met
    """
    if len(value) < min_length:
        raise ValidationError(f"String must be at least {min_length} characters long")

    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"String must be no more than {max_length} characters long")

    return True

def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate that a string matches a specific date format.

    Args:
        date_str: String containing the date
        format: Expected date format

    Returns:
        bool: True if date format is valid

    Raises:
        ValidationError: If date format is invalid
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        raise ValidationError(f"Date must be in {format} format")

def validate_number_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None,
                         max_val: Optional[Union[int, float]] = None) -> bool:
    """
    Validate that a number is within a specified range.

    Args:
        value: Number to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        bool: True if number is within range

    Raises:
        ValidationError: If number is outside the specified range
    """
    if min_val is not None and value < min_val:
        raise ValidationError(f"Value must be at least {min_val}")

    if max_val is not None and value > max_val:
        raise ValidationError(f"Value must be no more than {max_val}")

    return True
