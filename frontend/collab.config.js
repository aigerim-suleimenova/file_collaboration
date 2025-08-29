// Collaboration Configuration
export const COLLAB_CONFIG = {
  // WebSocket server for collaboration
  WS_HOST: import.meta.env.VITE_COLLAB_WS || 'ws://127.0.0.1:1234',

  // Default room name
  DEFAULT_ROOM: import.meta.env.VITE_COLLAB_ROOM || 'filecollab',

  // Optional password for private rooms
  PASSWORD: import.meta.env.VITE_COLLAB_PASSWORD || undefined,

  // Connection timeout (ms)
  CONNECTION_TIMEOUT: 10000,

  // Reconnection settings
  RECONNECT_INTERVAL: 1000,
  MAX_RECONNECT_ATTEMPTS: 5
}

// Helper function to build room names
export const buildRoomName = (roomName, documentId) => {
  return `${roomName}-${documentId}`
}

// Helper function to get collaboration status
export const getCollaborationStatus = (provider) => {
  if (!provider) return 'disconnected'

  if (provider.wsconnected) return 'connected'
  if (provider.wsconnecting) return 'connecting'
  if (provider.wsconnected === false) return 'disconnected'

  return 'unknown'
}
