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

  // Ensure a chef row exists for this user (idempotent — testing_db seeds
  // the user but not the cookbook Chef).
  const py = [
    "from io import BytesIO",
    "from PIL import Image",
    "from django.core.files.uploadedfile import SimpleUploadedFile",
    "from bis.models import User",
    "from cookbook.models.chefs import Chef",
    "from rest_framework.authtoken.models import Token",
    `u, _ = User.objects.get_or_create(email='${email}', defaults={'first_name': 'Cypress', 'last_name': 'Tester'})`,
    "Token.objects.get_or_create(user=u)",
    `c, _ = Chef.objects.get_or_create(user=u, defaults={'name': 'Cypress Chef', 'email': u.email})`,
    "buf = BytesIO()",
    "Image.new('RGB', (32, 32), 'red').save(buf, format='PNG')",
    "c.photo or c.photo.save('chef.png', SimpleUploadedFile('chef.png', buf.getvalue(), 'image/png'))",
    "print(u.auth_token.key)",
  ].join("; ")
  const ensureChef = `docker exec ${container} python manage.py shell -c "${py}"`

  cy.exec(ensureChef).then(({ stdout }) => {
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
