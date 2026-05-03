import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  preview: {
    allowedHosts: [
      "tranquil-benevolence-production-dd44.up.railway.app"
    ]
  }
})