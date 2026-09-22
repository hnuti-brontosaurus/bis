import { API_BASE, expect, readFixture, test } from "./support/test.js"

/** Playwright has no `closest()`; the reverse xpath axis picks the nearest match. */
const closestCollapseItem = locator =>
  locator.locator(
    'xpath=ancestor-or-self::*[contains(concat(" ", @class, " "), " n-collapse-item ")][1]',
  )

/**
 * Expands a collapsed section by its header text and scopes to that item.
 * Plain clicks (no `force`) matter here: Playwright waits for the collapse
 * animation to settle, whereas a forced click can land on a moving target and
 * silently toggle nothing.
 */
const openSection = async (page, title) => {
  const header = page.locator("h6", { hasText: title }).first()
  await header.click()
  return closestCollapseItem(header)
}

/**
 * Naive UI teleports dropdown menus out of the collapse item, and stale hidden
 * options from a previous dropdown stay in the DOM — so option clicks must
 * scope to the *visible* menu.
 */
const visibleOptions = page =>
  page.locator(".n-base-select-menu:visible .n-base-select-option")

/**
 * Ensures a Naive UI select's menu is open. The menu is teleported out of the
 * collapse item, which is still animating when a row first appears, so a click
 * can toggle the select open and straight back shut. Retrying the click until
 * the menu stays up is what makes this reliable when several workers share the
 * machine.
 */
const openSelect = (page, selection) =>
  expect(async () => {
    const options = visibleOptions(page)
    if (!(await options.first().isVisible())) await selection.click()
    await expect(options.first()).toBeVisible({ timeout: 2_000 })
  }).toPass({ timeout: 30_000 })

/**
 * Opens a select and clicks one of its options. Open and pick retry together,
 * because the menu can also close between the two.
 */
const pickOption = (page, selection, choose = options => options.first()) =>
  expect(async () => {
    const options = visibleOptions(page)
    if (!(await options.first().isVisible())) await selection.click()
    await choose(options).click({ timeout: 2_000 })
  }).toPass({ timeout: 30_000 })

const save = page => page.locator("button", { hasText: "Uložit" }).first().click()

