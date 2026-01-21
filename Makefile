.PHONY: help test lint format run

help:
	@echo "Available targets:"
	@echo "  test    - Run tests"
	@echo "  lint    - Run linter"
	@echo "  format  - Format code"
	@echo "  run     - Run the application"

test:
	python3 -m unittest discover -s . -p "test_*.py"

lint:
	# Add lint command here
	@echo "Linting not configured yet"

format:
	# Add format command here
	@echo "Formatting not configured yet"

run:
	# Add run command here
	@echo "Run command not configured yet"
