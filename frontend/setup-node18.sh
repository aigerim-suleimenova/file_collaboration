#!/bin/bash

# Setup script for Node.js 18 environment
echo "🚀 Setting up Node.js 18 environment for collaboration server..."

# Source nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Use Node.js 18
echo "📦 Switching to Node.js 18..."
nvm use 18

# Verify version
echo "✅ Current Node.js version:"
node --version
npm --version

# Install dependencies if needed
echo "📥 Installing dependencies..."
npm install

# Start collaboration server
echo "🌐 Starting collaboration server..."
echo "   Server will run on: ws://127.0.0.1:1234"
echo "   Press Ctrl+C to stop the server"
echo ""
npm run collab:server
