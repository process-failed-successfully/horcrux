.PHONY: all test run clean

all: test

test:
	python3 -m unittest test_feature_implementation.py

run:
	python3 feature_implementation.py

clean:
	rm -f *.pyc __pycache__ test-results.txt
