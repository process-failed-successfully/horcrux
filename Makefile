.PHONY: all test integration clean

all: test

test:
	go test ./... -v

test-storage:
	go test ./internal/storage -v

test-retrieval:
	go test ./internal/retrieval -v

integration:
	go run integration.go

clean:
	rm -f integration.go
