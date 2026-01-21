#!/bin/bash

# HorcruxKV Setup Script

echo "Setting up HorcruxKV development environment..."

# Install Go (if not installed)
if ! command -v go &> /dev/null; then
    echo "Installing Go..."
    sudo apt-get update
    sudo apt-get install -y golang-go
fi

# Install dependencies (if any)
echo "Installing dependencies..."
go mod tidy

# Print setup information
echo ""
echo "HorcruxKV setup complete!"
echo "To run the project:"
echo "  1. Start the HorcruxKV server: go run cmd/server/main.go"
echo "  2. Use the CLI: go run cmd/cli/main.go --help"
echo ""
