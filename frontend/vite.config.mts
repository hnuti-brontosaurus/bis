import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import svgr from 'vite-plugin-svgr'
import tsconfigPaths from 'vite-tsconfig-paths'
import checker from 'vite-plugin-checker'

export default defineConfig(({mode}) => ({
  // The e2e stack type-checks in its own job (`make check_frontend`), so running
  // tsc inside the dev server too only steals CPU from the Playwright browsers.
  plugins: [react(), tsconfigPaths(), svgr(),
    ...(process.env.VITE_E2E ? [] : [checker({typescript: true})])],
  server: { host: '0.0.0.0', port: 3000, allowedHosts: ['frontend', 'nginx'] },
  build: { outDir: 'build', target: 'es2021' },
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
  test: {
    globals: true,
    environment: 'node',
    // Playwright specs are also *.spec.ts; keep vitest to the unit tests.
    include: ['src/**/__tests__/**/*.{test,spec}.{ts,tsx}'],
  },
}))
