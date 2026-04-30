import "./commands.js"

// Surface uncaught client-side exceptions in the cypress runner output.
Cypress.on("uncaught:exception", err => {
  cy.task(
    "log",
    `uncaught: ${err && err.message} | ${(err?.stack || "").split("\n").slice(0, 5).join(" || ")}`,
    { log: false },
  )
  return true
})

Cypress.on("window:before:load", win => {
  const origError = win.console.error
  win.console.error = (...args) => {
    try {
      cy.task(
        "log",
        `console.error: ${args.map(a => (a && a.message) || (typeof a === "string" ? a : JSON.stringify(a, null, 0))).join(" | ")}`,
        { log: false },
      )
    } catch (e) {
      void e
    }
    return origError.apply(win.console, args)
  }
})
