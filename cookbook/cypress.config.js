// Bare config object (no `defineConfig` import) so cypress is not required
// in cookbook/node_modules — the runner image (cypress/included) provides it.
export default {
  allowCypressEnv: false,
  e2e: {
    baseUrl: "http://nginx/cookbook/",
    responseTimeout: 10000,
    pageLoadTimeout: 30000,
    video: false,
    setupNodeEvents(on) {
      const fs = require("fs")
      // Seed cookbook test fixtures before every spec via the backend's
      // TEST-only HTTP endpoint. `testing_db cookbook` is idempotent so
      // re-running per spec is cheap and keeps `cypress open` honest.
      // `before:spec` fires in both `cypress run` and `cypress open`,
      // unlike `before:run` which only fires in run mode.
      on("before:spec", async () => {
        const seedUrl =
          process.env.SEED_URL || "http://nginx/api/cookbook/testing/seed/"
        const res = await fetch(seedUrl, { method: "POST" })
        if (!res.ok) {
          throw new Error(`seed failed: ${res.status} ${await res.text()}`)
        }
      })
      on("task", {
        log(message) {
          fs.appendFileSync("/tmp/cypress-debug.log", `${message}\n`)
          return null
        },
      })
    },
  },
}
