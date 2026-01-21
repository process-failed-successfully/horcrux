"""
Unit tests for the DataValidator module.
"""

import unittest
from data_validator import DataValidator

class TestDataValidator(unittest.TestCase):
    """
    Test cases for DataValidator class methods.
    """

    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        self.assertTrue(DataValidator.validate_email("test@example.com"))
        self.assertTrue(DataValidator.validate_email("user.name+tag@sub.domain.co.uk"))
        self.assertTrue(DataValidator.validate_email("user@localhost"))

        # Invalid emails
        self.assertFalse(DataValidator.validate_email(""))
        self.assertFalse(DataValidator.validate_email("invalid"))
        self.assertFalse(DataValidator.validate_email("user@.com"))
        self.assertFalse(DataValidator.validate_email("@example.com"))
        self.assertFalse(DataValidator.validate_email("user@.com."))

    def test_validate_phone(self):
        """Test phone number validation."""
        # Valid phone numbers
        self.assertTrue(DataValidator.validate_phone("+1234567890"))
        self.assertTrue(DataValidator.validate_phone("1234567890"))
        self.assertTrue(DataValidator.validate_phone("+442012345678"))

        # Invalid phone numbers
        self.assertFalse(DataValidator.validate_phone(""))
        self.assertFalse(DataValidator.validate_phone("0123456789"))  # Should start with country code
        self.assertFalse(DataValidator.validate_phone("+0123456789"))  # Country code can't start with 0
        self.assertFalse(DataValidator.validate_phone("abc1234567"))

    def test_validate_date(self):
        """Test date validation."""
        # Valid dates
        self.assertTrue(DataValidator.validate_date("2023-01-01"))
        self.assertTrue(DataValidator.validate_date("2023-12-31"))
        self.assertTrue(DataValidator.validate_date("2000-02-29"))  # Leap year

        # Invalid dates
        self.assertFalse(DataValidator.validate_date(""))
        self.assertFalse(DataValidator.validate_date("2023-01-01T12:00:00"))  # Wrong format
        self.assertFalse(DataValidator.validate_date("2023-13-01"))  # Invalid month
        self.assertFalse(DataValidator.validate_date("2023-01-32"))  # Invalid day
        self.assertFalse(DataValidator.validate_date("2001-02-29"))  # Not a leap year

        # Custom format
        self.assertTrue(DataValidator.validate_date("01/01/2023", "%d/%m/%Y"))
        self.assertFalse(DataValidator.validate_date("01/01/2023", "%Y-%m-%d"))

    def test_validate_required_fields(self):
        """Test required fields validation."""
        data = {
            "name": "John",
            "email": "john@example.com",
            "age": 30
        }

        # Valid cases
        self.assertTrue(DataValidator.validate_required_fields(data, ["name", "email"]))
        self.assertTrue(DataValidator.validate_required_fields(data, ["name"]))
        self.assertTrue(DataValidator.validate_required_fields(data, []))

        # Invalid cases
        self.assertFalse(DataValidator.validate_required_fields(data, ["name", "phone"]))
        self.assertFalse(DataValidator.validate_required_fields(data, ["address"]))
        self.assertFalse(DataValidator.validate_required_fields({}, ["name"]))
        self.assertFalse(DataValidator.validate_required_fields(None, ["name"]))

        # Edge cases
        self.assertFalse(DataValidator.validate_required_fields({"name": ""}, ["name"]))
        self.assertFalse(DataValidator.validate_required_fields({"name": None}, ["name"]))

    def test_validate_string_length(self):
        """Test string length validation."""
        # Valid cases
        self.assertTrue(DataValidator.validate_string_length("hello", 0, 10))
        self.assertTrue(DataValidator.validate_string_length("hello", 5, 5))
        self.assertTrue(DataValidator.validate_string_length("", 0, 10))
        self.assertTrue(DataValidator.validate_string_length("a" * 100, 0, 1000))

        # Invalid cases
        self.assertFalse(DataValidator.validate_string_length("hello", 10, 20))
        self.assertFalse(DataValidator.validate_string_length("hello", 0, 4))
        self.assertFalse(DataValidator.validate_string_length(123, 0, 10))  # Not a string
        self.assertFalse(DataValidator.validate_string_length(None, 0, 10))

    def test_validate_number_range(self):
        """Test number range validation."""
        # Valid cases
        self.assertTrue(DataValidator.validate_number_range(5, 0, 10))
        self.assertTrue(DataValidator.validate_number_range(0, 0, 10))
        self.assertTrue(DataValidator.validate_number_range(10, 0, 10))
        self.assertTrue(DataValidator.validate_number_range(5, None, 10))
        self.assertTrue(DataValidator.validate_number_range(5, 0, None))
        self.assertTrue(DataValidator.validate_number_range(5, None, None))
        self.assertTrue(DataValidator.validate_number_range("5", 0, 10))  # String number

        # Invalid cases
        self.assertFalse(DataValidator.validate_number_range(15, 0, 10))
        self.assertFalse(DataValidator.validate_number_range(-1, 0, 10))
        self.assertFalse(DataValidator.validate_number_range("abc", 0, 10))  # Invalid number
        self.assertFalse(DataValidator.validate_number_range(None, 0, 10))

if __name__ == "__main__":
    unittest.main()
