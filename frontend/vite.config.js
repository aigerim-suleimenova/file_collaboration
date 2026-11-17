import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Where the dev server forwards API and collaboration traffic. docker-compose sets
// this to the backend service; outside Docker the backend runs on localhost:8000.
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000, // default vite port
    proxy: {
      '/api/v1': {
        target: proxyTarget,
        changeOrigin: true,
        ws: true
      },
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1')
      }
    }
  }
})
