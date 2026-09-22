import { chromium, request } from "@playwright/test"

/**
 * Seeds the cookbook fixtures (categories, chef, ingredients, one canonical
 * recipe) through the TESTING-only backend endpoint. `testing_db cookbook` is
 * idempotent, so re-running is cheap.
 *
 * Then loads the SPA once. Vite transforms modules the first time a browser
 * asks for them; without this, every worker races that cold compile at the
 * same moment and interactions stall past their timeout.
 */
export default async function globalSetup(config) {
  const { baseURL } = config.projects[0].use
  const api = await request.newContext({ baseURL })

  const response = await api.post("/api/cookbook/testing/seed/")
  if (!response.ok()) {
    throw new Error(`seed failed: ${response.status()} ${await response.text()}`)
  }

  await api.dispose()

  const browser = await chromium.launch()
  const page = await browser.newPage({ baseURL })
  await page.goto("/cookbook/recipes/")
  await page.waitForLoadState("networkidle")
  await browser.close()
}
