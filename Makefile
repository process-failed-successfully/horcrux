.PHONY: test, lint, format, run, clean, install, requirements, test-go, test-python

test:
	@echo "Running all tests..."
	$(MAKE) test-python
	$(MAKE) test-go

test-python:
	@echo "Running Python tests..."
	python3 -m pytest tests/ -v

test-go:
	@echo "Running Go tests..."
	cd internal/swim && go test -v

lint:
	@echo "Running linting..."
	python3 -m pylint internal/ tests/ || true
	python3 -m flake8 internal/ tests/ || true

format:
	@echo "Formatting code..."
	python3 -m black internal/ tests/ || true
	python3 -m isort internal/ tests/ || true

run:
	@echo "Running application..."
	python3 main.py

clean:
	@echo "Cleaning up..."
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt

requirements:
	@echo "Generating requirements..."
	pip3 freeze > requirements.txt
