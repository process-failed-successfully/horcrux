#!/bin/bash

# Install system dependencies
apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    make \
    nodejs \
    npm

# Install Python packages
python3 -m pip install pytest

# Install Node packages if needed
npm install -g typescript

echo "Environment initialized successfully"
