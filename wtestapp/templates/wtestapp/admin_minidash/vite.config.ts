import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    host: 'localhost',
    port: 5174,
    proxy: {
      // Proxy API calls to Django so the dashboard at http://localhost:5174 can fetch live data
      '/api': 'http://127.0.0.1:8000',
      // Optional: serve media/static through Django during dev if needed by the app
      '/media': 'http://127.0.0.1:8000',
      '/static': 'http://127.0.0.1:8000',
    },
  },
});
