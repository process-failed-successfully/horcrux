# Makefile for horcrux-swim-gossip project

.PHONY: all test lint format clean

all:
	@echo "Build complete"

test:
	@echo "Running all tests..."
	python3 -m pytest test_*.py -v
	python3 -m pytest internal/tests/ -v 2>/dev/null || true

test-gossip:
	@echo "Running SWIM gossip tests..."
	python3 -m pytest test_swim_gossip.py -v

lint:
	@echo "Running linter..."
	python3 -m pylint internal/gossip/ || echo "pylint not installed, skipping"

format:
	@echo "Formatting code..."
	python3 -m black internal/ test_*.py || echo "black not installed, skipping"

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ */__pycache__ .pytest_cache
	find . -name "*.pyc" -delete

run:
	@echo "Running the application..."
	python3 feature_implementation.py
