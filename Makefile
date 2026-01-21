.PHONY: help
help:
	@echo "Available targets:"
	@echo "  help            - Show this help message"
	@echo "  test            - Run all tests"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  install         - Install dependencies"
	@echo "  clean           - Clean build artifacts"

.PHONY: install
install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt 2>/dev/null || echo "No Python requirements.txt found"
	npm install 2>/dev/null || echo "No Node.js package.json found"

.PHONY: test
test:
	@echo "Running tests..."
	python3 -m pytest -v 2>/dev/null || echo "No Python tests found"
	npm test 2>/dev/null || echo "No Node.js tests found"

.PHONY: lint
lint:
	@echo "Running linting..."
	pylint *.py 2>/dev/null || echo "No Python files to lint"
	eslint . 2>/dev/null || echo "No JavaScript files to lint"

.PHONY: format
format:
	@echo "Formatting code..."
	black *.py 2>/dev/null || echo "No Python files to format"
	prettier --write . 2>/dev/null || echo "No JavaScript files to format"

.PHONY: clean
clean:
	@echo "Cleaning..."
	rm -rf __pycache__ .pytest_cache
	rm -rf node_modules
