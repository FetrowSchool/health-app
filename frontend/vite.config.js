import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: { rollupOptions: { input: { main: 'index.html', voiceDiagnostic: 'voice-diagnostic.html' } } },
  server: {
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
