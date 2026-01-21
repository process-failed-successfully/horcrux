#!/bin/bash

# Initialize the development environment for horcrux-swim-gossip

echo "Setting up the development environment for horcrux-swim-gossip..."

# Install dependencies
echo "Installing dependencies..."
if [ -f "go.mod" ]; then
    echo "Found go.mod. Installing Go dependencies..."
    go mod download
    go mod tidy
else
    echo "No go.mod found. Please ensure you are in the correct directory."
    exit 1
fi

# Print helpful information
echo ""
echo "Development environment setup complete."
echo "To run the project:"
echo "  1. Ensure you have Go installed (version 1.16 or higher)."
echo "  2. Run 'go build' to build the project."
echo "  3. Run the binary to start the application."
echo ""
echo "To run tests:"
echo "  go test ./internal/gossip/..."
echo ""
echo "For more information, refer to the README.md file."
