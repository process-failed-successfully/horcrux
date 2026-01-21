"""
Unit tests for the validator module.
"""

import unittest
import pytest
from src.utils.validator import (
    validate_email,
    validate_required_fields,
    validate_string_length,
    validate_date_format,
    validate_number_range,
    ValidationError
)

class TestValidator(unittest.TestCase):

    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name+tag@sub.domain.co.uk",
            "email@[123.123.123.123]"
        ]

        for email in valid_emails:
            self.assertTrue(validate_email(email))

    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            ("", "Email cannot be empty"),
            ("invalid", "Invalid email format"),
            ("user@.com", "Invalid email format"),
            ("@example.com", "Invalid email format"),
            ("user@domain", "Invalid email format")
        ]

        for email, expected_msg in invalid_emails:
            with self.assertRaises(ValidationError) as context:
                validate_email(email)
            self.assertIn(expected_msg, str(context.exception))

    def test_validate_required_fields(self):
        """Test required field validation."""
        data = {"name": "John", "age": 30, "email": "john@example.com"}

        # Should pass with all required fields
        self.assertTrue(validate_required_fields(data, ["name", "age"]))

        # Should fail with missing fields
        with self.assertRaises(ValidationError) as context:
            validate_required_fields(data, ["name", "address"])
        self.assertIn("Missing required fields: address", str(context.exception))

    def test_validate_string_length(self):
        """Test string length validation."""
        # Valid cases
        self.assertTrue(validate_string_length("hello", min_length=3, max_length=10))
        self.assertTrue(validate_string_length("a", min_length=1))
        self.assertTrue(validate_string_length("longstring", max_length=20))

        # Invalid cases
        with self.assertRaises(ValidationError):
            validate_string_length("hi", min_length=5)

        with self.assertRaises(ValidationError):
            validate_string_length("toolong", max_length=5)

    def test_validate_date_format(self):
        """Test date format validation."""
        # Valid dates
        self.assertTrue(validate_date_format("2023-01-15"))
        self.assertTrue(validate_date_format("2023-12-31", "%Y-%m-%d"))

        # Invalid dates
        with self.assertRaises(ValidationError):
            validate_date_format("15-01-2023")  # Wrong format

        with self.assertRaises(ValidationError):
            validate_date_format("2023-02-30")  # Invalid date

    def test_validate_number_range(self):
        """Test number range validation."""
        # Valid cases
        self.assertTrue(validate_number_range(5, min_val=1, max_val=10))
        self.assertTrue(validate_number_range(0, min_val=0))
        self.assertTrue(validate_number_range(100, max_val=200))

        # Invalid cases
        with self.assertRaises(ValidationError):
            validate_number_range(0, min_val=1)

        with self.assertRaises(ValidationError):
            validate_number_range(200, max_val=100)

if __name__ == "__main__":
    unittest.main()
