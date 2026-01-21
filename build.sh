#!/bin/bash

# Build the local-storage binary
echo "Building local-storage..."
go build -o local-storage main.go
echo "Build complete!"
