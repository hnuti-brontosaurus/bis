/// <reference types="cypress" />

const BACKEND_CONTAINER = Cypress.env("BACKEND_CONTAINER") || "bis-backend"
const TEST_USER_EMAIL = Cypress.env("TEST_USER_EMAIL") || "lamanchy@gmail.com"

/**
 * Returns the id of an editable recipe owned by the logged-in chef whose
 * photo file actually exists on disk. Creates one if none exists yet —
 * keeps the spec runnable against either the dev DB or a clean
 * `testing_db` seed.
 */
const ensureEditableRecipe = chefId =>
  cy
    .exec(
      `docker exec ${BACKEND_CONTAINER} python manage.py shell -c "` +
        `import os; from cookbook.models.recipes import Recipe; ` +
        `cands=[r for r in Recipe.objects.filter(chef_id=${chefId}) ` +
        `if r.photo and os.path.exists(r.photo.path)]; ` +
        `print(cands[0].id if cands else '')"`,
    )
    .then(({ stdout }) => {
      const id = parseInt(stdout.trim().split(/\s+/).pop(), 10)
      if (id >= 1) return id
      return cy
        .exec(
          `docker exec ${BACKEND_CONTAINER} python manage.py shell -c "` +
            `from io import BytesIO; from PIL import Image; ` +
            `from django.core.files.uploadedfile import SimpleUploadedFile; ` +
            `from cookbook.models.recipes import Recipe; ` +
            `from cookbook_categories.models import RecipeDifficulty, RecipeRequiredTime; ` +
            `d, _ = RecipeDifficulty.objects.get_or_create(slug='easy', defaults={'name': 'easy', 'order': 1}); ` +
            `t, _ = RecipeRequiredTime.objects.get_or_create(slug='fast', defaults={'name': 'fast', 'order': 1}); ` +
            `buf = BytesIO(); Image.new('RGB', (8, 8), 'red').save(buf, format='PNG'); ` +
            `f = SimpleUploadedFile('seed.png', buf.getvalue(), content_type='image/png'); ` +
            `r = Recipe.objects.create(name='Cypress seed', chef_id=${chefId}, difficulty=d, required_time=t, photo=f, intro='intro', sources='.'); ` +
            `print(r.id)"`,
        )
        .then(({ stdout: out }) => parseInt(out.trim().split(/\s+/).pop(), 10))
    })

describe("cookbook smoke", () => {
  beforeEach(() => {
    // Pre-seed localStorage before any page load so the SPA boots authenticated.
    cy.session(`chef-${TEST_USER_EMAIL}`, () => {
      // cy.session needs a visit to attach the storage to an origin.
      cy.visit("/")
      cy.loginAsChef(TEST_USER_EMAIL)
    })
    // Drop pinia's persisted store cache between specs so a stale shape from
    // a previous run doesn't leak in.
    cy.window().then(win => {
      Object.keys(win.localStorage)
        .filter(k => k.startsWith("cookbook:"))
        .forEach(k => win.localStorage.removeItem(k))
    })
  })

  it("renders recipes list and a recipe detail", () => {
    const auth = JSON.parse(window.localStorage.getItem("auth") || "{}")
    ensureEditableRecipe(auth.chef?.id ?? 0).then(() => {
      cy.visit("/recipes/")
      cy.contains("Recepty").should("exist")
      // Wait for recipe cards to render then click the first.
      cy.get(".n-card", { timeout: 10000 }).first().click()
      cy.location("pathname").should("match", /\/recipe\/\d+\//)
      cy.contains("Autorstvo").should("be.visible")
    })
  })

  it("opens edit form, mutates description, and persists", () => {
    cy.task("log", "TEST START")
    const auth = JSON.parse(window.localStorage.getItem("auth") || "{}")
    const token = auth.user?.token

    ensureEditableRecipe(auth.chef?.id ?? 0).then(recipeId => {
      cy.task("log", `recipeId=${recipeId}`)
      expect(recipeId, "owned recipe with photo").to.be.gte(1)

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

    // Reference token to avoid lint complaining about unused destructure.
    expect(token).to.be.a("string")
  })

  it("renders chefs view", () => {
    cy.visit("/chefs/")
    cy.contains("Kuchařstvo").should("exist")
    cy.get(".n-card").its("length").should("be.gte", 1)
  })
})
