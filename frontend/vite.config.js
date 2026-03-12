import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // 允许局域网访问
    port: 5173,       // 前端端口
    strictPort: true, // 端口被占用时不自动尝试其他端口
    open: false       // 不自动打开浏览器
  }
})
