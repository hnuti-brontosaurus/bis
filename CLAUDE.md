# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BIS (Brontosaurus Information System) is a full-stack web application for managing the Brontosaurus movement, a Czech youth organization. It handles event management, volunteering opportunities, user profiles, donations tracking, and a cookbook system.

**Tech Stack:**
- Backend: Django 4.x + Django REST Framework + PostgreSQL/PostGIS
- Frontend: React 18 + TypeScript + Redux Toolkit (RTK-Query)
- Cookbook: Vue 3 + Vite (separate SPA)
- Infrastructure: Docker + Docker Compose + Nginx

## Common Commands

### Development
```bash
make build            # Build all Docker images (run first)
make dev              # Start all services with live-reload
make clean            # Stop all containers and remove orphans
```

### Testing
```bash
make test              # Run all tests (backend + frontend + cookbook)
make test_backend      # Run pytest tests only
make test_frontend     # check_frontend + e2e_frontend
make test_cookbook     # check_cookbook + e2e_cookbook
make check_frontend    # Frontend type-check + vitest, in-container
make check_cookbook    # Cookbook vitest, in-container
make e2e_frontend      # Frontend Playwright — FULLY MOCKED (page.route). Containerized.
make e2e_cookbook      # Cookbook Playwright — REAL e2e against backend + postgres. Containerized.
make ui_frontend       # Interactive frontend Playwright UI mode → http://localhost:8101
make ui_cookbook       # Interactive cookbook Playwright UI mode → http://localhost:8100
```

The `check_*` / `e2e_*` split exists so CI can run them as separate parallel
jobs; locally `make test_frontend` still runs both.

`e2e_frontend` / `e2e_cookbook` accept `spec=<path>`, `grep=<title>` and
`workers=<n>` (e.g. `make e2e_frontend spec=e2e/login.spec.ts workers=1`).

Test stack profiles (`docker-compose.test.yaml`):
- `frontend` profile → nginx + frontend (no backend/DB) — used by `check_frontend` / `e2e_frontend` / `ui_frontend`.
- `cookbook` profile → nginx + cookbook + backend + postgres — used by `check_cookbook` / `e2e_cookbook` / `ui_cookbook`.
- `backend` profile → backend + postgres (+ nginx) — used by `test_backend`.
- `playwright` profile → cookbook Playwright runner (`mcr.microsoft.com/playwright`). Started on demand via `docker compose run --rm playwright`, never by `up`.
- `playwright-frontend` profile → frontend Playwright runner. Same image, mounts `frontend/` instead.

Both runners are fully containerized — no host Node toolchain is needed. The
image ships the browsers at `/ms-playwright`; `@playwright/test` itself comes
from the app's `node_modules` via the bind mount, so **the version pinned in
`frontend/package.json` and `cookbook/package.json` must match the image tag in
`docker-compose.test.yaml`**. The runners join the test docker network, so
`baseURL` is `http://nginx`. Playwright 1.63 requires Node ≥ 20, which is why
the frontend image is on Node 22.

Interactive runs use Playwright UI mode, served over HTTP on a published port —
no X server needed. `--headed` / `--debug` still work via the WSLg / X11 mounts.

Every compose bind-mount source must exist in the checkout, owned by the host
user. Docker creates a missing one itself, as **root**, and the containers run
as `${UID}:${GID}` — so the mount silently becomes unwritable. That is why
`backend/media`, `backend/frontend_static` and `backend/cookbook_static` each
carry a force-added `.gitkeep` despite being gitignored.

### CI (`.github/workflows/ci.yml`)
`pre-commit`, `test-backend`, `check-frontend`, `check-cookbook`,
`e2e-frontend`, `e2e-cookbook` and `build` all run in parallel; the deploy jobs
need all seven. Only `build` writes the buildx (`cache-to: type=gha`) and
node_modules caches — the rest restore only, so parallel jobs cannot race on a
cache scope.

Do not add ordering between the test jobs to make one set something up for
another; that coupling is what the `.gitkeep` files above replaced.

