# Y-Quill Integration with Yjs for Real-Time Collaboration

This guide explains how to implement real-time collaborative editing using y-quill, Yjs, and Quill.js in your Vue 3 application.

## 🚀 What We've Implemented

### **Core Components**
- **y-quill**: Official binding between Quill.js and Yjs
- **QuillCursors**: Shows other users' cursor positions
- **WebSocket Provider**: Real-time communication
- **Awareness**: User presence and cursor tracking

### **Key Features**
- ✅ **Real-time synchronization** of document content
- ✅ **Cursor awareness** - see other users' cursors
- ✅ **Conflict resolution** - automatic via CRDT
- ✅ **User presence** - know who's editing
- ✅ **Automatic reconnection** - handles network issues
- ✅ **Room-based collaboration** - separate documents

## 🛠️ Dependencies

```bash
npm install y-quill quill-cursors yjs y-websocket
```

### **Package Versions**
- `y-quill`: ^1.0.0 - Official Quill-Yjs binding
- `quill-cursors`: ^4.0.4 - Cursor visualization
- `yjs`: ^13.6.27 - CRDT framework
- `y-websocket`: ^1.5.4 - WebSocket provider

## 🔧 Component Usage

### **Basic Implementation**
```vue
<template>
  <QuillEditor
    v-model="content"
    :document-id="fileId"
    :room-name="'my-project'"
    @collaboration-ready="onCollaborationReady"
  />
</template>

<script>
import QuillEditor from '@/components/QuillEditor.vue'

export default {
  components: { QuillEditor },
  data() {
    return {
      content: '',
      fileId: 'document-123'
    }
  },
  methods: {
    onCollaborationReady(collabState) {
      if (collabState) {
        console.log('Collaboration active:', collabState.connected)
      } else {
        console.log('Collaboration failed, using local mode')
      }
    }
  }
}
</script>
```

### **Advanced Implementation with User Management**
```vue
<template>
  <div>
    <div class="collaboration-status">
      <span :class="statusClass">{{ collaborationStatus }}</span>
      <span v-if="activeUsers.length > 0">
        {{ activeUsers.length }} user(s) editing
      </span>
    </div>

    <QuillEditor
      v-model="content"
      :document-id="fileId"
      :room-name="roomName"
      @collaboration-ready="onCollaborationReady"
    />

    <div class="user-list">
      <div v-for="user in activeUsers" :key="user.id" class="user-item">
        <span class="user-color" :style="{ backgroundColor: user.color }"></span>
        <span class="user-name">{{ user.name }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import QuillEditor from '@/components/QuillEditor.vue'

export default {
  components: { QuillEditor },
  props: {
    fileId: { type: String, required: true },
    roomName: { type: String, default: 'default' }
  },
  setup(props) {
    const content = ref('')
    const collabState = ref(null)
    const activeUsers = ref([])

    const collaborationStatus = computed(() => {
      if (!collabState.value) return 'Disconnected'
      return collabState.value.connected ? 'Connected' : 'Connecting...'
    })

    const statusClass = computed(() => {
      return collaborationStatus.value === 'Connected' ? 'status-connected' : 'status-disconnected'
    })

    const onCollaborationReady = (state) => {
      collabState.value = state
      if (state?.provider?.awareness) {
        setupUserTracking(state.provider.awareness)
      }
    }

    const setupUserTracking = (awareness) => {
      awareness.on('change', (changes) => {
        const states = Array.from(awareness.getStates().values())
        activeUsers.value = states
          .filter(state => state.user)
          .map(state => state.user)
      })
    }

    return {
      content,
      collaborationStatus,
      statusClass,
      activeUsers,
      onCollaborationReady
    }
  }
}
</script>
```

## 🌐 WebSocket Server Setup

### **Start Collaboration Server**
```bash
# From frontend directory
npm run collab:server

# Or manually
npx y-websocket --port 1234 --host 127.0.0.1
```

### **Environment Configuration**
Create `.env` file in frontend directory:
```env
VITE_COLLAB_WS=ws://127.0.0.1:1234
VITE_COLLAB_ROOM=filecollab
VITE_COLLAB_PASSWORD=optional-password
```

## 🔄 How It Works

### **1. Document Initialization**
```javascript
// Create Yjs document
const ydoc = new Y.Doc()

// Create shared text
const ytext = ydoc.getText('quill')

// Connect via WebSocket
const provider = new WebsocketProvider(host, room, ydoc)
```

