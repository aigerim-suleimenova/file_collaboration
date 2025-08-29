<template>
  <div class="files-page">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">My Files</h1>
        <p class="mt-2 text-gray-600">Upload, manage, and share your files</p>
        <div class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p class="text-sm text-blue-800">
            🚀 <strong>New Feature:</strong> DOCX files are automatically
            converted to Quill format for rich text editing and live
            collaboration!
          </p>
        </div>
      </div>

      <!-- Upload Section -->
      <div class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Upload Files</h2>
        <FileUpload @upload-complete="refreshFiles" />
      </div>

      <!-- Files List Section -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium text-gray-900">Your Files</h2>
            <div class="flex items-center space-x-3">
              <button
                @click="refreshFiles"
                :disabled="loading"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <svg
                  class="w-4 h-4 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                    clip-rule="evenodd"
                  />
                </svg>
                Refresh
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="p-8 text-center">
          <div
            class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"
          ></div>
          <p class="mt-4 text-gray-500">Loading files...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="p-8 text-center">
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
            Error loading files
          </h3>
          <p class="mt-1 text-sm text-gray-500">{{ error }}</p>
          <div class="mt-6">
            <button
              @click="refreshFiles"
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try again
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="files.length === 0" class="p-8 text-center">
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
          <h3 class="mt-2 text-sm font-medium text-gray-900">No files yet</h3>
          <p class="mt-1 text-sm text-gray-500">
            Upload your first file to get started
          </p>
        </div>

        <!-- Files List -->
        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="file in files"
            :key="file.id"
            class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <!-- File Icon -->
                <div class="file-icon">
                  <svg
                    v-if="isDocument(file)"
                    class="w-8 h-8 text-blue-600"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                    />
                  </svg>
                  <svg
                    v-else-if="isImage(file)"
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

                <!-- File Info -->
                <div>
                  <h3 class="text-sm font-medium text-gray-900">
                    {{ file.filename }}
                  </h3>
                  <p class="text-xs text-gray-500">
                    {{ formatFileSize(file.file_size) }} • {{ file.mime_type }}
                  </p>
                  <p class="text-xs text-gray-400">
                    Uploaded {{ formatDate(file.created_at) }}
                  </p>
                  <!-- Quill Status -->
                  <div v-if="file.original_format === 'docx'" class="mt-1">
                    <span
                      v-if="file.quill_content"
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                    >
                      <svg
                        class="w-3 h-3 mr-1"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      Quill Ready
                    </span>
                    <span
                      v-else
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
                    >
                      <svg
                        class="w-3 h-3 mr-1"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      Needs Conversion
                    </span>
                  </div>
                </div>
              </div>

              <!-- File Actions -->
              <div class="flex items-center space-x-2">
                <button
                  @click="viewFile(file)"
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path
                      fill-rule="evenodd"
                      d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{
                    file.original_format === 'docx'
                      ? file.quill_content
                        ? 'Edit with Quill'
                        : 'Convert & Edit'
                      : 'View'
                  }}
                </button>

                <button
                  @click="downloadFile(file)"
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"
                    />
                  </svg>
                  Download
                </button>

                <button
                  @click="shareFile(file)"
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"
                    />
                  </svg>
                  Share
                </button>

                <!-- Convert to Quill button for DOCX files -->
                <button
                  v-if="file.original_format === 'docx' && !file.quill_content"
                  @click="convertToQuill(file)"
                  :disabled="convertingFiles.has(file.id)"
                  class="inline-flex items-center px-3 py-2 border border-purple-300 shadow-sm text-sm leading-4 font-medium rounded-md text-purple-700 bg-white hover:bg-purple-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50"
                >
                  <svg
                    v-if="convertingFiles.has(file.id)"
                    class="animate-spin w-4 h-4 mr-2"
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
                  <svg
                    v-else
                    class="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                    />
                  </svg>
                  {{
                    convertingFiles.has(file.id)
                      ? 'Converting...'
                      : 'Convert to Quill'
                  }}
                </button>

                <!-- Edit with Quill button for converted files -->
                <button
                  v-if="file.original_format === 'docx' && file.quill_content"
                  @click="router.push(`/files/${file.id}`)"
                  class="inline-flex items-center px-3 py-2 border border-green-300 shadow-sm text-sm leading-4 font-medium rounded-md text-green-700 bg-white hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
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
                  Edit with Quill
                </button>

                <button
                  @click="deleteFile(file)"
                  class="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- File Viewer Modal -->
    <div
      v-if="showFileViewer"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div class="relative top-0 mx-auto p-5 w-full h-full">
        <div
          class="relative bg-white rounded-lg shadow-xl h-full flex flex-col"
        >
          <!-- Modal Header -->
          <div
            class="flex items-center justify-between p-4 border-b border-gray-200"
          >
            <h3 class="text-lg font-medium text-gray-900">File Viewer</h3>
            <button
              @click="closeFileViewer"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg
                class="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- File Viewer Content -->
          <div class="flex-1 overflow-hidden">
            <FileViewer
              v-if="selectedFile"
              :file-id="selectedFile.id"
              @close="closeFileViewer"
            />
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
  import { useRouter } from 'vue-router'
  // import { useAuthStore } from '../stores/auth' // Unused - commented out
  import api from '../services/api'
  import { filesApi } from '../services/api'
  import FileUpload from '../components/FileUpload.vue'
  import FileViewer from '../components/FileViewer.vue'

  export default {
    name: 'Files',
    components: {
      FileUpload,
      FileViewer,
    },
    setup() {
      const router = useRouter()
      const files = ref([])
      const loading = ref(false)
      const error = ref(null)
      const showFileViewer = ref(false)
      const showShareModal = ref(false)
      const selectedFile = ref(null)
      const shareToken = ref(null)
      const shareExpiration = ref(4)
      const fileToShare = ref(null)
      const convertingFiles = ref(new Set())

      // Methods
      const loadFiles = async () => {
        loading.value = true
        error.value = null

        try {
          const response = await api.get('/files/')
          files.value = response.data
        } catch (err) {
          error.value = err.response?.data?.detail || 'Failed to load files'
        } finally {
          loading.value = false
        }
      }

      const refreshFiles = () => {
        loadFiles()
      }

      const viewFile = file => {
        // For DOCX files with Quill content, route to FileEditor
        if (file.original_format === 'docx' && file.quill_content) {
          router.push(`/files/${file.id}`)
          return
        }

        // For unconverted DOCX files, route to FileEditor which will handle conversion
        if (file.original_format === 'docx' && !file.quill_content) {
          router.push(`/files/${file.id}`)
          return
        }

        // For other files, show the FileViewer modal
        selectedFile.value = file
        showFileViewer.value = true
      }

      const closeFileViewer = () => {
        showFileViewer.value = false
        selectedFile.value = null
      }

      const downloadFile = async file => {
        try {
          const response = await api.get(`/files/${file.id}/download`)
          const downloadUrl = response.data.download_url

          // Create temporary link and click it
          const link = document.createElement('a')
          link.href = downloadUrl
          link.download = file.filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        } catch (err) {
          alert('Failed to download file')
        }
      }

      const shareFile = file => {
        fileToShare.value = file
        showShareModal.value = true
        shareToken.value = null
      }

      const closeShareModal = () => {
        showShareModal.value = false
        fileToShare.value = null
        shareToken.value = null
      }

      const generateShareToken = async () => {
        try {
          const formData = new FormData()
          formData.append('expires_hours', shareExpiration.value)

          const response = await api.post(
            `/files/${fileToShare.value.id}/share`,
            formData
          )
          shareToken.value = response.data.share_token
        } catch (err) {
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

      const deleteFile = async file => {
        if (!confirm(`Are you sure you want to delete "${file.filename}"?`)) {
          return
        }

        try {
          await api.delete(`/files/${file.id}`)
          await loadFiles() // Refresh the list
        } catch (err) {
          console.error('Error deleting file:', err)
          alert('Failed to delete file')
        }
      }

      const convertToQuill = async file => {
        if (convertingFiles.value.has(file.id)) return

        convertingFiles.value.add(file.id)
        try {
          await filesApi.convertToQuill(file.id)

          // Refresh the file list to show updated status
          await loadFiles()

          // Show success message
          alert(
            'File converted to Quill format successfully! You can now edit it with rich text formatting.'
          )
        } catch (err) {
          console.error('Error converting file to Quill:', err)
          alert('Failed to convert file to Quill format. Please try again.')
        } finally {
          convertingFiles.value.delete(file.id)
        }
      }

      const isDocument = file => {
        if (!file?.mime_type) return false
        return (
          file.mime_type.includes('document') ||
          file.mime_type.includes('word') ||
          file.mime_type.includes('pdf') ||
          file.mime_type.includes('excel') ||
          file.mime_type.includes('powerpoint')
        )
      }

      const isImage = file => {
        if (!file?.mime_type) return false
        return file.mime_type.startsWith('image/')
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

      // Computed properties
      const shareUrl = computed(() => {
        if (!shareToken.value || !fileToShare.value) return ''
        return `${window.location.origin}/public/files/${fileToShare.value.id}?token=${shareToken.value}`
      })

      // Lifecycle
      onMounted(() => {
        loadFiles()
      })

      return {
        files,
        loading,
        error,
        convertingFiles,
        showFileViewer,
        showShareModal,
        selectedFile,
        shareToken,
        shareExpiration,
        fileToShare,
        shareUrl,
        loadFiles,
        refreshFiles,
        viewFile,
        closeFileViewer,
        downloadFile,
        shareFile,
        closeShareModal,
        generateShareToken,
        copyShareUrl,
        deleteFile,
        convertToQuill,
        isDocument,
        isImage,
        formatFileSize,
        formatDate,
        router,
      }
    },
  }
</script>

<style scoped>
  .files-page {
    @apply min-h-screen bg-gray-50;
  }

  .file-icon {
    @apply flex-shrink-0;
  }
</style>