The e2e jobs start the ~2 GB Playwright image pull in the background right
after checkout, so it finishes while buildx builds the app image.

The frontend e2e suite takes 1.2m-2.0m for the same 48 specs on an unchanged
config, so comparing two CI runs cannot resolve anything smaller than roughly
a 40% change. Measure a tuning change by running both settings back to back in
one job instead. Done that way, `workers=4` beats the `50%` default by only
108s to 110.5s — the suite is bound by per-test browser and app startup, not
by CPU, so there is little to win by giving it more cores.

Frontend type-check + unit tests also run in-container — `make check_frontend` invokes `docker compose run --rm frontend sh docker-entrypoint.sh check` (see `frontend/docker-entrypoint.sh` for the `check` mode), so no host yarn install is needed at all. `test:types` covers `e2e/` too via `frontend/e2e/tsconfig.json`; Playwright itself does not type-check.

Cookbook unit tests use vitest + jsdom and run inside the cookbook container — `make check_cookbook` invokes `docker compose run --rm cookbook sh docker-entrypoint.sh check`. Specs live next to the source as `src/**/__tests__/*.test.js` and shouldn't depend on the dev backend (mock @/data modules).

Frontend specs are fully mocked and start signed in: `frontend/e2e/support/test.ts`
seeds the `persist:auth` localStorage entry through Playwright's `storageState`
instead of driving the login form, so only `login.spec.ts` walks the real sign-in
flow. `support/api.ts` wraps `page.route` with a Cypress-like matcher plus a
`Recorder` that replaces `cy.wait('@alias')` — Playwright runs route handlers
newest-first, so a stub registered in a test overrides one from `beforeEach`,
the same precedence `cy.intercept` had.

Cookbook seeding is exposed as a TEST-only Django endpoint at `POST /api/cookbook/testing/seed/` (`api/cookbook/views/testing.py`) — gated by `settings.TESTING` so it 404s in production. `cookbook/e2e/global-setup.js` POSTs to it once per run, which keeps the runner container minimal (no docker CLI, no socket mount).

Cookbook tests run against real backend state. The `testing_db cookbook` seed provides the chef, the ingredients and one canonical recipe; beyond that, the `recipe` fixture in `cookbook/e2e/support/test.js` creates a throwaway recipe per test and deletes it afterwards, so specs can mutate freely and run in parallel. The chef logs in over the API once per worker. The test DB volume is wiped on teardown.

### Backend-specific
```bash
docker exec -it bis-backend sh                          # Shell into backend container
docker exec -it bis-backend python manage.py <command>  # Run Django management command
docker exec -it bis-backend python manage.py migrate    # Apply migrations
docker exec -it bis-backend python manage.py reset      # Import old database
docker exec -it bis-backend python manage.py testing_db dev      # Full demo seed for dev.bis.brontosaurus.cz (flush + ~80 entities)
docker exec -it bis-backend python manage.py testing_db cookbook # Minimal idempotent seed for cookbook tests (categories + chef)
```

Containers run as the host UID/GID (`user: ${UID}:${GID}` in `docker-compose.yaml`, exported by the Makefile), so files written from inside (migrations, fixtures, build output) are owned by your host user. No `-u` flag or `sudo chown` needed.

