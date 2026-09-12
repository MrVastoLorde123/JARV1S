import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api/world': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
      },
      '/api/command': {
        target: 'http://127.0.0.1:8766',
        changeOrigin: true,
      },
    },
  },
});
