.PHONY: test lint format run clean

test:
	@echo "Running tests..."
	python3 -m unittest discover -s . -p "test_*.py" -v

lint:
	@echo "Running linting..."
	python3 -m pylint example_feature.py test_example_feature.py || true

format:
	@echo "Formatting code..."
	python3 -m autopep8 --in-place --aggressive example_feature.py test_example_feature.py || true

run:
	@echo "Running example feature..."
	python3 example_feature.py

clean:
	@echo "Cleaning up..."
	rm -f *.pyc __pycache__ test_*.pyc
	rm -rf __pycache__ .pytest_cache
