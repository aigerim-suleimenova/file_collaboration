<template>
  <div class="file-upload">
    <!-- Upload Area -->
    <div
      class="upload-area"
      :class="{ 'drag-over': isDragOver, uploading: uploading }"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        class="hidden"
        @change="handleFileSelect"
        accept="*/*"
      />

      <!-- Upload Icon -->
      <div class="upload-icon">
        <svg
          v-if="!uploading"
          class="w-12 h-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <div
          v-else
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
        ></div>
      </div>

      <!-- Upload Text -->
      <div class="upload-text">
        <h3 v-if="!uploading" class="text-lg font-medium text-gray-900">
          {{ isDragOver ? 'Drop files here' : 'Upload files' }}
        </h3>
        <p v-if="!uploading" class="text-sm text-gray-500">
          {{
            isDragOver
              ? 'Release to upload'
              : 'Drag and drop or click to select'
          }}
        </p>
        <p v-if="!uploading" class="text-xs text-blue-600 mt-1">
          💡 DOCX files will be automatically converted to Quill format for rich
          text editing
        </p>
        <p v-else class="text-sm text-gray-500">Uploading...</p>
      </div>

      <!-- Upload Button -->
      <button
        v-if="!uploading"
        type="button"
        class="upload-button"
        @click.stop="triggerFileInput"
      >
        Select Files
      </button>
    </div>

    <!-- File List -->
    <div v-if="files.length > 0" class="file-list mt-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Selected Files</h3>
      <div class="space-y-3">
        <div
          v-for="(file, index) in files"
          :key="index"
          class="file-item bg-white border border-gray-200 rounded-lg p-4"
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
                <p class="text-sm font-medium text-gray-900">{{ file.name }}</p>
                <p class="text-xs text-gray-500">
                  {{ formatFileSize(file.size) }}
                </p>
              </div>
            </div>

            <!-- Remove Button -->
            <button
              @click="removeFile(index)"
              class="text-red-400 hover:text-red-600"
              :disabled="uploading"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>

          <!-- Upload Progress -->
          <div v-if="file.uploading" class="mt-3">
            <div class="flex items-center space-x-2">
              <div class="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${file.progress || 0}%` }"
                ></div>
              </div>
              <span class="text-xs text-gray-500"
                >{{ file.progress || 0 }}%</span
              >
            </div>
          </div>

          <!-- Upload Status -->
          <div v-if="file.status" class="mt-2">
            <span
              v-if="file.status === 'success'"
              class="inline-flex items-center text-xs text-green-600"
            >
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clip-rule="evenodd"
                />
              </svg>
              Uploaded successfully
            </span>
            <span
              v-else-if="file.status === 'error'"
              class="inline-flex items-center text-xs text-red-600"
            >
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clip-rule="evenodd"
                />
              </svg>
              {{ file.error || 'Upload failed' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Upload All Button -->
      <div class="mt-6">
        <button
          @click="uploadAllFiles"
          :disabled="uploading || !hasFilesToUpload"
          class="upload-all-button"
        >
          <svg
            v-if="!uploading"
            class="w-5 h-5 mr-2"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"
              clip-rule="evenodd"
            />
          </svg>
          <span v-if="!uploading">Upload All Files</span>
          <span v-else>Uploading...</span>
        </button>
      </div>
    </div>

    <!-- Success Message -->
    <div
      v-if="uploadSuccess"
      class="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg"
    >
      <div class="flex items-center">
        <svg
          class="w-5 h-5 text-green-400 mr-2"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clip-rule="evenodd"
          />
        </svg>
        <span class="text-sm text-green-800">Files uploaded successfully!</span>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed } from 'vue'
  import api from '../services/api'

  export default {
    name: 'FileUpload',
    emits: ['upload-complete'],
    setup(props, { emit }) {
      const fileInput = ref(null)
      const files = ref([])
      const uploading = ref(false)
      const isDragOver = ref(false)
      const uploadSuccess = ref(false)

      // Computed properties
      const hasFilesToUpload = computed(() => {
        return files.value.some(file => !file.uploading && !file.status)
      })

      // Methods
      const triggerFileInput = () => {
        fileInput.value?.click()
      }

      const handleFileSelect = event => {
        const selectedFiles = Array.from(event.target.files)
        addFiles(selectedFiles)
        // Reset input value to allow selecting the same file again
        event.target.value = ''
      }

      const handleDrop = event => {
        event.preventDefault()
        isDragOver.value = false

        const droppedFiles = Array.from(event.dataTransfer.files)
        addFiles(droppedFiles)
      }

      const handleDragOver = event => {
        event.preventDefault()
        isDragOver.value = true
      }

      const handleDragLeave = event => {
        event.preventDefault()
        isDragOver.value = false
      }

      const addFiles = newFiles => {
        const validFiles = newFiles.filter(() => {
          // Add any file validation here if needed
          return true
        })

        const filesWithMetadata = validFiles.map(file => ({
          file,
          name: file.name,
          size: file.size,
          type: file.type,
          uploading: false,
          progress: 0,
          status: null,
          error: null,
        }))

        files.value.push(...filesWithMetadata)
      }

      const removeFile = index => {
        files.value.splice(index, 1)
      }

      const uploadAllFiles = async () => {
        if (uploading.value || !hasFilesToUpload.value) return

        uploading.value = true
        uploadSuccess.value = false

        try {
          const uploadPromises = files.value
            .filter(file => !file.uploading && !file.status)
            .map(file => uploadFile(file))

          await Promise.all(uploadPromises)

          uploadSuccess.value = true
          emit('upload-complete')

          // Clear success message after 3 seconds
          setTimeout(() => {
            uploadSuccess.value = false
          }, 3000)
        } catch (error) {
          console.error('Upload failed:', error)
        } finally {
          uploading.value = false
        }
      }

      const uploadFile = async fileItem => {
        fileItem.uploading = true
        fileItem.progress = 0
        fileItem.status = null
        fileItem.error = null

        try {
          const formData = new FormData()
          formData.append('file', fileItem.file)

          const response = await api.post('/files/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: progressEvent => {
              if (progressEvent.total) {
                fileItem.progress = Math.round(
                  (progressEvent.loaded * 100) / progressEvent.total
                )
              }
            },
          })

          fileItem.status = 'success'
          fileItem.uploadedFile = response.data
        } catch (error) {
          fileItem.status = 'error'
          fileItem.error = error.response?.data?.detail || 'Upload failed'
          console.error('File upload error:', error)
        } finally {
          fileItem.uploading = false
        }
      }

      const isDocument = file => {
        return (
          file.type.includes('document') ||
          file.type.includes('word') ||
          file.type.includes('pdf') ||
          file.type.includes('excel') ||
          file.type.includes('powerpoint')
        )
      }

      const isImage = file => {
        return file.type.startsWith('image/')
      }

      const formatFileSize = bytes => {
        if (!bytes) return '0 Bytes'
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(1024))
        return (
          Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i]
        )
      }

      // Lifecycle - removed onMounted since it's not imported
      // onMounted(() => {
      //   // Add drag and drop event listeners to window
      //   window.addEventListener('dragover', e => e.preventDefault())
      //   window.addEventListener('drop', e => e.preventDefault())
      // })

      return {
        fileInput,
        files,
        uploading,
        isDragOver,
        uploadSuccess,
        hasFilesToUpload,
        triggerFileInput,
        handleFileSelect,
        handleDrop,
        handleDragOver,
        handleDragLeave,
        removeFile,
        uploadAllFiles,
        isDocument,
        isImage,
        formatFileSize,
      }
    },
  }
</script>

<style scoped>
  .file-upload {
    @apply w-full;
  }

  .upload-area {
    @apply border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-colors duration-200;
  }

  .upload-area:hover {
    @apply border-gray-400 bg-gray-50;
  }

  .upload-area.drag-over {
    @apply border-blue-400 bg-blue-50;
  }

  .upload-area.uploading {
    @apply border-gray-200 bg-gray-50 cursor-not-allowed;
  }

  .upload-icon {
    @apply mx-auto mb-4;
  }

  .upload-text {
    @apply mb-6;
  }

  .upload-button {
    @apply inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500;
  }

  .upload-button:hover:not(:disabled) {
    @apply bg-blue-700;
  }

  .upload-button:disabled {
    @apply opacity-50 cursor-not-allowed;
  }

  .upload-all-button {
    @apply inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed;
  }

  .file-item {
    @apply transition-all duration-200;
  }

  .file-icon {
    @apply flex-shrink-0;
  }
</style>
