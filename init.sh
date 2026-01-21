#!/bin/bash

# Initialize the development environment for the Horcrux SWIM Gossip Provider

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y git make

# Clone the Horcrux repository
echo "Cloning the Horcrux repository..."
git clone https://github.com/process-failed-successfully/horcrux.git

# Navigate to the Horcrux directory
cd horcrux

# Install Go dependencies
echo "Installing Go dependencies..."
go mod download

# Print helpful information
echo "Development environment setup complete."
echo "To start the Horcrux project, run:"
echo "  make run"
