#!/bin/bash

# Exit on error
set -e

# Install Node.js and npm (if not installed)
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "Node.js is already installed: $(node --version)"
fi

# Initialize Node.js project if package.json doesn't exist
if [ ! -f "package.json" ]; then
    echo "Initializing Node.js project..."
    npm init -y
else
    echo "package.json already exists. Skipping npm init."
fi

# Install Express.js
if ! npm list express &> /dev/null; then
    echo "Installing Express.js..."
    npm install express
else
    echo "Express.js is already installed."
fi

# Print setup instructions
echo ""
echo "=== Setup Complete ==="
echo "To start the HTTP server:"
echo "1. Create a server.js file (see example below)."
echo "2. Run: node server.js"
echo ""
echo "Example server.js:"
cat << 'EXAMPLE'
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

app.listen(PORT, () => {
  console.log(\`Server listening on port ${PORT}\`);
});
EXAMPLE
