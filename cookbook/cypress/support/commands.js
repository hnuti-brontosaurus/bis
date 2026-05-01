/// <reference types="cypress" />

/**
 * Programmatic chef login via the API. Uses an auth token grabbed from the
 * backend (so we bypass hCaptcha and password-typing entirely).
 *
 * The token is fetched once per spec via cy.exec on a Django shell snippet.
 *
 * Backend container name + login email are env-configurable so the same
 * spec works against both `bis-backend` (dev seed) and `bis-test-backend`
 * (testing_db seed). Defaults match the dev stack.
 */
Cypress.Commands.add("loginAsChef", email => {
  email ??= Cypress.env("TEST_USER_EMAIL") || "lamanchy@gmail.com"
  const container = Cypress.env("BACKEND_CONTAINER") || "bis-backend"
  const apiBase = Cypress.env("API_BASE_URL") || "http://localhost/api/cookbook"

  // Fetch the chef's auth token. The chef is seeded by testing_db
  // (see backend/bis/management/commands/testing_db.create_cookbook_chef).
  const py = [
    "from bis.models import User",
    `print(User.objects.get(email='${email}').auth_token.key)`,
  ].join("; ")
  const fetchToken = `docker exec ${container} python manage.py shell -c "${py}"`

  cy.exec(fetchToken).then(({ stdout }) => {
    const token = stdout.trim().split(/\s+/).pop()
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
  })
})
