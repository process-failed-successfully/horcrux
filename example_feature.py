"""
Example Feature Implementation

This module implements a sample feature following the project guidelines.
"""

from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExampleFeature:
    """
    A class to demonstrate feature implementation following best practices.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ExampleFeature.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validate the configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(self.config, dict):
            raise ValueError("Config must be a dictionary")

        # Add more validation as needed

    def process(self, input_data: Any) -> Any:
        """
        Process the input data according to feature requirements.

        Args:
            input_data: Input data to process

        Returns:
            Processed output

        Raises:
            ValueError: If input is invalid
        """
        if input_data is None:
            raise ValueError("Input data cannot be None")

        # Example processing logic
        logger.info("Processing input data")
        result = f"Processed: {input_data}"

        return result

def main():
    """Main function for demonstration."""
    try:
        feature = ExampleFeature({"param": "value"})
        result = feature.process("sample input")
        print(result)
    except Exception as e:
        logger.error(f"Error in example feature: {e}")
        raise

if __name__ == "__main__":
    main()