If you need a running container (backend shell, management command, Python with the project's deps like `googleapiclient`/`google-auth`, DB access, etc.) and none is up, ask the user to run `make dev` (or the relevant `make` target) in a separate terminal rather than installing deps on the host or starting containers yourself. The backend has real credentials (e.g. `GOOGLE_CREDENTIALS`) wired in via env, so run Google Drive / external-service code inside `bis-backend`, not in a host venv.

### Frontend-specific
```bash
yarn --cwd frontend generate-api       # Regenerate RTK-Query types from the deployed dev backend (https://dev.bis.brontosaurus.cz/api/schema/) — needs internet
yarn --cwd frontend generate-api-local # Regenerate RTK-Query types from the local backend (http://localhost/api/schema/) — needs `make backend` running, no internet required
yarn --cwd frontend lint               # Run ESLint
yarn --cwd frontend format             # Run Prettier
```

### Pre-commit hooks
Validate any changes with `pre-commit run --files <changed files>` before committing. See `.pre-commit-config.yaml` for the hook list.

## Architecture

### Directory Structure
```
backend/              # Django application
├── bis/              # Core models (User, Location, etc.) and admin
├── api/              # REST API organized by domain:
│   ├── web/          # Public API endpoints
│   ├── auth/         # Authentication
│   ├── manage/       # Internal management
│   ├── categories/   # Category endpoints
│   ├── cookbook/     # Cookbook API
│   └── frontend/     # Frontend-specific endpoints
├── event/            # Event management
├── opportunities/    # Volunteering opportunities
├── feedback/         # Event feedback system
├── donations/        # Donation tracking
├── cookbook/         # Cookbook backend models
└── project/          # Django settings & URL config

frontend/             # React SPA
cookbook/             # Vue 3 SPA (separate from main frontend)
```

### API Connection Pattern
- RTK-Query services live in `frontend/src/app/services/bis.ts` (manually curated)
- Auto-generated types in `frontend/src/app/services/testApi.ts`
- Types must be re-exported through `bisTypes.ts` - never import directly from `testApi`
- Run `yarn generate-api` when API changes

### Transactional emails (Ecomail)
All emails are sent through Ecomail templates referenced by hardcoded
`template_id` in `backend/bis/emails.py`. The template's **name in Ecomail is
the email subject** (`get_name_from_template`, cached 5 minutes) and may contain
`*|variable|*` placeholders — Ecomail substitutes variables in the body only, so
`send_email` fills the subject itself; an unfilled placeholder is logged as an
error and sent as is, never raised, so one bad subject cannot block a batch.

The Ecomail API (`https://api2.ecomailapp.cz/`, header `key:`) can list
(`GET /templates`, paginated) and read (`GET /template/{id}`, includes `html` but
never `mjml`). `PUT /templates/{id}` exists and preserves the html byte for byte,
but it **switches the template to HTML mode and loses the drag-and-drop editor**,
so edits and renames are manual work in the Ecomail UI — verified on template 162.
Never create a new template instead of editing one; the id is in the code.

Triggers are either Django signals / DRF serializers, or the `daily` command run
by `backend/bis/scheduler.py` at 7:00 Prague (`nightly` at 5:00).

A per-email overview (trigger, recipients, variables, code reference) lives in
the "přehled emailů" tab of the Automatické emaily spreadsheet.

### Backend image
`backend/Dockerfile` is multi-stage: the builder installs `git` (one dependency
is a `git+https` URL) and runs `uv sync`; the runtime stage copies `/venv` and
installs only the shared libraries that are loaded at runtime rather than
imported —

- `libgdal36`, `libgeos-c1t64` — GeoDjango globs for these by path, see the
  `GDAL_LIBRARY_PATH` / `GEOS_LIBRARY_PATH` block in `project/settings.py`
- `libpango-1.0-0`, `libpangoft2-1.0-0`, `fonts-dejavu-*` — weasyprint. Without
  a font installed it still emits a PDF, just with the glyphs dropped.

pyheif needs nothing: its wheel bundles libheif/libde265/libaom/libx265 under
`site-packages/pyheif.libs`. It is no longer compiled from source, so
`build-essential`, `pkg-config` and `libheif-dev` are not needed anywhere.

Because none of these are `import`ed, a missing one fails only at runtime.
`project/tests/test_runtime_libraries.py` exercises each; keep it in step when
changing the apt list.

`requests` is floored at 2.34 because premailer pulls cssutils → encutils →
chardet 7, and older requests assert `chardet < 6` — every management command
then opens with a `RequestsDependencyWarning`.

### Backend startup
`django.setup()` imports ~2600 modules. Three things made that slow, all fixed;
the numbers are what a fresh container measured, so keep them in mind before
adding a module-scope import of anything heavy:

- The venv ships precompiled (`uv sync --compile-bytecode`). Without it Python
  recompiles ~5900 files on every start — 5.8s instead of 2.25s — and throws
  the result away with the container. Costs 74MB of image.
- `runserver`'s autoreloader repeats the whole import in a second process, so
  the `testing` entrypoint passes `--noreload`. `dev` keeps the reloader, and
  therefore still pays for two.
- weasyprint (~0.9s) is imported at its use site in `xlsx_export/export.py`,
  because admin autodiscovery loads that module on every start.

`make dev` still runs `migrate` and then `runserver`, so it pays the import
twice over. Migrations themselves are not the cost: of a ~4.5s no-op `migrate`,
reading all 299 migration files is 116ms and planning 29ms, against 2.3s of app
import and 0.6s of system checks. `migrate` therefore passes `--skip-checks`,
since `runserver` runs the checks itself moments later.

`bis/scheduler.py` must start the scheduler in exactly one process. Under
`runserver` that is the reloader child (`RUN_MAIN`), except with `--noreload`
where there is no child and no `RUN_MAIN`; under gunicorn it is the worker.
`bis/tests/test_scheduler.py` pins all of those, because getting it wrong
either runs every scheduled command twice or stops them firing at all.

### Image / file fields
Every model `ImageField`/`FileField`/`ThumbnailImageField` is serialized by the
Base64 mixin in `backend/api/helpers.py`. Reads render thumbnail URL dicts
(`{small, medium, large, original}`) or `null` when empty. Writes accept:
- a data-URI string (`data:image/png;filename=x.png;base64,...`) — uploads it
- a dict — ignored (`SkipField`), so a read payload can be PATCHed back as-is
- `null` — clears the file, but only where the model field is `blank=True`;
  required image fields still reject it. The columns are NOT NULL, so null is
  stored as `""`.

Model convention: a file field is either required (no kwargs) or optional
(`blank=True`) — never `null=True`. Empty is always `""`, never NULL.

Frontend consequence: an empty photo must be sent as `null`, never `undefined`
(`JSON.stringify` drops undefined keys, so the field would go untouched).

### Cookbook models

`cookbook` is the only app whose models live in a package. Django imports just
`cookbook/models/__init__.py`, so every model module has to be imported there —
a missing one is invisible to the app registry, and `migrate` announces the
models "have changes that are not yet reflected in a migration" because the
autodetector wants to delete the table. The model still works at runtime, since
admin autodiscovery or a viewset import registers it late — `migrate` is the
only place the omission shows up.

### Data Flow
1. React/Vue frontends → RTK-Query/Axios → Django REST Framework API
2. API validates via Django models → PostgreSQL + PostGIS (geospatial)
3. Nginx reverse proxy routes all requests

## Code Style

### Language
English for code, comments, variable names. Czech for user-facing strings.

### Naming Conventions
- React components: `PascalCase.tsx` in `PascalCase/` folders
- Non-component TypeScript: `camelCase.ts`
- CSS modules: `ComponentName.module.scss` next to component
- Python: snake_case (enforced by black/isort)
- API response properties use snake_case to match backend
- No abbreviations — use the full word (`ingredient`, not `ing`). Single-letter loop variables in tight scopes are fine.

### React/TypeScript
- One component per file, no default exports
- Use absolute imports
- Style with CSS modules + SCSS
- Forms use react-hook-form + yup validation

### Comments
- Default: no comments. Code with well-named identifiers should explain itself, rather rewrite the code to be more readable.
- Only write a comment for a non-obvious **why** — a constraint, an invariant, a workaround for a specific bug, or behavior that would surprise a reader.
- Do not write: section banners (`# ---- Foo ----`, `# Static files`), restatements of the next line, references to tasks/PRs/tickets, commented-out code blocks (use git history), or framework template boilerplate.
- If deleting the comment wouldn't confuse a competent reader, don't write it.

### Commit Messages
- Capital first letter, imperative style, no trailing period
- Follow with empty line, then details
- PRs with many small commits get squashed on merge

## Claude instructions
- When implementing new code / fixing a command, you are encouraged to update and CLAUDE.md with new findings about the repository to improve it
- No defensive fixes. Fix the root cause, keep it DRY, fail fast — no consumer-side guards or sanitizers for upstream bugs.
