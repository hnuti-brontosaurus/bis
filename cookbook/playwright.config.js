import { defineConfig, devices } from "@playwright/test"

export default defineConfig({
  testDir: "./e2e",
  globalSetup: "./e2e/global-setup.js",
  // Each spec owns the recipe it mutates (see the `recipe` fixture), so specs
  // do not collide even though they share one backend.
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.PW_WORKERS ? Number(process.env.PW_WORKERS) : "50%",
  reporter: [["list"], ["html", { open: "never" }]],
  outputDir: "test-results",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL: process.env.PW_BASE_URL ?? "http://nginx",
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
})
