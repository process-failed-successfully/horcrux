#!/bin/bash

# Initialize the development environment for horcrux-swim-gossip

echo "Setting up the development environment for horcrux-swim-gossip..."

# Install Go if not present
if ! command -v go &> /dev/null; then
    echo "Go not found. Installing Go..."
    apt-get update && apt-get install -y golang-go
fi

# Install dependencies
echo "Installing Go dependencies..."
go mod download
go mod tidy

# Print helpful information
echo ""
echo "Development environment setup complete."
echo "To run the project:"
echo "  1. Run 'go build' to build the project."
echo "  2. Run the binary to start the application."
echo ""
echo "To run tests:"
echo "  go test ./internal/gossip/..."
echo ""
echo "For more information, refer to the README.md file."
