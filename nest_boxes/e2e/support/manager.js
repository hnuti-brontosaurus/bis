import { randomUUID } from "node:crypto"

import { test as base, expect } from "@playwright/test"

const API = "/api/nest_boxes"
const PASSWORD = "nest-boxes-e2e"
const BUDKAR_EMAIL = "budkar@budky.nope"
const SEEDED_AREA = "E2E Cibulka"

const csrfToken = async context =>
  (await context.cookies()).find(cookie => cookie.name === "csrftoken").value

/**
 * The budkař signed in, and an area of their own for each test: the seeded
 * area is shared with the volunteer specs, which reseed it as they run.
 */
export const test = base.extend({
  api: async ({ page, context }, use) => {
    const login = await page.request.post("/api/auth/login/", {
      data: { email: BUDKAR_EMAIL, password: PASSWORD },
    })
    expect(login.ok()).toBe(true)
    await page.request.get(`${API}/whoami/`)
    const headers = { "X-CSRFToken": await csrfToken(context) }
    const call = async (method, url, data) => {
      const response = await page.request.fetch(`${API}${url}`, {
        method,
        data,
        headers,
      })
      expect(response.ok(), `${method} ${url}: ${await response.text()}`).toBe(true)
      return response.status() === 204 ? null : response.json()
    }
    await use({
      get: url => call("GET", url),
      post: (url, data) => call("POST", url, data),
    })
  },

  area: async ({ api }, use) => {
    // The public list: the budkař's own roles flicker while another spec
    // reseeds, and the area is missing for a moment while it is recreated.
    // One page, since the list shrinks under a reseed.
    let seeded
    while (!seeded) {
      const { results } = await api.get("/public/areas/?page_size=200")
      seeded = results.find(area => area.name === SEEDED_AREA)
    }
    const area = await api.post("/areas/", {
      name: `E2E ${randomUUID().slice(0, 8)}`,
      administration_unit_id: seeded.administration_unit.id,
    })
    // Somewhere of its own in Czechia, so the maps don't stack the test areas
    const [lng, lat] = [13 + Math.random() * 4, 49 + Math.random()]
    const box = (name, east) =>
      api.post("/boxes/", {
        area_id: area.id,
        name,
        status: "in_use",
        location: { type: "Point", coordinates: [lng + east, lat] },
        type_id: 2,
        hole_shape: "round",
        hole_size: 33,
        opening: "front",
        installed_on: "2020-03-01",
      })
    const boxes = {}
    for (const [name, east] of [
      ["1", 0],
      ["2", 0.0012],
      ["3", 0.0024],
    ])
      boxes[name] = await box(name, east)
    await use({ ...area, boxes, box })
  },
})

export { expect }

/** Picks an option of a naive-ui select by its text. */
export const choose = async (page, select, option) => {
  await select.click()
  await page.locator(".n-base-select-option", { hasText: option }).first().click()
}
