import { defineConfig } from "cypress"

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost/cookbook/",
    responseTimeout: 10000,
    pageLoadTimeout: 30000,
    video: false,
    setupNodeEvents(on) {
      const fs = require("fs")
      const { execSync } = require("node:child_process")
      // Seed cookbook test fixtures before every spec. `testing_db cookbook`
      // is idempotent (update_or_create / get_or_create), so re-running per
      // spec is cheap and keeps `cypress open` honest. `before:spec` fires in
      // both `cypress run` and `cypress open`, unlike `before:run` which only
      // fires in run mode.
      on("before:spec", () => {
        const container = process.env.BACKEND_CONTAINER || "bis-test-backend"
        execSync(`docker exec ${container} python manage.py testing_db cookbook`, {
          stdio: "inherit",
        })
      })
      on("task", {
        log(message) {
          fs.appendFileSync("/tmp/cypress-debug.log", `${message}\n`)
          return null
        },
      })
    },
  },
})
