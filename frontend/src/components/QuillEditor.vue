<template>
  <div class="quill-editor-container">
    <!-- Collaboration Status Indicator -->
    <div
      v-if="collaborationStatus !== 'connected'"
      class="collab-status bg-yellow-50 border border-yellow-200 rounded-t-md px-3 py-2 text-sm text-yellow-800"
    >
      <div class="flex items-center">
        <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
        {{
          collaborationStatus === 'timeout'
            ? 'Collaboration server unavailable - running in local mode'
            : 'Connecting to collaboration server...'
        }}
      </div>
    </div>

    <div ref="editorRef" class="quill-editor"></div>
  </div>
</template>

<script>
  import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
  import Quill from 'quill'
  import 'quill/dist/quill.snow.css'
  import * as Y from 'yjs'
  import { WebsocketProvider } from 'y-websocket'
  import { QuillBinding } from 'y-quill'
  import QuillCursors from 'quill-cursors'

  export default {
    name: 'QuillEditor',
    props: {
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
      roomName: {
        type: String,
        default: 'default',
      },
    },
    emits: ['update:modelValue', 'text-change', 'collaboration-ready'],
    setup(props, { emit }) {
      const editorRef = ref(null)
      const collaborationStatus = ref('connecting')
      let quill = null
      let ydoc = null
      let provider = null
      let ytext = null
      let binding = null

      // Computed properties for configuration
      const collabConfig = computed(() => {
        const config = {
          host: import.meta.env.VITE_COLLAB_WS || 'ws://127.0.0.1:1234',
          room: `${props.roomName}-${props.documentId}`,
          password: import.meta.env.VITE_COLLAB_PASSWORD || undefined,
        }
        return config
      })

      const setQuillContent = (content, silent = false) => {
        if (!quill) return
        try {
          if (content && content.trim()) {
            // AGGRESSIVE content cleaning to prevent all corruption
            let cleanContent = content
              .replace(/&lt;/g, '<')
              .replace(/&gt;/g, '>')
              .replace(/&amp;/g, '&')
              .replace(/<p><p>/g, '<p>') // Remove duplicate paragraph tags
              .replace(/<\/p><\/p>/g, '</p>') // Remove duplicate closing tags

            // If content still looks corrupted, reject it entirely
            if (
              cleanContent.includes('&lt;') ||
              cleanContent.includes('&gt;') ||
              cleanContent.includes('<p><p>') ||
              cleanContent.includes('</p></p>')
            ) {
              return
            }

            const delta = quill.clipboard.convert(cleanContent)
            quill.setContents(delta, silent ? 'silent' : undefined)
          } else {
            quill.setContents([], silent ? 'silent' : undefined)
          }
        } catch (error) {
          // Silently handle errors in production
        }
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

      // Initialize Quill with cursors module
      const initializeQuill = () => {
        // Register QuillCursors module
        Quill.register('modules/cursors', QuillCursors)

        quill = new Quill(editorRef.value, {
          theme: 'snow',
          modules: {
            toolbar: toolbarOptions,
            cursors: true,
          },
          placeholder: props.placeholder,
          readOnly: props.readOnly,
        })

        // DON'T set initial content here - let Yjs handle it during collaboration setup
        // This prevents conflicts between Quill and Yjs content initialization

        // Listen for text changes
        quill.on('text-change', (delta, oldDelta, source) => {
          if (source === 'user') {
            // Get clean HTML using Quill's proper method
            const cleanHtml = quill.root.innerHTML
              .replace(/&lt;/g, '<')
              .replace(/&gt;/g, '>')
              .replace(/&amp;/g, '&')

            emit('update:modelValue', cleanHtml)
            emit('text-change', { delta, oldDelta, source })
          }
        })

        // Handle focus to ensure cursor position is maintained
        quill.on('focus', () => {
          // When user focuses, ensure cursor is at the end if no selection
          const selection = quill.getSelection()
          if (!selection || selection.index === 0) {
            const length = quill.getLength()
            if (length > 1) {
              quill.setSelection(length - 1, 0)
            }
          }
        })

        // Handle readOnly changes
        if (props.readOnly) {
          quill.disable()
        } else {
          quill.enable()
        }
      }

      // Initialize Yjs collaboration
      const initializeCollaboration = async () => {
        try {
          // Create Yjs document
          ydoc = new Y.Doc()

          // Create WebSocket provider
          provider = new WebsocketProvider(
            collabConfig.value.host,
            collabConfig.value.room,
            ydoc,
            {
              password: collabConfig.value.password,
              connect: true,
            }
          )
          // Get or create the shared text
          ytext = ydoc.getText('quill')
          // Set initial content in Yjs BEFORE creating the binding
          if (props.modelValue !== undefined && props.modelValue !== null) {
            // Convert HTML to plain text for Yjs storage
            const tempDiv = document.createElement('div')
            tempDiv.innerHTML = props.modelValue
            const plainText = tempDiv.textContent || tempDiv.innerText || ''

            // Clear Yjs and insert plain text (not HTML)
            ytext.delete(0, ytext.length)
            ytext.insert(0, plainText)
          }

          // Wait for connection to be established with timeout
          const connectionPromise = new Promise(resolve => {
            if (provider.wsconnected) {
              resolve()
            } else {
              provider.on('status', ({ status }) => {
                if (status === 'connected') {
                  resolve()
                }
              })
            }
          })

          // Add timeout to prevent hanging
          const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Connection timeout')), 5000)
          })

          await Promise.race([connectionPromise, timeoutPromise])
          collaborationStatus.value = 'connected'

          // Create Quill binding
          binding = new QuillBinding(ytext, quill, provider.awareness)

          // Ensure editor is enabled/disabled based on readOnly prop after binding
          if (props.readOnly) {
            quill.disable()
          } else {
            quill.enable()
          }
          // Initial sync - only if Yjs has content and Quill is empty
          const quillText = quill.getText().trim()
          const yjsText = ytext.toString().trim()

          if (yjsText && (!quillText || quill.getLength() <= 1)) {
            try {
              // Yjs contains plain text, so we can set it directly
              quill.setText(yjsText)
            } catch (error) {
              // Silently handle sync errors
            }
          }
          // Emit collaboration ready event
          emit('collaboration-ready', { provider, ydoc, ytext })
        } catch (error) {
          // Fallback to non-collaborative mode
          emit('collaboration-ready', null)
          collaborationStatus.value = 'timeout'

          // Ensure Quill has content in fallback mode
          if (
            quill &&
            props.modelValue !== undefined &&
            props.modelValue !== null
          ) {
            setQuillContent(props.modelValue, true)
          }

          // Ensure editor is enabled/disabled based on readOnly prop
          if (props.readOnly) {
            quill.disable()
          } else {
            quill.enable()
          }
        }
      }

      // Handle awareness updates (cursor positions, user info)
      const setupAwareness = () => {
        if (!provider?.awareness) return

        // Set user information
        provider.awareness.setLocalStateField('user', {
          name: 'User', // You can make this configurable
          color: '#' + Math.floor(Math.random() * 16777215).toString(16),
          id: Math.random().toString(36).substr(2, 9),
        })
      }

      onMounted(async () => {
        // Initialize Quill first
        initializeQuill()

        // Initialize collaboration
        await initializeCollaboration()

        // Setup awareness
        setupAwareness()
      })

      watch(
        () => props.readOnly,
        newValue => {
          if (quill) {
            if (newValue) {
              quill.disable()
            } else {
              quill.enable()
            }
          }
        }
      )

      // Watch for documentId changes (reinitialize collaboration)
      watch(
        () => props.documentId,
        async (newId, oldId) => {
          if (newId && newId !== oldId) {
            // Clean up old collaboration
            if (binding) {
              binding.destroy()
              binding = null
            }
            if (provider) {
              provider.destroy()
              provider = null
            }

            // Reinitialize with new document
            await initializeCollaboration()
            setupAwareness()
          }
        }
      )

      // Watch for roomName changes
      watch(
        () => props.roomName,
        async (newRoom, oldRoom) => {
          if (newRoom && newRoom !== oldRoom && props.documentId) {
            // Clean up old collaboration
            if (binding) {
              binding.destroy()
              binding = null
            }
            if (provider) {
              provider.destroy()
              provider = null
            }

            // Reinitialize with new room
            await initializeCollaboration()
            setupAwareness()
          }
        }
      )

      onBeforeUnmount(() => {
        // Clean up Quill binding
        if (binding) {
          binding.destroy()
          binding = null
        }

        // Clean up provider
        if (provider) {
          provider.destroy()
          provider = null
        }

        // Clean up Yjs document
        if (ydoc) {
          ydoc.destroy()
          ydoc = null
        }

        // Clean up Quill
        if (quill) {
          quill = null
        }
      })

      return {
        editorRef,
        collaborationStatus,

        // Public methods
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

        // Method to manually sync content
        syncContent(content) {
          if (!quill) return

          if (!binding) {
            // Before collaboration binding exists → safe to set HTML
            const delta = quill.clipboard.convert(content || '')
            quill.setContents(delta, 'silent')
          } else {
            // After binding exists, never insert HTML strings into ytext
            // Instead, convert to Delta and update Quill
            if (content !== undefined && content !== null) {
              const delta = quill.clipboard.convert(content)
              const range = quill.getSelection()

              quill.updateContents(delta, 'silent')

              // Restore cursor position
              if (range) {
                quill.setSelection(range.index, range.length)
              }
            }
          }
        },

        // Emergency content reset function
        resetContent() {
          if (!quill) return

          // Clear everything
          quill.setContents([], 'silent')

          // Clear Yjs if available
          if (ytext) {
            ytext.delete(0, ytext.length)
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
