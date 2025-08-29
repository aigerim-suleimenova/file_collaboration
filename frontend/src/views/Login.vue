<template>
  <div class="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-sm">
      <h2
        class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900"
      >
        Sign in to your account
      </h2>
    </div>

    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
      <form @submit.prevent="handleLogin" method="POST" class="space-y-6">
        <div>
          <label for="email" class="block text-sm/6 font-medium text-gray-900"
            >Email address</label
          >
          <div class="mt-2">
            <input
              v-model="form.email"
              id="email"
              type="email"
              name="email"
              required
              autocomplete="email"
              class="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-base text-gray-900 placeholder-gray-400 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between">
            <label
              for="password"
              class="block text-sm/6 font-medium text-gray-900"
              >Password</label
            >
            <!--
          <div class="text-sm">
            <a href="#" class="font-semibold text-indigo-600 hover:text-indigo-500">Forgot password?</a>
          </div>
                -->
          </div>

          <div class="mt-2">
            <input
              v-model="form.password"
              id="password"
              type="password"
              name="password"
              required
              autocomplete="current-password"
              class="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-base text-gray-900 placeholder-gray-400 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Sign in
          </button>
        </div>
      </form>

      <p class="mt-10 text-center text-sm/6 text-gray-500">
        Not a member?
        <router-link
          to="/register"
          class="font-semibold text-indigo-600 hover:text-indigo-500"
        >
          Register
        </router-link>
      </p>
    </div>
  </div>
</template>

<script>
  import { reactive } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '../stores/auth'
  export default {
    name: 'Login',
    setup() {
      const router = useRouter()
      const authStore = useAuthStore()

      const form = reactive({
        email: '',
        password: '',
      })

      const errors = reactive({
        email: '',
        password: '',
      })

      const validateForm = () => {
        errors.email = ''
        errors.password = ''

        if (!form.email) {
          errors.email = 'Email is required'
        } else if (!/\S+@\S+\.\S+/.test(form.email)) {
          errors.email = 'Email is invalid'
        }

        if (!form.password) {
          errors.password = 'Password is required'
        } else if (form.password.length < 8) {
          errors.password = 'Password must be at least 8 characters'
        }

        return !errors.email && !errors.password
      }

      const handleLogin = async () => {
        if (!validateForm()) return

        const result = await authStore.login(form.email, form.password)

        if (result.success) {
          router.push('/')
        }
      }

      return {
        form,
        errors,
        authStore,
        handleLogin,
      }
    },
  }
</script>
