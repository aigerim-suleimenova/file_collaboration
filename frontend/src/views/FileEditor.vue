<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-xl font-bold text-gray-900">
                File Collaboration
              </h1>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link
                to="/"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Dashboard
              </router-link>
              <router-link
                to="/files"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Files
              </router-link>
            </div>
          </div>
          <div class="hidden sm:ml-6 sm:flex sm:items-center">
            <div class="ml-3 relative">
              <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-700">{{
                  authStore.user?.email
                }}</span>
                <button
                  class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                  @click="handleLogout"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
          <div class="flex items-center space-x-4">
            <router-link
              to="/files"
              class="text-gray-500 hover:text-gray-700 flex items-center"
            >
              <svg
                class="h-5 w-5 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back to Files
            </router-link>
            <h2 class="text-2xl font-bold text-gray-900">
              {{ isEditMode ? 'Edit File' : 'View File' }}
            </h2>
          </div>
          <div class="flex space-x-3">
            <button
              class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              @click="openShareModal"
            >
              Share
            </button>
            <button
              v-if="!isEditMode && !shareTokenFromUrl"
              class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              @click="toggleEditMode"
            >
              Edit
            </button>
            <button
              v-if="file?.quill_content && !shareTokenFromUrl"
              :disabled="isExporting"
              class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-md text-sm font-medium"
              @click="exportToDocx"
            >
              {{ isExporting ? 'Exporting...' : 'Export to DOCX' }}
            </button>
            <template v-else>
              <button
                v-if="!shareTokenFromUrl"
                :disabled="isLoading"
                class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                @click="saveFile"
              >
                {{ isLoading ? 'Saving...' : 'Save' }}
              </button>
              <button
                v-if="!shareTokenFromUrl"
                :disabled="isLoading"
                class="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                @click="cancelEdit"
              >
                Cancel
              </button>
            </template>
          </div>
        </div>

        <!-- Error Message -->
        <div
          v-if="error"
          class="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded"
        >
          {{ error }}
        </div>

        <!-- Success Message -->
        <div
          v-if="successMessage"
          class="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded"
        >
          {{ successMessage }}
        </div>

        <!-- Loading State -->
        <div
          v-if="isLoading && !file"
          class="flex justify-center items-center py-12"
        >
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"
          ></div>
          <span class="ml-2 text-gray-600">Loading file...</span>
        </div>

        <!-- Loading Route Params -->
        <div v-else-if="!fileId" class="flex justify-center items-center py-12">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
          <span class="ml-2 text-gray-600">Loading route parameters...</span>
          <div class="mt-2 text-sm text-gray-500">
            Route params: {{ JSON.stringify(route.params) }}
          </div>
        </div>

        <!-- File Editor -->
        <div v-else-if="file && fileId" class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900">
                  {{ file.filename }}
                </h3>
                <p class="text-sm text-gray-500 mt-1">
                  Last modified: {{ formatDate(file.updated_at) }}
                </p>
              </div>
              <div class="flex items-center space-x-2">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                >
                  {{ getFileExtension(file.filename) || 'txt' }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ getContentLength(file.content) }} characters
                </span>
              </div>
            </div>
          </div>

          <div class="p-6">
            <!-- Loading State for fileId -->
            <div v-if="!fileId" class="text-center py-8">
              <div
                class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"
              ></div>
              <p class="text-gray-600">Loading collaboration...</p>
              <p class="text-sm text-gray-500 mt-2">
                File ID: {{ fileId || 'Not available' }}
              </p>
            </div>

            <!-- Collaboration Status -->
            <div
              v-if="isCollaborating"
              class="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <div
                    class="w-2 h-2 bg-green-500 rounded-full animate-pulse"
                  ></div>
                  <span class="text-sm font-medium text-blue-900">
                    Live collaboration active
                  </span>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-xs text-blue-600">
                    {{ activeUsers.length }} user(s) editing
                  </span>
                  <div class="flex space-x-1">
                    <div
                      v-for="user in activeUsers"
                      :key="user.id"
                      class="w-6 h-6 rounded-full flex items-center justify-center text-xs text-white font-medium"
                      :style="{ backgroundColor: user.color }"
                      :title="user.name"
                    >
                      {{ user.name.charAt(0).toUpperCase() }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Edit Mode -->
            <div v-if="isEditMode && file && fileId" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Filename
                </label>
                <input
                  v-model="editForm.filename"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter filename"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Content
                </label>
                <div v-if="!fileId" class="text-sm text-gray-500 mb-2">
                  Loading file ID...
                </div>

                <!-- Conversion Status -->
                <div
                  v-if="
                    file?.original_format === 'docx' &&
                    !file?.quill_content &&
                    !isConverting
                  "
                  class="bg-yellow-50 border border-yellow-200 rounded-md p-3 mb-4"
                >
                  <div class="flex items-center">
                    <svg
                      class="w-5 h-5 text-yellow-400 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <div>
                      <p class="text-sm text-yellow-800">
                        This is a DOCX file. Converting to Quill format for rich
                        text editing...
                      </p>
                      <button
                        :disabled="isConverting"
                        class="mt-2 inline-flex items-center px-3 py-1 border border-yellow-300 rounded-md text-xs font-medium text-yellow-700 bg-white hover:bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50"
                        @click="convertToQuill"
                      >
                        <svg
                          v-if="isConverting"
                          class="animate-spin w-3 h-3 mr-1"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            class="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            stroke-width="4"
                          ></circle>
                          <path
                            class="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        {{ isConverting ? 'Converting...' : 'Convert Now' }}
                      </button>
                    </div>
                  </div>
                </div>

                <div
                  v-if="isConverting"
                  class="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4"
                >
                  <div class="flex items-center">
                    <svg
                      class="animate-spin w-5 h-5 text-blue-400 mr-2"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      ></circle>
                      <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    <p class="text-sm text-blue-800">
                      Converting DOCX to Quill format... This may take a few
                      moments.
                    </p>
                  </div>
                </div>
                <QuillEditor
                  v-if="fileId && editForm.content !== undefined"
                  :key="`quill-${fileId}`"
                  ref="quillEditorRef"
                  v-model="editForm.content"
                  :read-only="false"
                  :document-id="fileId"
                  :access-token="shareTokenFromUrl ? null : authStore.token"
                  :share-token="shareTokenFromUrl || null"
                  :user="collabUser"
                  placeholder="Enter file content"
                  height="400px"
                  @collaboration-ready="onCollaborationReady"
                />
                <div
                  v-else-if="fileId && editForm.content === undefined"
                  class="text-center py-8"
                >
                  <div
                    class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"
                  ></div>
                  <p class="text-gray-600">Loading editor content...</p>
                </div>
                <div v-if="fileId" class="text-xs text-gray-500 mt-1">
                  Document ID: {{ fileId }}
                </div>
              </div>
            </div>

            <!-- View Mode -->
            <div v-else>
              <div class="prose max-w-none">
                <!-- Safe: sanitizedViewContent is passed through DOMPurify (see setup). -->
                <!-- eslint-disable vue/no-v-html -->
                <div
                  v-if="sanitizedViewContent"
                  class="bg-gray-50 p-4 rounded-lg border min-h-[400px] whitespace-pre-wrap text-sm text-gray-700"
                  v-html="sanitizedViewContent"
                ></div>
                <!-- eslint-enable vue/no-v-html -->
                <div
                  v-else
                  class="bg-gray-50 p-4 rounded-lg border min-h-[400px] text-sm text-gray-500"
                >
                  No content available
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- File Not Found -->
        <div v-else-if="!isLoading" class="text-center py-12">
          <svg
            class="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">File not found</h3>
          <p class="mt-1 text-sm text-gray-500">
            The file you're looking for doesn't exist or has been deleted.
          </p>
          <div class="mt-6">
            <router-link
              to="/files"
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              Back to Files
            </router-link>
          </div>
        </div>
      </div>
    </div>
    <!-- Share Modal -->
    <div
      v-if="isShareModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center"
    >
      <div class="fixed inset-0 bg-black/50" @click="closeShareModal"></div>
      <div class="relative bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          Live collaboration
        </h3>
        <div class="space-y-3">
          <input
            type="text"
            :value="shareLink"
            readonly
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-700 select-all"
          />
          <div class="flex justify-end space-x-2">
            <button
              :disabled="shareLoading || !!shareToken"
              class="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white px-4 py-2 rounded-md text-sm font-medium"
              @click="createShare"
            >
              {{
                shareLoading
                  ? 'Generating...'
                  : shareToken
                    ? 'Generated'
                    : 'Generate link (4h)'
              }}
            </button>
            <button
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              @click="copyShareLink"
            >
              Copy link
            </button>
            <button
              class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              @click="closeShareModal"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, reactive, onMounted, computed, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useAuthStore } from '../stores/auth'
  import { filesApi } from '../services/api'
  import DOMPurify from 'dompurify'
  import QuillEditor from '../components/QuillEditor.vue'

  export default {
    name: 'FileEditor',
    components: {
      QuillEditor,
    },
    setup() {
      const router = useRouter()
      const route = useRoute()
      const authStore = useAuthStore()

      const file = ref(null)
      const isLoading = ref(false)
      const error = ref(null)
      const successMessage = ref(null)
      const isEditMode = ref(true)
      const isExporting = ref(false)
      const isConverting = ref(false)
      const quillEditorRef = ref(null)

      // Collaboration state management
      const collaborationState = ref(null)
      const activeUsers = ref([])
      const isCollaborating = ref(false)

      const editForm = reactive({
        filename: '',
        content: undefined,
      })
      const isShareModalOpen = ref(false)
      const shareToken = ref(null)
      const shareLoading = ref(false)
      const openShareModal = async () => {
        isShareModalOpen.value = true
        // pre-generate a token for convenience
        if (!shareToken.value) {
          await createShare()
        }
      }
      const closeShareModal = () => {
        isShareModalOpen.value = false
        shareToken.value = null
      }
      const shareLink = computed(() => {
        const base = `${window.location.origin}/files/${fileId.value}`
        return shareToken.value
          ? `${base}?share_token=${encodeURIComponent(shareToken.value)}`
          : base
      })
      const copyShareLink = async () => {
        if (!shareToken.value) {
          await createShare()
        }
        try {
          await navigator.clipboard.writeText(shareLink.value)
          successMessage.value = 'Link copied to clipboard'
          setTimeout(() => {
            if (successMessage.value === 'Link copied to clipboard')
              successMessage.value = null
          }, 2000)
        } catch (e) {
          console.error('Failed to copy link', e)
        }
      }

      const createShare = async () => {
        if (shareLoading.value || shareToken.value) return
        shareLoading.value = true
        try {
          const res = await filesApi.createShareToken(fileId.value)
          shareToken.value = res.data.share_token
          successMessage.value = 'Share link generated'
          setTimeout(() => {
            if (successMessage.value === 'Share link generated')
              successMessage.value = null
          }, 2000)
        } catch (e) {
          console.error('Failed to create share token', e)
          error.value =
            e?.response?.data?.detail || 'Failed to create share link'
        } finally {
          shareLoading.value = false
        }
      }

      const fileId = computed(() => {
        const id = route.params.id
        return id
      })
      const shareTokenFromUrl = computed(() => route.query.share_token)
      // Collaboration functions
      const onCollaborationReady = state => {
        collaborationState.value = state
        isCollaborating.value = Boolean(state)
        if (state?.provider?.awareness) {
          setupUserTracking(state.provider.awareness)
        }
      }

      // Identity shown on this user's cursor; share-link guests get one in QuillEditor.
      const collabUser = computed(() =>
        authStore.user
          ? {
              id: String(authStore.user.id),
              name: authStore.user.full_name || authStore.user.email,
            }
          : null
      )

      // Stored HTML is untrusted (any editor, incl. share-link guests, can change it):
      // sanitize before rendering it as markup.
      const sanitizedViewContent = computed(() => {
        const html = file.value?.quill_content || file.value?.content || ''
        return html
          ? DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
          : ''
      })

      const setupUserTracking = awareness => {
        console.log('Setting up user tracking')
        awareness.on('change', () => {
          const states = Array.from(awareness.getStates().values())
          activeUsers.value = states
            .filter(state => state.user)
            .map(state => state.user)
        })
      }

      const loadFile = async () => {
        if (!fileId.value) {
          error.value = 'Invalid file ID'
          return
        }

        isLoading.value = true
        error.value = null

        try {
          let response
          if (shareTokenFromUrl.value) {
            isEditMode.value = true
            response = await filesApi.getPublicFile(
              fileId.value,
              shareTokenFromUrl.value
            )
          } else {
            response = await filesApi.getFile(fileId.value)
          }
          file.value = response.data

          // Check if this is a DOCX file that needs conversion to Quill format
          if (
            file.value.original_format === 'docx' &&
            !file.value.quill_content
          ) {
            isConverting.value = true

            try {
              // Reload the file to get the updated quill_content
              const updatedResponse = await filesApi.getFile(fileId.value)
              file.value = updatedResponse.data

              successMessage.value =
                'File automatically converted to Quill format! You can now edit with rich text formatting.'
              setTimeout(() => {
                successMessage.value = null
              }, 5000)
            } catch (conversionErr) {
              console.warn(
                'Failed to auto-convert DOCX to Quill format:',
                conversionErr
              )
              error.value =
                'Failed to automatically convert file to Quill format. You can try converting manually.'
              // Continue without conversion
            } finally {
              isConverting.value = false
            }
          }

          // Initialize edit form with current file data
          // Prefer quill_content for rich editing, fallback to regular content
          editForm.filename = file.value.filename
          // Only seeds documents without collaborative state; see QuillEditor.
          editForm.content =
            file.value.quill_content || file.value.content || ''
        } catch (err) {
          error.value = 'Failed to load file. Please try again.'
          console.error('Error loading file:', err)
        } finally {
          isLoading.value = false
        }
      }

      const toggleEditMode = () => {
        isEditMode.value = true
        // Reset form with current file data
        editForm.filename = file.value.filename
        editForm.content = file.value.quill_content || file.value.content || ''
        error.value = null
        successMessage.value = null
      }

      const cancelEdit = () => {
        isEditMode.value = false
        // Reset form
        editForm.filename = file.value.filename
        editForm.content = file.value.quill_content || file.value.content || ''
        error.value = null
      }

      const saveFile = async () => {
        if (shareTokenFromUrl.value) {
          error.value = 'Cannot save when viewing via shared link'
          return
        }
        if (!editForm.filename.trim()) {
          error.value = 'Filename is required'
          return
        }

        isLoading.value = true
        error.value = null
        successMessage.value = null

        try {
          // First, update the Quill content using the new API
          if (
            editForm.content &&
            editForm.content !==
              (file.value.quill_content || file.value.content)
          ) {
            await filesApi.updateQuillContent(fileId.value, editForm.content)
          }

          // Then update the file metadata if needed
          const response = await filesApi.updateFile(fileId.value, editForm)
          file.value = response.data
          isEditMode.value = false
          successMessage.value = 'File saved successfully!'

          // Clear success message after 3 seconds
          setTimeout(() => {
            successMessage.value = null
          }, 3000)
        } catch (err) {
          error.value = 'Failed to save file. Please try again.'
          console.error('Error saving file:', err)
        } finally {
          isLoading.value = false
        }
      }

      const handleLogout = () => {
        authStore.logout()
        router.push('/login')
      }

      const formatDate = dateString => {
        if (!dateString) return 'Unknown'
        return new Date(dateString).toLocaleString()
      }

      const getFileExtension = filename => {
        if (!filename) return ''
        const parts = filename.split('.')
        return parts.length > 1 ? parts.pop().toLowerCase() : ''
      }

      const getContentLength = content => {
        if (!content) return 0
        // Strip HTML tags for character count
        const textContent = content.replace(/<[^>]*>/g, '')
        return textContent.length
      }

      onMounted(() => {
        // Wait a bit for route to be fully resolved
        setTimeout(() => {
          if (fileId.value) {
            console.log('Loading file')
            loadFile()
            // Needed for the collaborator cursor label after a page reload.
            if (
              !shareTokenFromUrl.value &&
              authStore.token &&
              !authStore.user
            ) {
              authStore.getCurrentUser()
            }
          } else {
            console.log('No fileId')
          }
        }, 100)
      })

      // Reload when share token changes (e.g., pasted link)
      watch(
        () => route.query.share_token,
        async () => {
          await loadFile()
        }
      )

      // Watch for fileId changes
      watch(
        () => fileId.value,
        async (newId, oldId) => {
          if (newId && newId !== oldId) {
            await loadFile()
          }
        }
      )

      const convertToQuill = async () => {
        if (
          !file.value?.original_format === 'docx' ||
          file.value?.quill_content
        ) {
          return
        }

        isConverting.value = true
        error.value = null
        successMessage.value = null

        try {
          await filesApi.convertToQuill(fileId.value)

          // Reload the file to get the updated quill_content
          await loadFile()

          successMessage.value =
            'File converted to Quill format successfully! You can now edit with rich text formatting.'

          // Clear success message after 5 seconds
          setTimeout(() => {
            successMessage.value = null
          }, 5000)
        } catch (err) {
          error.value =
            'Failed to convert file to Quill format. Please try again.'
          console.error('Error converting to Quill:', err)
        } finally {
          isConverting.value = false
        }
      }

      const exportToDocx = async () => {
        if (!file.value?.quill_content) {
          error.value = 'No Quill content available for export'
          return
        }

        isExporting.value = true
        error.value = null
        successMessage.value = null

        try {
          const response = await filesApi.convertToDocx(fileId.value)

          // The response contains the new converted file
          const convertedFile = response.data

          successMessage.value = `File exported to DOCX successfully! New file: ${convertedFile.filename}`

          // Clear success message after 5 seconds
          setTimeout(() => {
            successMessage.value = null
          }, 5000)
        } catch (err) {
          error.value = 'Failed to export file to DOCX. Please try again.'
          console.error('Error exporting to DOCX:', err)
        } finally {
          isExporting.value = false
        }
      }

      return {
        file,
        isLoading,
        error,
        successMessage,
        isEditMode,
        isExporting,
        isConverting,
        shareTokenFromUrl,
        editForm,
        authStore,
        toggleEditMode,
        cancelEdit,
        saveFile,
        handleLogout,
        formatDate,
        getFileExtension,
        getContentLength,
        // share modal
        isShareModalOpen,
        openShareModal,
        closeShareModal,
        shareLink,
        copyShareLink,
        createShare,
        quillEditorRef,
        convertToQuill,
        exportToDocx,
        // collaboration status
        isCollaborating,
        activeUsers,
        collaborationState,
        onCollaborationReady,
        collabUser,
        sanitizedViewContent,
        // computed properties
        fileId,
        // debugging
        route,
      }
    },
  }
</script>
