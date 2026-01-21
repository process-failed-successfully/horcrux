#!/bin/bash

# Initialize the development environment for horcrux-node gRPC server

echo "Setting up environment for horcrux-node gRPC server..."

# Install Go (if not already installed)
if ! command -v go &> /dev/null; then
    echo "Installing Go..."
    sudo apt-get update
    sudo apt-get install -y golang-go
fi

# Install protoc and protoc-gen-go
if ! command -v protoc &> /dev/null; then
    echo "Installing protoc..."
    sudo apt-get install -y protobuf-compiler
fi

if ! go list -m google.golang.org/protobuf &> /dev/null; then
    echo "Installing protoc-gen-go..."
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
fi

# Initialize Go module (if not already initialized)
if [ ! -f "go.mod" ]; then
    echo "Initializing Go module..."
    go mod init github.com/process-failed-successfully/horcrux
fi

# Create necessary directories
mkdir -p internal/grpc proto

echo "Environment setup complete!"
echo "To compile protocol buffers, run: protoc --go_out=. --go-grpc_out=. proto/*.proto"
