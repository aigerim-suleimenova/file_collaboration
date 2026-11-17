<template>
  <div class="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-sm">
      <h2
        class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900"
      >
        Register to your account
      </h2>
    </div>

    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
      <form method="POST" class="space-y-6" @submit.prevent="handleRegister">
        <div>
          <label
            for="full_name"
            class="block text-sm/6 font-medium text-gray-900"
            >Full Name</label
          >
          <div class="mt-2">
            <input
              id="full_name"
              v-model="form.full_name"
              type="text"
              name="full_name"
              required
              autocomplete="name"
              class="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-base text-gray-900 placeholder-gray-400 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
          <p v-if="errors.full_name" class="mt-1 text-sm text-red-600">
            {{ errors.full_name }}
          </p>
        </div>

        <div>
          <label for="email" class="block text-sm/6 font-medium text-gray-900"
            >Email address</label
          >
          <div class="mt-2">
            <input
              id="email"
              v-model="form.email"
              type="email"
              name="email"
              required
              autocomplete="email"
              class="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-base text-gray-900 placeholder-gray-400 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
          <p v-if="errors.email" class="mt-1 text-sm text-red-600">
            {{ errors.email }}
          </p>
        </div>

        <div>
          <div class="flex items-center justify-between">
            <label
              for="password"
              class="block text-sm/6 font-medium text-gray-900"
              >Password</label
            >
          </div>
          <div class="mt-2">
            <input
              id="password"
              v-model="form.password"
              type="password"
              name="password"
              required
              autocomplete="new-password"
              class="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-base text-gray-900 placeholder-gray-400 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
          <p v-if="errors.password" class="mt-1 text-sm text-red-600">
            {{ errors.password }}
          </p>
        </div>

        <div>
          <div class="flex items-center justify-between">
            <label
              for="confirmPassword"
              class="block text-sm/6 font-medium text-gray-900"
              >Confirm Password</label
            >
          </div>
          <div class="mt-2">
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              name="confirmPassword"
              required
              autocomplete="new-password"
              class="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-base text-gray-900 placeholder-gray-400 focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
          <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">
            {{ errors.confirmPassword }}
          </p>
        </div>

        <div>
          <button
            type="submit"
            class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Sign up
          </button>
        </div>
      </form>
      <p class="mt-10 text-center text-sm/6 text-gray-500">
        <router-link
          to="/login"
          class="font-semibold text-indigo-600 hover:text-indigo-500"
        >
          Back to Sign in
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
    name: 'Register',
    setup() {
      const router = useRouter()
      const authStore = useAuthStore()

      const form = reactive({
        email: '',
        password: '',
        confirmPassword: '',
        full_name: '',
      })

      const errors = reactive({
        email: '',
        password: '',
        confirmPassword: '',
        full_name: '',
      })

      const validateForm = () => {
        errors.email = ''
        errors.password = ''
        errors.confirmPassword = ''
        errors.full_name = ''

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

        if (!form.confirmPassword) {
          errors.confirmPassword = 'Please confirm your password'
        } else if (form.password !== form.confirmPassword) {
          errors.confirmPassword = 'Passwords do not match'
        }

        if (!form.full_name) {
          errors.full_name = 'Full name is required'
        }

        return (
          !errors.email &&
          !errors.password &&
          !errors.confirmPassword &&
          !errors.full_name
        )
      }

      const handleRegister = async () => {
        if (!validateForm()) return

        const userData = {
          email: form.email,
          password: form.password,
          full_name: form.full_name,
        }

        const result = await authStore.register(userData)

        if (result.success) {
          router.push('/login')
        }
      }

      return {
        form,
        errors,
        authStore,
        handleRegister,
      }
    },
  }
</script>