### **2. Quill Binding**
```javascript
// Bind Quill to Yjs
const binding = new QuillBinding(ytext, quill, provider.awareness)

// Now Quill and Yjs are automatically synchronized
```

### **3. Real-time Updates**
- **Local changes**: Quill → Yjs → WebSocket → Other clients
- **Remote changes**: WebSocket → Yjs → Quill → UI update
- **Cursor positions**: Shared via awareness protocol

## 🎯 Advanced Features

### **Custom User Information**
```javascript
// Set user details
provider.awareness.setLocalStateField('user', {
  name: 'John Doe',
  color: '#ff0000',
  id: 'user-123',
  avatar: 'https://example.com/avatar.jpg'
})
```

### **Document Permissions**
```javascript
// Password-protected rooms
const provider = new WebsocketProvider(host, room, ydoc, {
  password: 'secret123'
})

// Check if user has access
provider.on('access', (granted) => {
  if (!granted) {
    console.log('Access denied to room')
  }
})
```

### **Offline Support**
```javascript
// Yjs automatically handles offline scenarios
provider.on('status', ({ status }) => {
  if (status === 'disconnected') {
    // Show offline indicator
    showOfflineMessage()
  } else if (status === 'connected') {
    // Sync changes when back online
    hideOfflineMessage()
  }
})
```

## 🧪 Testing Collaboration

### **1. Start Multiple Browsers**
```bash
# Terminal 1: Start collaboration server
npm run collab:server

# Terminal 2: Start frontend
npm run dev

# Terminal 3: Start another frontend instance (different port)
npm run dev -- --port 3001
```

### **2. Test Real-time Editing**
- Open the same document in both browsers
- Type in one browser - see changes in the other
- Watch cursor positions update in real-time
- Test concurrent editing (multiple users typing simultaneously)

### **3. Network Simulation**
```javascript
// Simulate network issues
provider.ws.close()

// Watch automatic reconnection
provider.on('status', ({ status }) => {
  console.log('Connection status:', status)
})
```

## 🚨 Common Issues & Solutions

### **Issue: Cursors Not Showing**
```javascript
// Ensure QuillCursors is registered
Quill.register('modules/cursors', QuillCursors)

// Check if cursors module is enabled
modules: {
  cursors: true
}
```

### **Issue: Content Not Syncing**
```javascript
// Verify binding is created
if (binding) {
  console.log('Binding active')
} else {
  console.log('Binding failed')
}

// Check Yjs connection
console.log('Connected:', provider.wsconnected)
```

### **Issue: WebSocket Connection Failed**
```bash
# Check if server is running
lsof -i :1234

# Restart collaboration server
npm run collab:server
```

## 📊 Performance Considerations

### **Large Documents**
```javascript
// For very large documents, consider chunking
const chunkSize = 1000
const chunks = Math.ceil(content.length / chunkSize)

for (let i = 0; i < chunks; i++) {
  const chunk = content.substr(i * chunkSize, chunkSize)
  ytext.insert(i * chunkSize, chunk)
}
```

### **Memory Management**
```javascript
// Clean up when component unmounts
onBeforeUnmount(() => {
  if (binding) binding.destroy()
  if (provider) provider.destroy()
  if (ydoc) ydoc.destroy()
})
```

## 🔒 Security Considerations

### **Room Access Control**
```javascript
// Implement authentication
const provider = new WebsocketProvider(host, room, ydoc, {
  password: getAuthToken(),
  headers: {
    'Authorization': `Bearer ${getAuthToken()}`
  }
})
```

### **Content Validation**
```javascript
// Validate content before applying
quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user') {
    const content = quill.getText()
    if (isContentValid(content)) {
      // Apply changes
    } else {
      // Revert changes
      quill.updateContents(oldDelta, 'api')
    }
  }
})
```

## 🎉 What You've Achieved

With this implementation, you now have:

1. **Real-time collaborative editing** like Google Docs
2. **Automatic conflict resolution** via CRDT
3. **User presence and cursor tracking**
4. **Seamless offline/online experience**
5. **Scalable architecture** for multiple users
6. **Professional-grade collaboration** ready for production

This is exactly the kind of sophisticated real-time system that impresses in FAANG interviews! 🚀
