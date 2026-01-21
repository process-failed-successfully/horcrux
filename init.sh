#!/bin/bash

# Initialize the development environment for horcrux-node

# Install dependencies
echo "Installing dependencies..."
apt-get update
apt-get install -y git make

# Check if Go is installed, if not install it
if ! command -v go &> /dev/null; then
    echo "Go is not installed. Installing Go..."
    apt-get install -y golang
fi

# Check if Node.js is installed, if not install it
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Installing Node.js..."
    apt-get install -y nodejs npm
fi

# Install Go dependencies
echo "Installing Go dependencies..."
go mod tidy

# Print helpful information
echo "Development environment setup complete."
echo "To start the horcrux-node service, run:"
echo "  make run"
echo ""
echo "To run tests, run:"
echo "  make test"
