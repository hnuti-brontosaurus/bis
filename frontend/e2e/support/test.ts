import { expect, type Page, test as base } from '@playwright/test'

export { expect } from '@playwright/test'

/** Direct equivalent of `cy.location('pathname').should('equal', pathname)`. */
export const expectPath = (page: Page, pathname: string, timeout = 15_000) =>
  expect.poll(() => new URL(page.url()).pathname, { timeout }).toBe(pathname)

/** Direct equivalent of `cy.contains(text)` used as an assertion. */
export const expectText = (page: Page, text: string | RegExp) =>
  expect(page.locator('body')).toContainText(text)

export const AUTH_TOKEN = '1234567890abcdef'

/**
 * redux-persist stores one `persist:<key>` entry per slice, with every field
 * of the slice serialized separately inside it. Seeding it lets a spec start
 * signed in without driving the login form — see login.spec.ts for the flow
 * that still covers signing in for real.
 */
export const PERSISTED_AUTH_KEY = 'persist:auth'

export const persistedAuth = JSON.stringify({
  access: 'null',
  token: JSON.stringify(AUTH_TOKEN),
  isLoggingOut: 'false',
  _persist: JSON.stringify({ version: 1, rehydrated: true }),
})

/** Starts every test signed in. Specs that test signing in use `anonymousTest`. */
export const test = base.extend({
  storageState: async ({ baseURL }, use) => {
    await use({
      cookies: [],
      origins: [
        {
          origin: new URL(baseURL as string).origin,
          localStorage: [{ name: PERSISTED_AUTH_KEY, value: persistedAuth }],
        },
      ],
    })
  },
})

export const anonymousTest = base
