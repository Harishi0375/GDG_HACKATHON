// frontend/vite.config.js
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
// Remove 'path' import if no longer needed
// import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  // Keep the base path!
  base: '/GDG_HACKATHON/',

  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // Remove or comment out the entire 'build' section if 'dist' inside 'frontend' is the default,
  // OR explicitly set it:
  build: {
     outDir: 'dist', // Build inside frontend/dist
     emptyOutDir: true,
  }
})