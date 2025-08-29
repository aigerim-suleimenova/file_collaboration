# Node.js 18 Setup for Collaboration Server

## 🚨 **Problem**
The y-websocket collaboration server requires Node.js 16+ for WebCrypto API support. Your system has Node.js 18 installed, but the terminal session isn't using it properly.

## 🔧 **Solutions**

### **Option 1: Use the Setup Script (Recommended)**
```bash
# Make sure you're in the frontend directory
cd frontend

# Run the setup script
./setup-node18.sh
```

### **Option 2: Manual nvm Setup**
```bash
# Source nvm in current terminal
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Use Node.js 18
nvm use 18

# Verify version
node --version  # Should show v18.20.8

# Start collaboration server
npm run collab:server
```

### **Option 3: Use .nvmrc (Automatic)**
```bash
# The .nvmrc file is already created
# Just run this command to automatically use Node 18
nvm use

# Then start the server
npm run collab:server
```

### **Option 4: Direct Node 18 Execution**
```bash
# Use the direct script that bypasses nvm
npm run collab:server:direct
```

## 🧪 **Testing the Setup**

### **1. Verify Node Version**
```bash
node --version
# Should show: v18.20.8
```

### **2. Check WebCrypto Support**
```bash
node -e "console.log('WebCrypto available:', !!require('crypto').webcrypto)"
# Should show: WebCrypto available: true
```

### **3. Start Collaboration Server**
```bash
npm run collab:server
# Should show: "running at 'localhost' on port 1234"
```

## 🔍 **Troubleshooting**

### **Issue: "nvm: command not found"**
```bash
# Add this to your ~/.zshrc or ~/.bash_profile
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Then restart terminal or run:
source ~/.zshrc
```

### **Issue: Still using old Node version**
```bash
# Check which node is being used
which node

# Should show: ~/.nvm/versions/node/v18.20.8/bin/node
# NOT: /usr/bin/node or /opt/homebrew/bin/node
```

### **Issue: WebCrypto still undefined**
```bash
# Make sure you're using Node 18+
node --version

# If still having issues, try reinstalling dependencies
rm -rf node_modules package-lock.json
npm install
```

## 🎯 **Quick Start Commands**

### **For New Terminal Sessions:**
```bash
cd frontend
nvm use 18
npm run collab:server
```

### **For Existing Sessions:**
```bash
cd frontend
./setup-node18.sh
```

### **For Development:**
```bash
# Terminal 1: Start collaboration server
cd frontend
nvm use 18
npm run collab:server

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## 🌟 **Why This Happens**

1. **System Node.js**: Your system has an older Node.js version
2. **nvm isolation**: nvm installs Node.js in user directory
3. **Terminal sessions**: New terminals don't automatically source nvm
4. **WebCrypto requirement**: y-websocket needs Node.js 16+ for crypto APIs

## ✅ **Success Indicators**

- ✅ `node --version` shows `v18.20.8`
- ✅ `npm run collab:server` starts without errors
- ✅ Server shows "running at 'localhost' on port 1234"
- ✅ No WebCrypto errors in console

---

**After setup, your collaboration server should work perfectly! 🎉**
