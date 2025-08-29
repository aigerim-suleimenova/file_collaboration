<template>
  <div class="file-viewer">
    <!-- File Header -->
    <div class="file-header bg-white border-b border-gray-200 p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="file-icon">
            <svg
              v-if="isDocument"
              class="w-8 h-8 text-blue-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
              />
            </svg>
            <svg
              v-else-if="isImage"
              class="w-8 h-8 text-green-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
              />
            </svg>
            <svg
              v-else
              class="w-8 h-8 text-gray-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
              />
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-semibold text-gray-900">
              {{ file?.filename }}
            </h2>
            <p class="text-sm text-gray-500">
              {{ formatFileSize(file?.file_size) }} • {{ file?.mime_type }}
            </p>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <button
            @click="downloadFile"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path
                d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"
              />
            </svg>
            Download
          </button>

          <button
            @click="shareFile"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path
                d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"
              />
            </svg>
            Share
          </button>
        </div>
      </div>
    </div>

    <!-- File Content Area -->
    <div class="file-content bg-gray-50 flex-1 p-6">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-64">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
        ></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <svg
          class="mx-auto h-12 w-12 text-red-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
          />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">
          Error loading file
        </h3>
        <p class="mt-1 text-sm text-gray-500">{{ error }}</p>
        <div class="mt-6">
          <button
            @click="loadFile"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Try again
          </button>
        </div>
      </div>

      <!-- File Content -->
      <div v-else-if="file" class="max-w-4xl mx-auto">
        <!-- Document Viewer -->
        <div
          v-if="isDocument"
          class="bg-white rounded-lg shadow-sm border border-gray-200"
        >
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-gray-900">
                Document Preview
              </h3>
              <div class="flex space-x-2">
                <button
                  @click="openInNewTab"
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"
                    />
                  </svg>
                  Open in New Tab
                </button>
                <button
                  @click="editFile"
                  class="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
                    />
                  </svg>
                  Edit File
                </button>
              </div>
            </div>

            <!-- Document Content Preview -->
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center"
            >
              <svg
                class="mx-auto h-12 w-12 text-gray-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">
                {{ file.filename }}
              </h3>
              <p class="mt-1 text-sm text-gray-500">
                {{ formatFileSize(file.file_size) }} • {{ file.mime_type }}
              </p>
              <div class="mt-6">
                <button
                  @click="downloadFile"
                  class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Download to Edit
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Image Viewer -->
        <div
          v-else-if="isImage"
          class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
        >
          <div class="p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">
              Image Preview
            </h3>
            <img
              :src="imageUrl"
              :alt="file.filename"
              class="max-w-full h-auto rounded-lg shadow-sm"
              @error="handleImageError"
            />
          </div>
        </div>

        <!-- Text Viewer -->
        <div
          v-else-if="isText"
          class="bg-white rounded-lg shadow-sm border border-gray-200"
        >
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-gray-900">Text Content</h3>
              <button
                @click="editText"
                class="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg
                  class="w-4 h-4 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"
                  />
                </svg>
                Edit
              </button>
            </div>
            <pre
              class="bg-gray-50 p-4 rounded-lg text-sm text-gray-800 whitespace-pre-wrap overflow-x-auto"
              >{{ textContent }}</pre
            >
          </div>
        </div>

        <!-- Generic File Viewer -->
        <div
          v-else
          class="bg-white rounded-lg shadow-sm border border-gray-200"
        >
          <div class="p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">
              File Information
            </h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm font-medium text-gray-500">Filename:</span>
                <span class="text-sm text-gray-900">{{ file.filename }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm font-medium text-gray-500">Size:</span>
                <span class="text-sm text-gray-900">{{
                  formatFileSize(file.file_size)
                }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm font-medium text-gray-500">Type:</span>
                <span class="text-sm text-gray-900">{{ file.mime_type }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm font-medium text-gray-500">Created:</span>
                <span class="text-sm text-gray-900">{{
                  formatDate(file.created_at)
                }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Share Modal -->
    <div
      v-if="showShareModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
      >
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Share File</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >Expiration (hours)</label
              >
              <input
                v-model="shareExpiration"
                type="number"
                min="1"
                max="168"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div v-if="shareToken" class="bg-gray-50 p-3 rounded-md">
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Share Link</label
              >
              <div class="flex">
                <input
                  :value="shareUrl"
                  readonly
                  class="flex-1 border-gray-300 rounded-l-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                <button
                  @click="copyShareUrl"
                  class="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                    <path
                      d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"
                    />
                  </svg>
                </button>
              </div>
            </div>
            <div class="flex justify-end space-x-3">
              <button
                @click="closeShareModal"
                class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                v-if="!shareToken"
                @click="generateShareToken"
                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Generate Link
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted } from 'vue'
  // import { useAuthStore } from '../stores/auth' // Unused - commented out
  import api from '../services/api'

  export default {
    name: 'FileViewer',
    props: {
      fileId: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      // const authStore = useAuthStore() // Unused - commented out
      const file = ref(null)
      const loading = ref(true)
      const error = ref(null)
      const showShareModal = ref(false)
      const shareToken = ref(null)
      const shareExpiration = ref(4)
      const textContent = ref('')
      const imageUrl = ref('')

      // Computed properties
      const isDocument = computed(() => {
        if (!file.value?.mime_type) return false
        return (
          file.value.mime_type.includes('document') ||
          file.value.mime_type.includes('word') ||
          file.value.mime_type.includes('pdf') ||
          file.value.mime_type.includes('excel') ||
          file.value.mime_type.includes('powerpoint')
        )
      })

      const isImage = computed(() => {
        if (!file.value?.mime_type) return false
        return file.value.mime_type.startsWith('image/')
      })

      const isText = computed(() => {
        if (!file.value?.mime_type) return false
        return (
          file.value.mime_type.startsWith('text/') ||
          file.value.mime_type.includes('javascript') ||
          file.value.mime_type.includes('python') ||
          file.value.mime_type.includes('html') ||
          file.value.mime_type.includes('css')
        )
      })

      const shareUrl = computed(() => {
        if (!shareToken.value) return ''
        return `${window.location.origin}/public/files/${props.fileId}?token=${shareToken.value}`
      })

      // Methods
      const loadFile = async () => {
        loading.value = true
        error.value = null

        try {
          const response = await api.get(`/files/${props.fileId}`)
          file.value = response.data

          // Load text content for text files
          if (isText.value) {
            await loadTextContent()
          }

          // Load image for image files
          if (isImage.value) {
            await loadImageContent()
          }
        } catch (err) {
          error.value = err.response?.data?.detail || 'Failed to load file'
          console.error('Error loading file:', err)
        } finally {
          loading.value = false
        }
      }

      const loadTextContent = async () => {
        try {
          const response = await api.get(`/files/${props.fileId}/content`)
          textContent.value = response.data
        } catch (err) {
          console.error('Error loading text content:', err)
          textContent.value = 'Unable to load file content'
        }
      }

      const loadImageContent = async () => {
        try {
          const response = await api.get(`/files/${props.fileId}/download`)
          imageUrl.value = response.data.download_url
        } catch (err) {
          console.error('Error loading image:', err)
          imageUrl.value = ''
        }
      }

      const downloadFile = async () => {
        try {
          const response = await api.get(`/files/${props.fileId}/download`)
          const downloadUrl = response.data.download_url

          // Create temporary link and click it
          const link = document.createElement('a')
          link.href = downloadUrl
          link.download = file.value.filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        } catch (err) {
          console.error('Error downloading file:', err)
          alert('Failed to download file')
        }
      }

      const openInNewTab = async () => {
        try {
          const response = await api.get(`/files/${props.fileId}/download`)
          const downloadUrl = response.data.download_url
          window.open(downloadUrl, '_blank')
        } catch (err) {
          console.error('Error opening file:', err)
          alert('Failed to open file')
        }
      }

      const editFile = () => {
        downloadFile() // For now, just download and edit locally
      }

      const editText = () => {
        // For text files, you could implement inline editing
        alert('Text editing feature coming soon!')
      }

      const shareFile = () => {
        showShareModal.value = true
        shareToken.value = null
      }

      const generateShareToken = async () => {
        try {
          const formData = new FormData()
          formData.append('expires_hours', shareExpiration.value)

          const response = await api.post(
            `/files/${props.fileId}/share`,
            formData
          )
          shareToken.value = response.data.share_token
        } catch (err) {
          console.error('Error generating share token:', err)
          alert('Failed to generate share link')
        }
      }

      const copyShareUrl = async () => {
        try {
          await navigator.clipboard.writeText(shareUrl.value)
          alert('Share link copied to clipboard!')
        } catch (err) {
          console.error('Error copying to clipboard:', err)
          // Fallback for older browsers
          const textArea = document.createElement('textarea')
          textArea.value = shareUrl.value
          document.body.appendChild(textArea)
          textArea.select()
          document.execCommand('copy')
          document.body.removeChild(textArea)
          alert('Share link copied to clipboard!')
        }
      }

      const closeShareModal = () => {
        showShareModal.value = false
        shareToken.value = null
      }

      const formatFileSize = bytes => {
        if (!bytes) return 'Unknown size'
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(1024))
        return (
          Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i]
        )
      }

      const formatDate = dateString => {
        if (!dateString) return 'Unknown date'
        return new Date(dateString).toLocaleDateString()
      }

      const handleImageError = () => {
        imageUrl.value = ''
        error.value = 'Failed to load image'
      }

      // Lifecycle
      onMounted(() => {
        loadFile()
      })

      return {
        file,
        loading,
        error,
        showShareModal,
        shareToken,
        shareExpiration,
        textContent,
        imageUrl,
        isDocument,
        isImage,
        isText,
        shareUrl,
        loadFile,
        downloadFile,
        openInNewTab,
        editFile,
        editText,
        shareFile,
        generateShareToken,
        copyShareUrl,
        closeShareModal,
        formatFileSize,
        formatDate,
        handleImageError,
      }
    },
  }
</script>

<style scoped>
  .file-viewer {
    @apply flex flex-col h-full;
  }

  .file-content {
    @apply flex-1 overflow-auto;
  }

  .file-icon {
    @apply flex-shrink-0;
  }
</style>
