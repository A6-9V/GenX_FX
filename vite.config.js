import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import * as path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
export default defineConfig({
    plugins: [react()],
    root: 'client',
    build: {
        outDir: '../services/server/public',
        emptyOutDir: true,
    },
    server: {
        host: '0.0.0.0',
        port: 5173,
        proxy: {
            '/api/v1': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/api': {
                target: 'http://localhost:5000',
                changeOrigin: true
            },
            '/health': {
                target: 'http://localhost:5000',
                changeOrigin: true
            },
            '/socket.io': {
                target: 'http://localhost:5000',
                changeOrigin: true,
                ws: true
            }
        }
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './client/src')
        }
    }
});
