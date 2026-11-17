<template>
  <div class="quill-editor-container">
    <!-- Collaboration Status Indicator -->
    <div
      v-if="collaborationStatus !== 'connected'"
      class="collab-status border rounded-t-md px-3 py-2 text-sm"
      :class="
        collaborationStatus === 'denied'
          ? 'bg-red-50 border-red-200 text-red-800'
          : 'bg-yellow-50 border-yellow-200 text-yellow-800'
      "
      role="status"
    >
      {{ statusMessage }}
    </div>
    <div ref="editorRef" class="quill-editor"></div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
  import Quill from 'quill'
  import 'quill/dist/quill.snow.css'
  import * as Y from 'yjs'
  import { WebsocketProvider } from 'y-websocket'
  import { QuillBinding } from 'y-quill'
  import QuillCursors from 'quill-cursors'

  Quill.register('modules/cursors', QuillCursors)

  // Close codes sent by the backend's /api/v1/collab endpoint.
  const AUTH_CLOSE_MESSAGES = {
    4001: 'Your session has expired or this link is no longer valid. Sign in again or ask for a new link.',
    4003: "You don't have access to live editing for this document.",
    4004: 'This document no longer exists.',
  }
  const SLOW_CONNECTION_MS = 5000

  // Default collaboration endpoint: the configured backend origin if there is one
  // (http -> ws, https -> wss), otherwise this page's own origin.
  const defaultCollabUrl = () => {
    const apiBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
    if (apiBase) {
      return `${apiBase.replace(/^http/, 'ws')}/api/v1/collab`
    }
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    return `${proto}://${window.location.host}/api/v1/collab`
  }

  // Stable colour per user id, so a user's cursor keeps its colour across reconnects.
  const colorFor = id => {
    let hash = 0
    for (const ch of String(id)) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0
    return `hsl(${hash % 360}, 70%, 40%)`
  }

  const guestIdentity = () => {
    let id = null
    try {
      id = sessionStorage.getItem('collab-guest-id')
      if (!id) {
        id = `guest-${Math.random().toString(36).slice(2, 10)}`
        sessionStorage.setItem('collab-guest-id', id)
      }
    } catch {
      id = id || `guest-${Math.random().toString(36).slice(2, 10)}`
    }
    return { id, name: 'Guest' }
  }

  export default {
    name: 'QuillEditor',
    props: {
      // Stored HTML used only to seed a document that has no collaborative state yet.
      modelValue: {
        type: String,
        default: '',
      },
      placeholder: {
        type: String,
        default: 'Enter content...',
      },
      readOnly: {
        type: Boolean,
        default: false,
      },
      height: {
        type: String,
        default: '300px',
      },
      documentId: {
        type: String,
        required: true,
      },
      // Exactly one of accessToken / shareToken authorizes the collaboration socket.
      accessToken: {
        type: String,
        default: null,
      },
      shareToken: {
        type: String,
        default: null,
      },
      // { id, name } of the signed-in user; guests get an anonymous identity.
      user: {
        type: Object,
        default: null,
      },
    },
    emits: ['update:modelValue', 'text-change', 'collaboration-ready'],
    setup(props, { emit }) {
      const editorRef = ref(null)
      // connecting | slow | connected | denied
      const collaborationStatus = ref('connecting')
      const deniedMessage = ref('')
      let quill = null
      let ydoc = null
      let provider = null
      let ytext = null
      let binding = null
      let slowTimer = null

      const statusMessage = computed(() => {
        switch (collaborationStatus.value) {
          case 'denied':
            return deniedMessage.value
          case 'slow':
            return 'Collaboration server unavailable. Retrying… Editing is paused until it reconnects.'
          default:
            return 'Connecting to collaboration server…'
        }
      })

      const identity = () =>
        props.shareToken || !props.user?.id
          ? guestIdentity()
          : { id: props.user.id, name: props.user.name || 'User' }

      const setAwarenessUser = () => {
        if (!provider) return
        const { id, name } = identity()
        provider.awareness.setLocalStateField('user', {
          id,
          name,
          color: colorFor(id),
        })
      }

      const setEditable = enabled => {
        if (!quill) return
        if (enabled && !props.readOnly) quill.enable()
        else quill.disable()
      }

      const toolbarOptions = [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ header: 1 }, { header: 2 }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ script: 'sub' }, { script: 'super' }],
        [{ indent: '-1' }, { indent: '+1' }],
        [{ direction: 'rtl' }],
        [{ size: ['small', false, 'large', 'huge'] }],
        [{ header: [1, 2, 3, 4, 5, 6, false] }],
        [{ color: [] }, { background: [] }],
        [{ font: [] }],
        [{ align: [] }],
        ['clean'],
        ['link', 'image'],
      ]

      const initializeQuill = () => {
        quill = new Quill(editorRef.value, {
          theme: 'snow',
          modules: {
            toolbar: toolbarOptions,
            cursors: true,
          },
          placeholder: props.placeholder,
        })
        // Stay read-only until the shared document has synced, so nothing typed
        // offline can race with the server state or the one-time seeding.
        quill.disable()

        quill.on('text-change', (delta, oldDelta, source) => {
          // Quill escapes typed text in its HTML, so this is safe to store as-is.
          // Never un-escape entities here: that turns typed "<tags>" into markup.
          emit('update:modelValue', quill.root.innerHTML)
          if (source === 'user') {
            emit('text-change', { delta, oldDelta, source })
          }
        })
      }

      // Seed a document that has no collaborative state yet from its stored HTML,
      // keeping formatting. Runs once, after the first sync with the server.
      const seedInitialContent = () => {
        if (ytext.length > 0) return
        const html = props.modelValue
        if (!html || !html.trim()) return
        // 'user' source so the y-quill binding writes it into the shared document.
        // Quill drops 'user' changes while disabled, so enable it for the seed.
        const wasEnabled = quill.isEnabled()
        quill.enable()
        quill.setContents(quill.clipboard.convert({ html }), 'user')
        if (!wasEnabled) quill.disable()
      }

      const initializeCollaboration = () => {
        collaborationStatus.value = 'connecting'
        deniedMessage.value = ''

        ydoc = new Y.Doc()
        ytext = ydoc.getText('quill')

        const params = props.shareToken
          ? { share_token: props.shareToken }
          : props.accessToken
            ? { token: props.accessToken }
            : {}

        provider = new WebsocketProvider(
          import.meta.env.VITE_COLLAB_WS || defaultCollabUrl(),
          props.documentId,
          ydoc,
          { params, connect: false }
        )
        // Set presence before connecting so the first awareness update has the name.
        setAwarenessUser()
        binding = new QuillBinding(ytext, quill, provider.awareness)

        provider.on('connection-close', event => {
          const message = event && AUTH_CLOSE_MESSAGES[event.code]
          if (message) {
            // Auth failures won't fix themselves: stop reconnecting.
            provider.disconnect()
            clearTimeout(slowTimer)
            deniedMessage.value = message
            collaborationStatus.value = 'denied'
            setEditable(false)
          }
        })

        provider.on('status', ({ status }) => {
          if (collaborationStatus.value === 'denied') return
          if (status !== 'connected') {
            collaborationStatus.value = 'connecting'
            setEditable(false)
          }
        })

        let seeded = false
        provider.on('sync', isSynced => {
          if (!isSynced || collaborationStatus.value === 'denied') return
          clearTimeout(slowTimer)
          if (!seeded) {
            seeded = true
            seedInitialContent()
          }
          collaborationStatus.value = 'connected'
          setEditable(true)
        })

        slowTimer = setTimeout(() => {
          if (collaborationStatus.value === 'connecting') {
            collaborationStatus.value = 'slow'
          }
        }, SLOW_CONNECTION_MS)

        provider.connect()
        emit('collaboration-ready', { provider, ydoc, ytext })
      }

      const destroyCollaboration = () => {
        clearTimeout(slowTimer)
        binding?.destroy()
        binding = null
        provider?.destroy()
        provider = null
        ydoc?.destroy()
        ydoc = null
        ytext = null
      }

      onMounted(() => {
        initializeQuill()
        initializeCollaboration()
      })

      watch(
        () => props.readOnly,
        () => setEditable(collaborationStatus.value === 'connected')
      )

      // The signed-in user may load after the editor mounts.
      watch(() => [props.user?.id, props.user?.name], setAwarenessUser)

      // Switching document or credentials means a new shared document.
      watch(
        () => [props.documentId, props.accessToken, props.shareToken],
        (next, prev) => {
          if (next.join() === prev.join()) return
          destroyCollaboration()
          quill.setContents([], 'silent')
          quill.disable()
          initializeCollaboration()
        }
      )

      onBeforeUnmount(() => {
        destroyCollaboration()
        quill = null
      })

      return {
        editorRef,
        collaborationStatus,
        statusMessage,

        getQuillInstance() {
          return quill
        },

        getCollaborationState() {
          return {
            provider,
            ydoc,
            ytext,
            binding,
            connected: provider?.wsconnected || false,
          }
        },
      }
    },
  }
