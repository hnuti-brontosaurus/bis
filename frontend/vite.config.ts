import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import svgr from 'vite-plugin-svgr'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig(({mode}) => ({
  plugins: [react(), tsconfigPaths(), svgr()],
  server: { host: '0.0.0.0', port: 3000, allowedHosts: ['frontend'] },
  build: { outDir: 'build' },
  assetsInclude: ['**/*.xlsx', '**/*.pdf'],
  css: {
    preprocessorOptions: {
      scss: { includePaths: ['src'] },
    },
    modules: mode === 'development' ? {
      generateScopedName: '[name]__[local]__[hash:base64:5]'
    } : {}
  },
  // safety net for third-party libs that still reference process.env
  define: { 'process.env': {} },
}))
