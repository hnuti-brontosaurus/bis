# Testing

Three layers, all runnable with one command from the repo root:

| layer      | tool           | where                        |
| ---------- | -------------- | ---------------------------- |
| types      | `tsc --noEmit` | `src/` and `e2e/`            |
| unit       | vitest         | `src/**/__tests__/*.test.ts` |
| end-to-end | Playwright     | [`e2e/`](../e2e)             |

```bash
make test_frontend                                # types + unit + e2e
make test_frontend spec=e2e/login.spec.ts         # one spec
make test_frontend grep='can sign in'             # by test title
make test_frontend workers=1                      # serial, for debugging
make e2e_frontend                                 # Playwright UI → http://localhost:8101
```

Everything runs in containers — no host Node toolchain is needed. See the
Testing section of the repo-root `CLAUDE.md` for the compose profiles.

## How the specs are written

The e2e specs stub **every** API call, so they need neither a backend nor a
database. The helpers live in [`e2e/support/`](../e2e/support):

- **`api.ts`** — `mock(page, matcher, reply)` wraps `page.route` with matching
  on method + pathname (glob or regex). It returns a `Recorder`, whose
  `first()` / `nth()` / `all()` resolve once the request has been made, so
  assertions on request bodies read like the old `cy.wait('@alias')`.
  Playwright runs route handlers newest-first, so a stub registered inside a
  test overrides one from `beforeEach`.
- **`mocks.ts`** — the recurring bundles: `mockCurrentUser`, `mockCategories`,
  `mockFullEvent`.
- **`test.ts`** — the `test` export starts every spec already signed in by
  seeding redux-persist's `persist:auth` entry via Playwright's
  `storageState`. Use `anonymousTest` for specs that drive the login form
  themselves. `expectPath` and `expectText` stand in for
  `cy.location('pathname')` and `cy.contains`.

Fixtures are plain JSON in [`e2e/fixtures/`](../e2e/fixtures), read with
`fixture('name')`. Binary inputs (images, spreadsheets) live in
[`e2e/assets/`](../e2e/assets) and are resolved with `asset('name.png')`.

`VITE_E2E=true` is set for the test stack; the app reads it to drop input
debounces to 0ms (`src/hooks/debouncedState.ts`).

## Continuous integration

`.github/workflows/ci.yml` runs `make test` on every push.

Failures leave a trace in `test-results/`; open it with
`npx playwright show-trace <path>` for a full timeline with DOM snapshots.
