# Testing

Three layers, all runnable with one command from the repo root:

| layer      | tool           | where                        |
| ---------- | -------------- | ---------------------------- |
| types      | `tsc --noEmit` | `src/` and `e2e/`            |
| unit       | vitest         | `src/**/__tests__/*.test.ts` |
| end-to-end | Playwright     | [`e2e/`](../e2e)             |

## Run tests

### From the repository root (containerized)

This is how CI runs them, and it needs no node toolchain on your machine — the
type check, the unit tests and Playwright all run inside containers.

```sh
make test_frontend                            # types + unit + e2e
make test_frontend spec=e2e/login.spec.ts     # one spec
make test_frontend grep='can sign in'         # by test title
make test_frontend workers=1                  # serial, for debugging
make e2e_frontend                             # Playwright UI → http://localhost:8101
```

See the testing section of [`CLAUDE.md`](../../CLAUDE.md) for the compose
profiles behind these targets.

### From `frontend/` with a local toolchain

```sh
yarn test:types  # tsc --noEmit, for src/ and e2e/
yarn test:unit   # vitest run
yarn test:e2e    # playwright test; set PW_BASE_URL to point at a running app
yarn test        # all three
```

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

[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) runs `pre-commit`
and `make test` (backend + frontend + cookbook) on every push. A push to
`master`, or any commit whose message contains `#deploy`, also deploys to the
[development server](https://dev.bis.brontosaurus.cz).

Failures leave a trace in `test-results/`; open it with
`npx playwright show-trace <path>` for a full timeline with DOM snapshots.
