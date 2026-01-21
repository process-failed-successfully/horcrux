#!/usr/bin/make -f

.PHONY: all test lint format run

all: test

test:
	@echo "Running tests..."
	python3 -m unittest test_feature_implementation.py -v

lint:
	@echo "Running linting..."
	python3 -m flake8 feature_implementation.py test_feature_implementation.py --max-line-length=120

format:
	@echo "Running formatting..."
	python3 -m black feature_implementation.py test_feature_implementation.py

run:
	@echo "Running feature implementation..."
	python3 feature_implementation.py

clean:
	@echo "Cleaning up..."
	rm -f *.pyc __pycache__ test_*.pyc
