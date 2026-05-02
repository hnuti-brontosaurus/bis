/// <reference types="cypress" />

const TEST_USER_EMAIL = Cypress.env("TEST_USER_EMAIL") || "lamanchy@gmail.com"
const API_BASE_URL = Cypress.env("API_BASE_URL") || "http://localhost/api/cookbook"

// Read the whoami payload out of the pinia-persisted auth store.
const getStoredAuth = () => {
  const raw = window.localStorage.getItem("cookbook:auth:v1")
  return raw ? (JSON.parse(raw).me ?? {}) : {}
}

// Returns the id of a recipe owned by the logged-in chef. The seed
// (`testing_db cookbook`) guarantees one exists with a photo on disk, so
// this is just a list call against the API the SPA itself uses.
const getOwnedRecipeId = (chefId, token) =>
  cy
    .request({
      url: `${API_BASE_URL}/recipes/?chef=${chefId}`,
      headers: { Authorization: `Token ${token}` },
    })
    .then(({ body }) => {
      expect(body.results, "owned recipes").to.have.length.gte(1)
      return body.results[0].id
    })

describe("cookbook smoke", () => {
  beforeEach(() => {
    // Pre-seed localStorage before any page load so the SPA boots authenticated.
    // Session id tracks the auth-store key version so a cached session from
    // the pre-pinia-store world doesn't get restored.
    cy.session(`chef-${TEST_USER_EMAIL}:auth-v1`, () => {
      // cy.session needs a visit to attach the storage to an origin.
      cy.visit("/")
      cy.loginAsChef(TEST_USER_EMAIL)
    })
    // Drop pinia's persisted store cache between specs so a stale shape from
    // a previous run doesn't leak in.
    // Auth is also cookbook-prefixed (cookbook:auth:v1) but must survive the
    // cleanup — it's what cy.session just restored.
    cy.window().then(win => {
      Object.keys(win.localStorage)
        .filter(k => k.startsWith("cookbook:") && k !== "cookbook:auth:v1")
        .forEach(k => win.localStorage.removeItem(k))
    })
  })

  it("renders recipes list and a recipe detail", () => {
    cy.visit("/recipes/")
    cy.contains("Recepty").should("exist")
    // Wait for recipe cards to render then click the first.
    cy.get(".n-card", { timeout: 10000 }).first().click()
    cy.location("pathname").should("match", /\/recipe\/\d+\//)
    cy.contains("Autorstvo").should("be.visible")
  })

  it("opens edit form, mutates description, and persists", () => {
    cy.task("log", "TEST START")
    const auth = getStoredAuth()
    const token = auth.user?.token

    getOwnedRecipeId(auth.chef?.id, token).then(recipeId => {
      cy.task("log", `recipeId=${recipeId}`)

      cy.intercept("**/api/cookbook/**").as("api")
      cy.visit(`/recipe/${recipeId}/edit/`, {
        onBeforeLoad(win) {
          win.addEventListener("error", e => {
            cy.task("log", `window.error: ${e.message} at ${e.filename}:${e.lineno}`)
          })
          win.addEventListener("unhandledrejection", e => {
            cy.task("log", `unhandled: ${e.reason?.message || e.reason}`)
          })
          const origError = win.console.error
          win.console.error = (...args) => {
            try {
              cy.task("log", `console.error: ${args.map(String).join(" || ")}`, {
                log: false,
              })
            } catch (e) {
              void e
            }
            origError.apply(win.console, args)
          }
        },
      })
      cy.location("pathname").should("equal", `/cookbook/recipe/${recipeId}/edit/`)

      const tag = `cypress-${Date.now()}`
      // Wait for the form to render its textareas (recipe data loaded).
      cy.get("textarea", { timeout: 15000 }).should("have.length.gte", 1)
      cy.get("textarea")
        .first()
        .then($el => {
          const original = `${$el.val()}`.replace(/\s+$/, "")
          // Avoid newlines: the form has @keydown.enter="save" which would
          // submit prematurely. Append the tag with a single space.
          cy.wrap($el).clear().type(`${original} ${tag}`, { delay: 0 })
        })

      cy.contains("button", "Uložit").click({ force: true })
      cy.location("pathname", { timeout: 15000 }).should(
        "equal",
        `/cookbook/recipe/${recipeId}/`,
      )

      cy.reload()
      cy.contains(tag).should("exist")
    })
  })

  it("renders chefs view", () => {
    cy.visit("/chefs/")
    cy.contains("Kuchařstvo").should("exist")
    cy.get(".n-card").its("length").should("be.gte", 1)
  })
})
