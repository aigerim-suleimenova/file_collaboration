import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (email, password) => {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.login(email, password)
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)

      // Get user info
      const userResponse = await authApi.getCurrentUser()
      user.value = userResponse.data

      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const register = async userData => {
    loading.value = true
    error.value = null

    try {
      await authApi.register(userData)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const getCurrentUser = async () => {
    if (!token.value) return

    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
    } catch (err) {
      console.warn('Failed to get current user:', err.message)
      // Only logout if it's a 401 error (unauthorized)
      if (err.response?.status === 401) {
        logout()
      }
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    getCurrentUser,
  }
})
