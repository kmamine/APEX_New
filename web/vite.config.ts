import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Dev server proxies /api to the FastAPI backend so the browser stays same-origin.
// Override the backend target with VITE_API_TARGET (e.g. if :8000 is taken).
const apiTarget = process.env.VITE_API_TARGET || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    allowedHosts: true,
    proxy: {
      '/api': { target: apiTarget, changeOrigin: true },
    },
  },
  build: { outDir: 'dist', sourcemap: true },
});
