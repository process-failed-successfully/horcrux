.PHONY: build
build:
	./build.sh

.PHONY: test
test:
	@echo "Running tests..."
	@go test -v ./...

.PHONY: clean
clean:
	rm -f local-storage
	rm -rf data/logs/*

.PHONY: run
run:
	@echo "Usage: ./local-storage <command> [args]"
	@echo "Commands:"
	@echo "  append <data>  - Append a log entry"
	@echo "  read           - Read all log entries"
