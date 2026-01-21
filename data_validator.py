"""
Data Validator Module

This module provides functions to validate various types of data inputs.
"""

from typing import Any, Dict, List, Optional
import re
from datetime import datetime

class DataValidator:
    """
    A class to handle various data validation tasks.
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate an email address format.

        Args:
            email: The email address to validate

        Returns:
            bool: True if email is valid, False otherwise
        """
        if not email:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate a phone number format (basic international format).

        Args:
            phone: The phone number to validate

        Returns:
            bool: True if phone is valid, False otherwise
        """
        if not phone:
            return False

        # Basic international phone number validation
        pattern = r'^\+?[1-9]\d{1,14}$'  # E.164 format
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_date(date_str: str, date_format: str = '%Y-%m-%d') -> bool:
        """
        Validate a date string against a specified format.

        Args:
            date_str: The date string to validate
            date_format: The expected date format (default: '%Y-%m-%d')

        Returns:
            bool: True if date is valid, False otherwise
        """
        try:
            datetime.strptime(date_str, date_format)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that all required fields are present in a dictionary.

        Args:
            data: The dictionary to validate
            required_fields: List of required field names

        Returns:
            bool: True if all required fields are present, False otherwise
        """
        if not data or not required_fields:
            return False

        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return False

        return True

    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """
        Validate that a string falls within specified length constraints.

        Args:
            value: The string to validate
            min_length: Minimum allowed length (default: 0)
            max_length: Maximum allowed length (default: 1000)

        Returns:
            bool: True if string length is valid, False otherwise
        """
        if not isinstance(value, str):
            return False

        length = len(value)
        return min_length <= length <= max_length

    @staticmethod
    def validate_number_range(value: Any, min_value: float = None, max_value: float = None) -> bool:
        """
        Validate that a number falls within specified range.

        Args:
            value: The value to validate
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)

        Returns:
            bool: True if number is within range, False otherwise
        """
        try:
            num = float(value)
        except (ValueError, TypeError):
            return False

        if min_value is not None and num < min_value:
            return False

        if max_value is not None and num > max_value:
            return False

        return True
