.PHONY: all test run clean

all: test

test:
	python3 -m unittest internal.gossip.test_swim_provider

run:
	python3 internal/gossip/swim_provider.py

clean:
	rm -f *.pyc __pycache__ test-results.txt
