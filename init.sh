#!/bin/bash

# Initialize Go module
echo "Initializing Go module..."
go mod init github.com/process-failed-successfully/horcrux

# Create basic project structure
echo "Creating project structure..."
mkdir -p internal
touch main.go

# Initialize main.go with a basic main function
cat << 'GOMAIN' > main.go
package main

import "fmt"

func main() {
    fmt.Println("Horcrux initialized successfully")
}
GOMAIN

# Print setup information
echo "Project setup complete."
echo "To build and run the project:"
echo "1. Run 'go build' to compile the project"
echo "2. Run './horcrux' to execute the binary"
