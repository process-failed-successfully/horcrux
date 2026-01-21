#!/bin/bash

# Initialize the environment
echo "Initializing environment..."

# Update package lists
apt-get update

# Install common tools
apt-get install -y --no-cache \
    python3 \
    python3-pip \
    nodejs \
    npm \
    git \
    curl \
    make \
    jq

# Install Python development tools
python3 -m pip install --upgrade pip
python3 -m pip install pytest flake8 black

# Install Node.js development tools (if needed)
npm install -g eslint prettier

echo "Environment initialized successfully."
