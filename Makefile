.PHONY: test, lint, format, run, clean

test:
	@echo "Running tests..."
	python3 -m pytest tests/ -v

lint:
	@echo "Running linting..."
	python3 -m pylint src/ || true
	python3 -m flake8 src/ || true

format:
	@echo "Formatting code..."
	python3 -m black src/ tests/ || true
	python3 -m isort src/ tests/ || true

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
