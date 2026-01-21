#!/bin/bash

# Initialize the local-storage development environment

# Create required directories
mkdir -p data/logs
mkdir -p config

# Install Go (if not present)
if ! command -v go &> /dev/null; then
    echo "Installing Go..."
    sudo apt-get update
    sudo apt-get install -y golang-go
fi

# Print setup information
echo "Setup complete!"
echo "Log directory: ./data/logs"
echo "Config directory: ./config"
echo "To run tests: make test"
