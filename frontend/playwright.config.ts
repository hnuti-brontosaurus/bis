import { defineConfig, devices } from '@playwright/test'

// eslint-disable-next-line import/no-default-export
export default defineConfig({
  testDir: './e2e',
  // Every spec stubs its own API calls, so nothing is shared between them.
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.PW_WORKERS ? Number(process.env.PW_WORKERS) : '50%',
  reporter: [['list'], ['html', { open: 'never' }]],
  outputDir: 'test-results',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: process.env.PW_BASE_URL ?? 'http://nginx',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})
