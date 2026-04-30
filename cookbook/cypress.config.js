import { defineConfig } from "cypress"

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost/cookbook/",
    responseTimeout: 10000,
    pageLoadTimeout: 30000,
    video: false,
    setupNodeEvents(on) {
      const fs = require("fs")
      on("task", {
        log(message) {
          fs.appendFileSync("/tmp/cypress-debug.log", `${message}\n`)
          return null
        },
      })
    },
  },
})
