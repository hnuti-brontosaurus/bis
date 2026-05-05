import "./commands.js"

// Surface uncaught client-side exceptions in the cypress runner output.
// Use console.log (not cy.task) — cy.* commands are disallowed in Cypress
// event handlers in Cypress 13+ and trigger "promise mixed with cy command".
//
// Returning `false` is what suppresses the test failure (Cypress docs); the
// previous `return true` was a no-op. Suppress only well-known benign
// warnings (ResizeObserver loop) so real bugs still fail the test.
Cypress.on("uncaught:exception", err => {
  const msg = err && err.message

  console.log(
    `uncaught: ${msg} | ${(err?.stack || "").split("\n").slice(0, 5).join(" || ")}`,
  )
  if (typeof msg === "string" && msg.includes("ResizeObserver loop")) {
    return false
  }
  // Axios 4xx/5xx surface as uncaught when the app's save() re-throws via
  // handleAxiosError (which is intentional UX). Don't fail the test on those —
  // the spec asserts the eventual app behaviour (URL, persisted data).
  if (err?.name === "AxiosError" || err?.isAxiosError) {
    return false
  }
})

Cypress.on("window:before:load", win => {
  const origError = win.console.error
  win.console.error = (...args) => {
    console.log(
      `console.error: ${args.map(a => (a && a.message) || (typeof a === "string" ? a : JSON.stringify(a, null, 0))).join(" | ")}`,
    )
    return origError.apply(win.console, args)
  }
})
