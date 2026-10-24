import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// base: './' — чтобы сборка открывалась и на GitHub Pages, и с любого хостинга
export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
})
