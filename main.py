"""
Main application entry point.
"""

from src.utils.validator import (
    validate_email,
    validate_required_fields,
    ValidationError
)

def main():
    """Demonstrate validator usage."""
    print("Data Validator Demo")

    # Test email validation
    try:
        validate_email("test@example.com")
        print("✓ Valid email")
    except ValidationError as e:
        print(f"✗ Email validation failed: {e}")

    try:
        validate_email("invalid")
        print("✓ Valid email")
    except ValidationError as e:
        print(f"✗ Email validation failed: {e}")

    # Test required fields
    data = {"name": "John", "age": 30}
    try:
        validate_required_fields(data, ["name", "age"])
        print("✓ All required fields present")
    except ValidationError as e:
        print(f"✗ Required fields validation failed: {e}")

    try:
        validate_required_fields(data, ["name", "email"])
        print("✓ All required fields present")
    except ValidationError as e:
        print(f"✗ Required fields validation failed: {e}")

if __name__ == "__main__":
    main()
