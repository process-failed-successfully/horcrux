#!/bin/bash

# Initialize the project environment
echo "Setting up the Shamir's Secret Sharing project..."

# Create necessary directories
mkdir -p internal/split internal/combine internal/edge config

# Initialize Git repository if not already initialized
if [ ! -d ".git" ]; then
    git init
    echo "Initialized Git repository."
fi

# Create README.md if it doesn't exist
if [ ! -f "README.md" ]; then
    cat << 'README' > README.md
# Shamir's Secret Sharing

This project implements Shamir's Secret Sharing algorithm for splitting and combining secrets.

## Features
- Split a secret into multiple shares.
- Combine shares to reconstruct the secret.
- Handle edge cases and invalid inputs.

## Setup
Run the following command to set up the environment:
