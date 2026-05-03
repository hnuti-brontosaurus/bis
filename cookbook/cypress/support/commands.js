/// <reference types="cypress" />

/**
 * Programmatic chef login via the API. The auth token is fetched from a
 * TEST-only backend endpoint (api/cookbook/testing/auth_token/), so the
 * cypress runner doesn't need docker/shell access.
 */
Cypress.Commands.add("loginAsChef", email => {
  email ??= "test@test.local"
  const apiBase = "http://nginx/api/cookbook"

  cy.request("POST", `${apiBase}/testing/auth_token/`, { email }).then(
    ({ body: { token } }) => {
      expect(token, "auth token").to.match(/^[a-f0-9]{40}$/)

      // Hit the login endpoint with `Token <token>` as the password — the
      // backend accepts this short-circuit (see api/cookbook/views/auth.login).
      cy.request("POST", `${apiBase}/auth/login/`, {
        email,
        password: `Token ${token}`,
      }).then(({ body }) => {
        // Match the persisted shape pinia-plugin-persistedstate writes for
        // useAuthStore (data/auth.js): the store has a single state ref `me`,
        // and the persist config keys it as `cookbook:auth:v1`.
        window.localStorage.setItem("cookbook:auth:v1", JSON.stringify({ me: body }))
      })
    },
  )
})
