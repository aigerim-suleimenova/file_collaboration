#!/bin/bash

# Simple script to start collaboration server with Node.js 18
echo "🚀 Starting collaboration server..."

# Direct path to Node.js 18
NODE_PATH="/Users/aigerimsuleimenova/.nvm/versions/node/v18.20.8/bin/node"

# Check if Node.js 18 exists
if [ ! -f "$NODE_PATH" ]; then
    echo "❌ Node.js 18 not found at: $NODE_PATH"
    echo "   Please run: nvm install 18"
    exit 1
fi

# Show Node.js version
echo "📦 Using Node.js: $($NODE_PATH --version)"

# Start collaboration server
echo "🌐 Starting server on ws://127.0.0.1:1234 (IPv4 only)"
echo "   Press Ctrl+C to stop"
echo ""

# Start the server with proper options for room-based connections
# --persistence false: Don't save to disk
# --debug: Enable debug logging
# --host 127.0.0.1: Bind to IPv4 localhost
# Force IPv4 binding by setting environment variable
export NODE_OPTIONS="--dns-result-order=ipv4first"
$NODE_PATH ./node_modules/y-websocket/bin/server.js --port 1234 --host 127.0.0.1 --persistence false --debug