</script>

<style scoped>
  .quill-editor-container {
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    overflow: hidden;
  }

  .quill-editor {
    height: v-bind(height);
  }

  /* Ensure Quill editor is properly styled and interactive */
  .quill-editor :deep(.ql-editor) {
    min-height: v-bind(height);
    font-size: 14px;
    line-height: 1.5;
    cursor: text;
  }

  .quill-editor :deep(.ql-toolbar) {
    border-bottom: 1px solid #d1d5db;
    background-color: #f9fafb;
  }

  .quill-editor :deep(.ql-container) {
    border: none;
  }

  .quill-editor :deep(.ql-editor.ql-blank::before) {
    color: #9ca3af;
    font-style: italic;
  }

  /* Ensure the editor is interactive when not read-only */
  .quill-editor :deep(.ql-editor:not(.ql-disabled)) {
    cursor: text;
  }

  .quill-editor :deep(.ql-editor.ql-disabled) {
    cursor: not-allowed;
  }

  /* Cursor styling for collaboration */
  .quill-editor :deep(.ql-cursor) {
    border-left: 2px solid;
    border-right: 2px solid;
    margin-left: -1px;
    margin-right: -1px;
    pointer-events: none;
    position: absolute;
    z-index: 1;
  }

  .quill-editor :deep(.ql-cursor-selection) {
    background-color: rgba(0, 0, 255, 0.1);
    pointer-events: none;
    position: absolute;
    z-index: 0;
  }
</style>