test.describe("cookbook smoke", () => {
  test("renders recipes list and a recipe detail", async ({ page, recipe }) => {
    await page.goto("/cookbook/recipes/")
    await expect(page.getByText("Recepty").first()).toBeVisible()

    // The store fetches every page, so this test's own recipe is in the DOM —
    // clicking a neighbour's card would race its teardown.
    await page.locator(".n-card").filter({ hasText: recipe.name }).first().click()
    await expect(page).toHaveURL(new RegExp(`/cookbook/recipe/${recipe.id}/$`))
    await expect(page.getByText("Autorstvo").first()).toBeVisible()
  })

  test("opens edit form, mutates description, and persists", async ({
    page,
    recipe,
  }) => {
    await page.goto(`/cookbook/recipe/${recipe.id}/edit/`)
    await expect(page).toHaveURL(new RegExp(`/cookbook/recipe/${recipe.id}/edit/$`))

    const tag = `e2e-${Date.now()}`
    const description = page.locator("textarea").first()
    await expect(description).toBeVisible()

    const original = ((await description.inputValue()) ?? "").replace(/\s+$/, "")
    await description.fill(`${original} ${tag}`)

    await save(page)
    await expect(page).toHaveURL(new RegExp(`/cookbook/recipe/${recipe.id}/$`))

    await page.reload()
    await expect(page.getByText(tag).first()).toBeAttached()
  })

  test("adds an ingredient, step, and tip via the form and persists them", async ({
    page,
    recipe,
  }) => {
    // Regression for #order-not-filled: the dynamic-input creates rows as
    // `{}`, so the frontend must inject `order` from list position before
    // PATCH or the backend rejects RecipeIngredient/RecipeStep.
    const tag = `e2e-${Date.now()}`
    const stepName = `step-${tag}`
    const tipName = `tip-${tag}`
    const tipDesc = `tip-desc-${tag}`

    await page.goto(`/cookbook/recipe/${recipe.id}/edit/`)
    await expect(page.locator("textarea").first()).toBeVisible()

    const ingredients = await openSection(page, "Ingredience")
    await ingredients.locator(".n-dynamic-input button").first().click()
    // Ingredient select (first n-select in the new row).
    await pickOption(page, ingredients.locator(".n-base-selection").nth(0))

    // Closing the dropdown can collapse the section; re-open it if it did.
    const ingredientsItem = page.locator(".n-collapse-item", { hasText: "Ingredience" })
    if ((await ingredientsItem.locator(".n-input-number").count()) === 0) {
      await page.locator("h6", { hasText: "Ingredience" }).first().click()
    }

    const amount = ingredientsItem.locator(".n-input-number input").first()
    await amount.fill("2")
    // Unit select (second n-select in the row).
    await pickOption(page, ingredientsItem.locator(".n-base-selection").nth(1))

    const steps = await openSection(page, "Postup")
    await steps.locator(".n-dynamic-input button").first().click()
    await steps.locator('input[type="text"]').first().fill(stepName)
    await steps.locator("textarea").first().fill(`step-desc-${tag}`)

    const tips = await openSection(page, "Tipy a triky")
    await tips.locator(".n-dynamic-input button").first().click()
    await tips.locator('input[type="text"]').first().fill(tipName)
    await tips.locator("textarea").first().fill(tipDesc)

    await save(page)
    // Successful save navigates to the detail page; failed save stays on edit.
    await expect(page).toHaveURL(new RegExp(`/cookbook/recipe/${recipe.id}/$`))

    await page.reload()
    await expect(page.getByText(stepName).first()).toBeAttached()
    // Naive UI's CollapseList lazy-renders item bodies, so the tip header has
    // to be opened before its description enters the DOM. The clickable node
    // is .n-collapse-item__header-main — the outer __header is a wrapper
    // without the toggle handler.
    await page.locator(".n-collapse-item__header-main", { hasText: tipName }).click()
    // The wrapper has overflow:hidden during the collapse animation, so a
    // visibility assertion can flap. Presence in the DOM is what we need.
    await expect(page.getByText(tipDesc).first()).toBeAttached()
  })

  test("adds a step with a photo and uploads it via the staged save flow", async ({
    page,
    recipe,
  }) => {
    // Exercises useRecipeSave + UploadPhotosDialog + the
    // /api/cookbook/recipe_steps/{id}/ endpoint end-to-end: the recipe text
    // save creates the step with photo=null, then the orchestrator PATCHes
    // the photo to the dedicated step endpoint.
    await page.goto(`/cookbook/recipe/${recipe.id}/edit/`)
    await expect(page.locator("textarea").first()).toBeVisible()

    const recipePatch = page.waitForRequest(
      request =>
        request.method() === "PATCH" &&
        request.url().includes(`${API_BASE}/recipes/${recipe.id}/`),
    )
    const stepPhotoPatch = page.waitForRequest(
      request =>
        request.method() === "PATCH" &&
        /\/api\/cookbook\/recipe_steps\/\d+\//.test(request.url()),
    )

    const tag = `e2e-${Date.now()}`
    const stepName = `step-${tag}`

    const steps = await openSection(page, "Postup")
    await steps.locator(".n-dynamic-input button").first().click()
    await steps.locator('input[type="text"]').first().fill(stepName)

    // The recipe already has its main photo, so target the file input inside
    // the step row — it is empty, so adding a file there does not collide
    // with NUpload's :max="1" on the recipe-level input.
    await steps.locator('input[type="file"]').setInputFiles({
      name: "red-pixel.png",
      mimeType: "image/png",
      buffer: readFixture("upload/red-pixel.png"),
    })

    // The NForm change-trigger validator runs FileReader to populate
    // `step.photo.base64data`; isNewUpload checks for that key, so without it
    // the orchestrator collects zero uploads.
    await page.waitForTimeout(500)

    await save(page)
    await expect(page.getByText("Ukládám recept").first()).toBeAttached()

    const step = ((await recipePatch).postDataJSON().steps || []).find(
      s => s.name === stepName,
    )
    expect(step, `step "${stepName}" in payload`).toBeTruthy()
    expect(step.photo, "step.photo stripped before upload").toBeNull()

    expect((await stepPhotoPatch).postDataJSON().photo).toMatch(/^data:image\/png/)

    await expect(page).toHaveURL(new RegExp(`/cookbook/recipe/${recipe.id}/$`), {
      timeout: 30_000,
    })
  })

  test("changes ingredient unit and recomputes the amount", async ({
    page,
    api,
    recipe,
  }) => {
    // Cukr is seeded with g_per_liter=850, so it can use both weight and
    // volume units. Servings/pieces have no g_per_* set, so they must be
    // hidden from the dropdown.
    const { results: ingredients } = await api
      .get(`${API_BASE}/ingredients/?search=Cukr`)
      .then(response => response.json())
    const cukr = ingredients.find(ingredient => ingredient.name === "Cukr")
    expect(cukr, "seeded Cukr ingredient").toBeTruthy()

    const unitsBody = await api
      .get(`${API_BASE}/units/`)
      .then(response => response.json())
    const bySlug = Object.fromEntries(
      (unitsBody.results || unitsBody).map(unit => [unit.slug, unit]),
    )

    // Pre-populate one ingredient in kilograms so the spec only exercises the
    // unit-change flow, not the row-creation flow.
    await api.patch(`${API_BASE}/recipes/${recipe.id}/`, {
      data: {
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

    await page.goto(`/cookbook/recipe/${recipe.id}/edit/`)
    await expect(page.locator("textarea").first()).toBeVisible()

    const section = await openSection(page, "Ingredience")
    // First selection is the ingredient (Cukr); second is the unit.
    const unitSelect = section.locator(".n-base-selection").nth(1)
    await openSelect(page, unitSelect)

    // Labels are pluralized for the current amount (2 → "gramy", "litry"), so
    // match on the stem. Anchoring at the start keeps "gram" off "kilogramy"
    // and "litr" off "mililitry".
    const option = stem =>
      visibleOptions(page).filter({ hasText: new RegExp(`^\\s*${stem}`) })

    await expect(option("gram")).toHaveCount(1)
    await expect(option("litr")).toHaveCount(1)
    await expect(option("porce")).toHaveCount(0)
    await expect(option("kus")).toHaveCount(0)
    await pickOption(page, unitSelect, () => option("gram"))

    // 2 kg → 2000 g.
    await expect(
      page
        .locator(".n-collapse-item", { hasText: "Ingredience" })
        .locator(".n-input-number input")
        .first(),
    ).toHaveValue("2000")

    await save(page)
    await expect(page).toHaveURL(new RegExp(`/cookbook/recipe/${recipe.id}/$`))

    const saved = await api
      .get(`${API_BASE}/recipes/${recipe.id}/`)
      .then(response => response.json())
    const ingredient = saved.ingredients.find(row => row.ingredient_id === cukr.id)
    expect(ingredient, "Cukr row").toBeTruthy()
    expect(ingredient.unit_id).toBe(bySlug.grams.id)
    expect(ingredient.amount).toBe(2000)
  })

  test("removes the photo from a recipe that already has one", async ({
    page,
    api,
    recipe,
  }) => {
    // The write side has to accept `photo: null` — that is how both "never had
    // a photo" and "user removed it" reach the backend.
    expect(recipe.photo, "seeded photo").not.toBeNull()

    const recipePatch = page.waitForRequest(
      request =>
        request.method() === "PATCH" &&
        request.url().includes(`${API_BASE}/recipes/${recipe.id}/`),
    )

    await page.goto(`/cookbook/recipe/${recipe.id}/edit/`)
    await expect(page.locator("textarea").first()).toBeVisible()

    // The image-card upload renders its remove button inside the file card;
    // it only shows on hover, hence the forced click.
    await page
      .locator(".n-upload-file-list .n-upload-file")
      .first()
      .locator("button")
      .last()
      .click({ force: true })

    await save(page)
    expect((await recipePatch).postDataJSON().photo, "cleared photo payload").toBeNull()

    await expect(page).toHaveURL(new RegExp(`/cookbook/recipe/${recipe.id}/$`), {
      timeout: 30_000,
    })
    // The detail page of a photo-less recipe must render — reading photo.large
    // unguarded used to throw here.
    await expect(page.getByText("Autorstvo").first()).toBeVisible()

    const saved = await api
      .get(`${API_BASE}/recipes/${recipe.id}/`)
      .then(response => response.json())
    expect(saved.photo, "photo after removal").toBeNull()
  })

  test("renders chefs view", async ({ page }) => {
    await page.goto("/cookbook/chefs/")
    await expect(page.getByText("Kuchařstvo").first()).toBeVisible()
    expect(await page.locator(".n-card").count()).toBeGreaterThanOrEqual(1)
  })
})
