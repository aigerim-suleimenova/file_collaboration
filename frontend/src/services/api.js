import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Request interceptor to add auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  response => response,
  error => {
    // Handle network errors gracefully
    if (!error.response) {
      console.warn('Network error:', error.message)
      return Promise.reject(error)
    }

    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API methods
export const authApi = {
  login: (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    return api.post('/login/access-token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  register: userData => {
    return api.post('/users/signup', userData)
  },

  getCurrentUser: () => {
    return api.get('/users/me')
  },
}

// Files API methods
export const filesApi = {
  getFiles: () => {
    return api.get('/files')
  },

  getFile: fileId => {
    return api.get(`/files/${fileId}`)
  },

  createFile: fileData => {
    return api.post('/files', fileData)
  },

  updateFile: (fileId, fileData) => {
    return api.put(`/files/${fileId}`, fileData)
  },

  deleteFile: fileId => {
    return api.delete(`/files/${fileId}`)
  },

  // Create a short-lived share token (owner only)
  createShareToken: fileId => {
    return api.post(`/files/${fileId}/share`)
  },

  // Read-only public access via share token
  getPublicFile: (fileId, token) => {
    return api.get(`/public/files/${fileId}`, { params: { token } })
  },

  // Document conversion endpoints
  convertToQuill: fileId => {
    return api.post(`/files/${fileId}/convert-existing-to-quill`)
  },

  updateQuillContent: (fileId, quillContent) => {
    const formData = new FormData()
    formData.append('quill_content', quillContent)
    return api.post(`/files/${fileId}/update-quill-content`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  convertToDocx: fileId => {
    return api.post(`/files/${fileId}/convert-to-docx`)
  },

  uploadFile: (file, description = '') => {
    const formData = new FormData()
    formData.append('file', file)
    if (description) {
      formData.append('description', description)
    }
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export default api
