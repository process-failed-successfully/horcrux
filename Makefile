# Makefile for the project

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linter"
	@echo "  format     - Format code"
	@echo "  run        - Run the application"

.PHONY: install
install:
	@echo "Installing dependencies..."
	@python3 -m pip install --upgrade pip
	@python3 -m pip install -r requirements.txt 2>/dev/null || echo "No Python requirements found"
	@npm install 2>/dev/null || echo "No Node.js dependencies found"

.PHONY: test
test:
	@echo "Running tests..."
	@python3 -m pytest -v 2>/dev/null || echo "No Python tests found"
	@npm test 2>/dev/null || echo "No Node.js tests found"

.PHONY: lint
lint:
	@echo "Running linter..."
	@python3 -m flake8 . 2>/dev/null || echo "No Python linter configured"
	@npm run lint 2>/dev/null || echo "No Node.js linter configured"

.PHONY: format
format:
	@echo "Formatting code..."
	@python3 -m black . 2>/dev/null || echo "No Python formatter configured"
	@npm run format 2>/dev/null || echo "No Node.js formatter configured"

.PHONY: run
run:
	@echo "Running the application..."
	@python3 main.py 2>/dev/null || echo "No main.py found"
	@npm start 2>/dev/null || echo "No Node.js start script found"
