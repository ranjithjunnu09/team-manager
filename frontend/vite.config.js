import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  preview: {
    allowedHosts: [
      "tranquil-benevolence-production-76d1.up.railway.app"
    ]
  }
})