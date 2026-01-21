.PHONY: test
test:
	python3 -m pytest test_swim_node_discovery.py -v

.PHONY: all
all:
	python3 -m pytest -v
