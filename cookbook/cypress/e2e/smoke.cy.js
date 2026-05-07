/// <reference types="cypress" />

const TEST_USER_EMAIL = "test@test.local"
const API_BASE_URL = "http://nginx/api/cookbook"

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

  it("adds an ingredient, step, and tip via the form and persists them", () => {
    // Regression for #order-not-filled: the dynamic-input creates rows as
    // `{}`, so the frontend must inject `order` from list position before
    // PATCH or the backend rejects RecipeIngredient/RecipeStep.
    const auth = getStoredAuth()
    const token = auth.user?.token

    getOwnedRecipeId(auth.chef?.id, token).then(recipeId => {
      // Reset the seeded recipe to a known clean slate (no children) so
      // the section dynamic-inputs render their empty-state create button.
      cy.request({
        method: "PATCH",
        url: `${API_BASE_URL}/recipes/${recipeId}/`,
        headers: { Authorization: `Token ${token}` },
        body: { ingredients: [], steps: [], tips: [] },
      })

      const tag = `cypress-${Date.now()}`
      const stepName = `step-${tag}`
      const tipName = `tip-${tag}`
      const tipDesc = `tip-desc-${tag}`

      cy.visit(`/recipe/${recipeId}/edit/`)
      cy.location("pathname").should("equal", `/cookbook/recipe/${recipeId}/edit/`)
      cy.get("textarea", { timeout: 15000 }).should("have.length.gte", 1)

      // Helper: expand a collapsed section by its header text. The header
      // is an <h6> wrapped inside .n-collapse-item; click it to expand,
      // then scope subsequent interactions to that collapse item.
      const openSection = title =>
        cy
          .contains("h6", title, { timeout: 10000 })
          .click({ force: true })
          .closest(".n-collapse-item")

      // Ingredience: empty list → click the empty-state create button,
      // then drive the row's three inputs (ingredient select, amount,
      // unit select). Naive UI teleports the dropdown menu out of the
      // collapse-item, so option clicks must scope to the *visible*
      // .n-base-select-menu — not just .n-base-select-option, which
      // also matches stale hidden options from the previous dropdown.
      const pickFirstOpenOption = () =>
        cy
          .get(".n-base-select-menu:visible .n-base-select-option", {
            timeout: 5000,
          })
          .first()
          .click({ force: true })

      openSection("Ingredience").within(() => {
        cy.get(".n-dynamic-input").find("button").first().click({ force: true })
        // Ingredient select (first n-select in the new row).
        cy.get(".n-base-selection").eq(0).click({ force: true })
      })
      pickFirstOpenOption()
      // Guard: the dropdown close event can collapse the section; re-open if needed.
      cy.contains("h6", "Ingredience", { timeout: 10000 }).then($h6 => {
        if (!$h6.closest(".n-collapse-item").find(".n-input-number").length) {
          cy.wrap($h6).click({ force: true })
        }
      })
      cy.contains(".n-collapse-item", "Ingredience").within(() => {
        // Amount input. Break clear().type() chain: clear() triggers a Vue
        // re-render via v-model, detaching the element before type() runs.
        cy.get(".n-input-number input", { timeout: 10000 })
          .first()
          .clear({ force: true })
        cy.get(".n-input-number input").first().type("2")
        // Unit select (second n-select in the row).
        cy.get(".n-base-selection").eq(1).click({ force: true })
      })
      pickFirstOpenOption()

      // Postup: name + description.
      openSection("Postup").within(() => {
        cy.get(".n-dynamic-input").find("button").first().click({ force: true })
        cy.get('input[type="text"]').first().clear({ force: true })
        cy.get('input[type="text"]').first().type(stepName)
        cy.get("textarea").first().clear({ force: true })
        cy.get("textarea").first().type(`step-desc-${tag}`)
      })

      // Tipy a triky: name + description.
      openSection("Tipy a triky").within(() => {
        cy.get(".n-dynamic-input").find("button").first().click({ force: true })
        cy.get('input[type="text"]').first().clear({ force: true })
        cy.get('input[type="text"]').first().type(tipName)
        cy.get("textarea").first().clear({ force: true })
        cy.get("textarea").first().type(tipDesc)
      })

      cy.contains("button", "Uložit").click({ force: true })
      // Successful save navigates to the detail page; failed save stays on edit.
      cy.location("pathname", { timeout: 15000 }).should(
        "equal",
        `/cookbook/recipe/${recipeId}/`,
      )

      cy.reload()
      cy.contains(stepName, { timeout: 10000 }).should("exist")
      // Naive UI's CollapseList lazy-renders item bodies (the n-collapse-item
      // content node only mounts after the item has been opened at least
      // once, even with displayDirective="show"). Open the tip header so
      // tipDesc actually enters the DOM.
      // The clickable element is .n-collapse-item__header-main — the outer
      // __header is just a wrapper without the toggle handler.
      cy.contains(".n-collapse-item__header-main", tipName, {
        timeout: 10000,
      }).click({ force: true })
      // The wrapper has overflow:hidden during/after the collapse animation,
      // so .be.visible can flap. Existence is enough — the text being in the
      // DOM means the saved description hydrated into the rendered recipe.
      cy.contains(tipDesc, { timeout: 10000 }).should("exist")
    })
  })

  it("adds a step with a photo and uploads it via the staged save flow", () => {
    // Exercises useRecipeSave + UploadPhotosDialog + the new
    // /api/cookbook/recipe_steps/{id}/ endpoint end-to-end: the recipe
    // text save creates the step with photo=null, then the orchestrator
    // PATCHes the photo to the dedicated step endpoint.
    const auth = getStoredAuth()
    const token = auth.user?.token

    getOwnedRecipeId(auth.chef?.id, token).then(recipeId => {
      // Reset to a clean slate (no steps) so the dynamic-input renders
      // its empty-state add button and we own the step we'll create.
      cy.request({
        method: "PATCH",
        url: `${API_BASE_URL}/recipes/${recipeId}/`,
        headers: { Authorization: `Token ${token}` },
        body: { steps: [] },
      })

      cy.visit(`/recipe/${recipeId}/edit/`)
      cy.location("pathname").should("equal", `/cookbook/recipe/${recipeId}/edit/`)
      cy.get("textarea", { timeout: 15000 }).should("have.length.gte", 1)

      // Intercept the two endpoints we expect the orchestrator to hit.
      cy.intercept("PATCH", `**/api/cookbook/recipes/${recipeId}/`).as("recipePatch")
      cy.intercept("PATCH", "**/api/cookbook/recipe_steps/*/").as("stepPhotoPatch")

      const tag = `cypress-${Date.now()}`
      const stepName = `step-${tag}`

      // Add a step with a name. Photo input lives in the same row.
      cy.contains("h6", "Postup", { timeout: 10000 })
        .click({ force: true })
        .closest(".n-collapse-item")
        .within(() => {
          cy.get(".n-dynamic-input").find("button").first().click({ force: true })
          cy.get('input[type="text"]').first().clear({ force: true })
          cy.get('input[type="text"]').first().type(stepName)
        })

      // Attach a photo. The recipe already has its main photo so we
      // target the file input inside the step row specifically — it's
      // empty, so adding a file here doesn't collide with NUpload's
      // :max="1" constraint on the recipe-level input.
      cy.fixture("upload/red-pixel.png", "base64").then(base64 => {
        cy.contains(".n-collapse-item", "Postup")
          .find('input[type="file"]')
          .selectFile(
            {
              contents: Cypress.Buffer.from(base64, "base64"),
              fileName: "red-pixel.png",
              mimeType: "image/png",
            },
            { force: true },
          )
      })

      // The NForm change-trigger validator runs FileReader async to
      // populate `step.photo.base64data`; isNewUpload checks for that
      // key, so without it the orchestrator collects zero uploads. The
      // FileReader resolves on the next microtask after change fires —
      // a small wait is enough.
      cy.wait(500)

      cy.contains("button", "Uložit").click({ force: true })
      // Modal opens during the save+upload sequence.
      cy.contains("Ukládám recept", { timeout: 10000 }).should("exist")

      // First: recipe text PATCH (creates the step with photo=null).
      cy.wait("@recipePatch", { timeout: 30000 }).then(({ request }) => {
        const step = (request.body.steps || []).find(s => s.name === stepName)
        expect(step, `step "${stepName}" in payload`).to.exist
        expect(step.photo, "step.photo stripped before upload").to.be.null
      })

      // Second: per-step photo PATCH against the new endpoint.
      cy.wait("@stepPhotoPatch", { timeout: 30000 }).then(({ request }) => {
        expect(request.body.photo, "step photo payload").to.match(/^data:image\/png/)
      })

      // All-done → navigate to detail page.
      cy.location("pathname", { timeout: 30000 }).should(
        "equal",
        `/cookbook/recipe/${recipeId}/`,
      )
    })
  })

  it("changes ingredient unit and recomputes the amount", () => {
    // Cukr is seeded with g_per_liter=850, so it can use both weight and
    // volume units. Servings/pieces have no g_per_* set, so they must be
    // hidden from the dropdown.
    const auth = getStoredAuth()
    const token = auth.user?.token

    cy.request({
      url: `${API_BASE_URL}/ingredients/?search=Cukr`,
      headers: { Authorization: `Token ${token}` },
    }).then(({ body }) => {
      const cukr = body.results.find(i => i.name === "Cukr")
      expect(cukr, "seeded Cukr ingredient").to.exist

      cy.request({
        url: `${API_BASE_URL}/units/`,
        headers: { Authorization: `Token ${token}` },
      }).then(({ body: unitsBody }) => {
        const units = unitsBody.results || unitsBody
        const bySlug = Object.fromEntries(units.map(u => [u.slug, u]))

        getOwnedRecipeId(auth.chef?.id, token).then(recipeId => {
          // Pre-populate one ingredient in kilograms so the spec only has to
          // exercise the unit-change flow, not the row-creation flow.
          cy.request({
            method: "PATCH",
            url: `${API_BASE_URL}/recipes/${recipeId}/`,
            headers: { Authorization: `Token ${token}` },
            body: {
              ingredients: [
                {
                  order: 0,
                  ingredient_id: cukr.id,
                  unit_id: bySlug.kilograms.id,
                  amount: 2,
                  is_optional: false,
                },
              ],
            },
          })

          cy.visit(`/recipe/${recipeId}/edit/`)
          cy.location("pathname").should("equal", `/cookbook/recipe/${recipeId}/edit/`)
          cy.get("textarea", { timeout: 15000 }).should("have.length.gte", 1)

          cy.contains("h6", "Ingredience", { timeout: 10000 })
            .click({ force: true })
            .closest(".n-collapse-item")
            .within(() => {
              // First selection is the ingredient (Cukr); second is the unit.
              cy.get(".n-base-selection").eq(1).click({ force: true })
            })

          // Filtering: weight + volume must be present, but servings/pieces
          // must not (Cukr has no g_per_serving / g_per_piece).
          cy.get(".n-base-select-menu:visible", { timeout: 5000 }).within(() => {
            cy.contains(".n-base-select-option", "gram").should("exist")
            cy.contains(".n-base-select-option", "litr").should("exist")
            cy.contains(".n-base-select-option", "porce").should("not.exist")
            cy.contains(".n-base-select-option", "kus").should("not.exist")
            cy.contains(".n-base-select-option", "gram").click({ force: true })
          })

          // 2 kg → 2000 g.
          cy.contains(".n-collapse-item", "Ingredience").within(() => {
            cy.get(".n-input-number input").first().should("have.value", "2000")
          })

          cy.contains("button", "Uložit").click({ force: true })
          cy.location("pathname", { timeout: 15000 }).should(
            "equal",
            `/cookbook/recipe/${recipeId}/`,
          )

          // Backend round-trip: amount stored as 2000g.
          cy.request({
            url: `${API_BASE_URL}/recipes/${recipeId}/`,
            headers: { Authorization: `Token ${token}` },
          }).then(({ body }) => {
            const ing = body.ingredients.find(i => i.ingredient_id === cukr.id)
            expect(ing, "Cukr row").to.exist
            expect(ing.unit_id).to.equal(bySlug.grams.id)
            expect(ing.amount).to.equal(2000)
          })
        })
      })
    })
  })

  it("renders chefs view", () => {
    cy.visit("/chefs/")
    cy.contains("Kuchařstvo").should("exist")
    cy.get(".n-card").its("length").should("be.gte", 1)
  })
})
