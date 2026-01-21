.PHONY: run test lint format clean

run:
	@echo "Starting horcrux-node service..."
	@go run main.go

test:
	@echo "Running tests..."
	@go test -v ./...

lint:
	@echo "Running linter..."
	@go vet ./...

format:
	@echo "Formatting code..."
	@gofmt -w .

clean:
	@echo "Cleaning up..."
	@rm -rf bin/ *.exe

build:
	@echo "Building horcrux-node..."
	@go build -o bin/horcrux-node main.go
