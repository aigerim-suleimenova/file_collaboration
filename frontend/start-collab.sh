#!/bin/bash

# Start collaboration server with Node.js 18
echo "🚀 Starting collaboration server with Node.js 18..."

# Source nvm in this script
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Use Node.js 18
echo "📦 Using Node.js 18..."
nvm use 18

# Verify version
echo "✅ Node.js version: $(node --version)"
echo "✅ NPM version: $(npm --version)"

# Start the collaboration server
echo "🌐 Starting collaboration server on ws://127.0.0.1:1234"
echo "   Press Ctrl+C to stop the server"
echo ""

# Use the direct node command with the nvm Node.js 18
$NVM_DIR/versions/node/v18.20.8/bin/node ./node_modules/y-websocket/bin/server.js --port 1234 --host 127.0.0.1
