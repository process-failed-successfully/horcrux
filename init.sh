#!/bin/bash
set -e

# Update package lists
apt-get update

# Install common development tools
apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    make

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "Environment initialized successfully"
