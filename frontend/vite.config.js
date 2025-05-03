// frontend/vite.config.js
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'path' // Import the path module

// https://vite.dev/config/
export default defineConfig({
  // Keep the base path for correct asset loading on GitHub Pages
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
  build: {
    // Output the build to a 'docs' folder in the repository root
    // path.resolve goes from the current file (__dirname) up two levels (to GDG_HACKATHON root) and then into 'docs'
    outDir: path.resolve(__dirname, '../../docs'),
    emptyOutDir: true, // Recommended: Clears the docs folder before each build
  }
})
