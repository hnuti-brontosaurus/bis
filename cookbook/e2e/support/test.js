import { test as base } from "@playwright/test"
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const here = path.dirname(fileURLToPath(import.meta.url))

export { expect } from "@playwright/test"

export const TEST_USER_EMAIL = "test@test.nope"
export const API_BASE = "/api/cookbook"

// Worker fixtures cannot depend on `baseURL` (a test-scoped option), so the
// origin is read from the same env var playwright.config.js uses.
export const BASE_URL = process.env.PW_BASE_URL ?? "http://nginx"

/** pinia-plugin-persistedstate keys the cookbook auth store under this name. */
export const AUTH_STORAGE_KEY = "cookbook:auth:v1"

export const readFixture = name =>
  fs.readFileSync(path.join(here, "..", "fixtures", name))

export const test = base.extend({
  /**
   * Signs the seeded chef in over the API once per worker. The token comes
   * from a TESTING-only backend endpoint, so the runner needs no shell access
   * to the backend container.
   */
  chef: [
    async ({ playwright }, use) => {
      const api = await playwright.request.newContext({ baseURL: BASE_URL })

      const tokenResponse = await api.post(`${API_BASE}/testing/auth_token/`, {
        data: { email: TEST_USER_EMAIL },
      })
      const { token } = await tokenResponse.json()

      // The backend accepts `Token <token>` as the password — see
      // api/cookbook/views/auth.login.
      const loginResponse = await api.post(`${API_BASE}/auth/login/`, {
        data: { email: TEST_USER_EMAIL, password: `Token ${token}` },
      })
      const me = await loginResponse.json()

      await api.dispose()
      await use(me)
    },
    { scope: "worker" },
  ],

  storageState: async ({ chef, baseURL }, use) => {
    await use({
      cookies: [],
      origins: [
        {
          origin: new URL(baseURL ?? BASE_URL).origin,
          localStorage: [
            { name: AUTH_STORAGE_KEY, value: JSON.stringify({ me: chef }) },
          ],
        },
      ],
    })
  },

  /** An API client authenticated as the seeded chef. */
  api: async ({ playwright, baseURL, chef }, use) => {
    const context = await playwright.request.newContext({
      baseURL,
      extraHTTPHeaders: { Authorization: `Token ${chef.user.token}` },
    })
    await use(context)
    await context.dispose()
  },

  /**
   * A throwaway recipe owned by the chef, with a photo on disk. Every spec
   * gets its own so they can mutate freely and run in parallel.
   */
  recipe: async ({ api, chef }, use) => {
    const [difficulties, requiredTimes] = await Promise.all([
      api.get(`${API_BASE}/recipe_difficulties/`).then(r => r.json()),
      api.get(`${API_BASE}/recipe_required_times/`).then(r => r.json()),
    ])
    const photo = readFixture("upload/red-pixel.png").toString("base64")

    const response = await api.post(`${API_BASE}/recipes/`, {
      data: {
        name: `e2e-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        chef_id: chef.chef.id,
        difficulty_id: difficulties.results[0].id,
        required_time_id: requiredTimes.results[0].id,
        is_public: false,
        photo: `data:image/png;filename=red-pixel.png;base64,${photo}`,
      },
    })
    const created = await response.json()

    await use(created)

    await api.delete(`${API_BASE}/recipes/${created.id}/`)
  },
})
