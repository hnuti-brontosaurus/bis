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

The postgres healthcheck has to force TCP (`pg_isready -h 127.0.0.1`). Over the
unix socket it answers for the temporary server the image runs during initdb,
which listens on the socket only, so compose calls postgres healthy and starts
the backend against a port nothing is accepting on yet. The test stack sets
`restart: "no"`, so one lost race fails the whole job; dev's `restart: always`
retries and hides it.

The app services and Playwright runners set `init: true`. Their PID 1 would
otherwise be `sh docker-entrypoint.sh` or `npx`, and the kernel gives PID 1 no
default signal actions: SIGTERM is ignored, so Ctrl+C on `make dev` waits out
the 10s stop timeout and then SIGKILLs.

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

Backend pytest specs live in `<app>/tests/test_*.py`. Building a usable BIS
object graph in a fixture has three non-obvious requirements — see
`backend/api/frontend/tests/conftest.py`:
- `Event.clean()` demands a qualified main organizer and a geolocated venue,
  so create events inside `paused_validation()`.
- `User.update_roles()` returns early unless the `BrontosaurusMovement`
  singleton and the matching `RoleCategory` rows exist. Without roles every
  organizer is rejected by `Permissions`, so an API test 403s.
- `BrontosaurusMovement.get()` caches the singleton in redis, *outside* the
  test transaction. A fixture that creates one must `cache.delete(
  "brontosaurus_movement")` both before and after, or the rolled-back row
  leaks into unrelated tests and their FK derefs raise `User.DoesNotExist`.

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

### URL layout
User-facing paths are Czech: the cookbook SPA lives at `/kucharka/` (vite
`base`), the game book at `/sbornik/`. Code, url names, the `/api/cookbook/`
API and the static directories keep their English names.

A path served by Django rather than the React app has to be listed in three
places: `nginx/dev.conf` (and `test.conf` if tests need it), the ingress in
`deployments/{devel,production}/ingress.yml` (a separate GitLab repo, gitignored
here), and a `ServerRedirect` route in `frontend/src/App.tsx`. The last one is
what makes `/login?next=<path>` work: after sign-in the router navigates
client-side, and `ServerRedirect` turns that into a full page load. `/o/*` is
listed so the MCP OAuth flow (`/o/authorize/?…` → `LOGIN_URL` `/logout?next=…`)
survives the login; `next` carries the query string for that reason.

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

`django_cleanup` deletes a file on commit once its row is deleted or the field
is replaced, and `ThumbnailImageField` removes its thumbnails alongside. Neither
checks whether another row still references the file name, so moving a file
between rows means copying it (`field.save(name, other.field.file)`), never
assigning `other.field` — see `User.merge_with`.

### MCP server
`/mcp` exposes one GraphQL `query` tool (`bis/mcp.py`, schema in
`bis/mcp_schema.py`) for staff and the Brontobot account. The one rule is **no
PII**: names, emails (organisation ones included), phones, birthdays and
addresses (only the region is kept) never appear in results. People are
anonymous `UserType` rows (id, birth year, region). Filter-based oracles (`filters: {user__email__startswith: …}`) are accepted.
The game book and cookbook are deliberately left out.

- Person models (`User`, `EventApplication`, `Donor`, the address types) list
  their fields explicitly, so a new model field stays hidden until reviewed.
  Other models use `exclude=`.
- `aggregate` group/sum paths may only walk fields the schema exposes
  (`EXPOSED_FIELDS`), so grouping cannot print a hidden value. `birth_year` is
  an alias for `birthday__year`.
- `export=true` emails a full-PII XLSX. It only works for models that are in
  `EXPORT_SERIALIZERS` in `xlsx_export/export.py`. Emailed exports go through
  `SavedFile.store`, which puts each file in a random directory: `/media` is
  served without authentication, so the directory name is the only thing
  keeping the file private. `nightly` deletes them after 14 days.
- `bis/tests/test_mcp_schema.py` denylists PII field names across the schema.
  Add to `ALLOWED` only after deciding the field is not PII.

### Logs
`bis/logs.py` writes one JSON line per record to `LOG_DIR`
(`/app/logs/backend/<utc hour>.jsonl`, on the `django-logs` volume) and the MCP
`logs` tool — superusers and the bot only — is the one way they are read. So a
record is written to be filtered, not to be read in a terminal:

- The message is a fixed phrase, optionally ending in a value from a small
  closed set (`Finished GET request on event-detail with 200`). Never an id, a
  count or an exception text: those go to `extra={"data": {...}}`.
- `data` names people by id only. The files are PII-free by construction rather
  than filtered on read, because a filter can recognise an email but not a
  name. Exception texts come from libraries, so emails and phone numbers are
  masked as the record is written; a name inside one would still get through.
- `logging.exception("Failed …")` with a fixed message: the formatter appends
  the exception class to the message and puts its text in `data.error`.
- Something that takes time is wrapped in `operation("running nightly
  command")`, which logs `Started` / `Finished` / `Failed` around that core.
- `request_id` ties together everything logged in one request or scheduler run
  and `user_id` is there once the request is authenticated — DRF does that
  inside the view, so only the closing `request` line is sure to have it. A
  record about a user who is not signed in (a rejected login) passes
  `extra={"user_id": …}` itself.

`RequestLogMiddleware` logs one line per request; query values and bodies are
never logged. `free_space` deletes the oldest hour files once the volume is
over 90%, each time a new file is opened. nginx writes its error log to the
same volume; its access log is off, since it was never rotated.

`disable_existing_loggers` has to stay `False`: `runserver` configures logging
twice, and the default silently disables every logger created in between.
Tests drop the file handler (`backend/conftest.py`).

### Fundraising campaigns
Campaign membership is a `DonorEvent` and the telesales views are keyed by donor
id, so only a `Donor` can be in a campaign. The `change_fundraising_campaign`
admin action (in `bis/admin.py`, shared by `UserAdmin` and `DonorAdmin`) creates
the missing `Donor` profiles when run on users. A donor profile therefore does
not mean the person ever gave: the Ecomail `Dárce` tag (`ecomail/tags.py`) needs
a donation or a pledge, except for profiles from before
`GIFTLESS_DONOR_CUTOFF` — those are legacy donors whose gifts predate the
donation records. The tag definitions are mirrored for the office in the
"Tagy pro ecomail.xlsm" file on Drive; keep it in step.

### Cookbook models

`cookbook` is the only app whose models live in a package. Django imports just
`cookbook/models/__init__.py`, so every model module has to be imported there —
a missing one is invisible to the app registry, and `migrate` announces the
models "have changes that are not yet reflected in a migration" because the
autodetector wants to delete the table. The model still works at runtime, since
admin autodiscovery or a viewset import registers it late — `migrate` is the
only place the omission shows up.

`Ingredient.category` is required and defaults to the `other`
`IngredientCategory`, looked up by slug when an ingredient is created. Tests run
with `--no-migrations`, so the row is not there unless a test asks for the
`ingredient_categories` fixture. Groq replaces the default on create, which is
why the new-ingredient form has no category field.

### Cookbook theme

`cookbook/src/composables/theme.js` is the single source of the palette (light
and dark). It feeds two consumers: the naive-ui `themeOverrides`, and CSS
variables (`--background`, `--surface`, `--line`, `--primary-text`, `--accent`,
… plus `--font-display` / `--font-body`) that a `watchEffect` writes onto
`<html>`. Shared classes in `assets/main.css` (`.panel`, `.columns`,
`.section-heading`, `.card-grid`, `.save-bar`, `.title-row`) and scoped styles
use those variables; never hard-code a colour in a component.

- The overrides are built as `entry.self(common)` with the *customised* common,
  then every `px` is multiplied by `SCALE`. Passing naive's default-derived
  values instead freezes every component to the stock colours, because a
  per-component override beats anything naive derives from `common`.
- A component rendered as a peer (the `InternalSelection` inside `Select`) only
  takes overrides from `Select.peers.InternalSelection`, not from a top-level
  `InternalSelection` key.
- Colours in `common` must be hex or `rgba()`: naive parses them, so
  `color-mix()` or `var()` throws at render.
- `position: sticky` needs the page content to sit directly in the outer
  `n-layout` scroll container. `n-layout-content` adds its own `overflow-x:
  hidden` box, which silently pins a sticky bar to nothing.
- New user-facing text has to exist in `backend/translation/*.yaml`; the
  cookbook eslint rule rejects unknown `_.group.key` lookups.
- Fonts are self-hosted variable woff2 (Bitter, Source Sans 3; latin +
  latin-ext) declared in `assets/base.css`.
- The edit form's e2e selectors depend on the `n-collapse-item` / `h6` section
  markup of `GenericForm`, and the detail page's on `CollapseList` for tips.

### Cookbook checkable lists

One rule for every list whose rows carry a checkbox (recipe ingredients, recipe
steps): the checkbox and the expand arrow are too small to aim at, so

- the arrow sits on the left and the checkbox on the right,
- clicking anywhere on a row expands or collapses its detail,
- clicking anywhere in the checkbox's cell ticks or unticks the row,
- a row with nothing to expand ticks instead, so no click is dead,
- a group row (an ingredient part heading) ticks all of its rows and shows as
  ticked exactly when all of them are,
- the header row does the same for the whole list: the row expands everything,
  its checkbox cell ticks everything.

Clicks that land on the checkbox or arrow itself are left to naive-ui, so they
are not handled twice. `RecipeIngredients.vue` does this through `row-props`
and a click handler on the table (naive-ui has no header-row hook);
`contrib/components/CollapseList.vue` does it for any list given a
`checked-key`, by keeping the checkbox area out of `trigger-areas`. A new
checkable list should follow the same rule rather than invent its own.

### Game book

`backend/game_book/` is server-rendered (django-bootstrap5, Bootstrap 5.3 from
the CDN). `static/game_book.css` defines the palette once as its own tokens
(`--surface`, `--primary`, …) for light and `[data-bs-theme="dark"]`, then maps
Bootstrap's `--bs-*` variables onto them — restyle through the tokens, not per
component. `static/game_book/theme.js` is loaded render-blocking in `<head>` and
sets `data-bs-theme` (and `data-theme`, which `bis/static/tinymce_dark_mode.js`
reads for the editor skin) from localStorage `game_book_theme`, else the OS.

- The chips in the forms are the unchanged Django checkbox / radio inputs: the
  input is visually hidden and its label drawn as a chip (`div[id^="id_"] >
  .form-check`). The on state of the four toggle buttons is likewise pure CSS,
  `:has([class*="-fill"])`, because `toggle_state` only swaps the icon class.
- The TinyMCE content lives in an iframe, so it is themed separately by
  `static/game_book/editor.css`, injected through `content_style` in
  `game_form.js`; its colours are hardcoded copies of the tokens.
- `add_form` clones the last formset row from the direct children of the
  button's parent, so the formset and its "add" button must share one wrapper
  (`.file-forms`).
- `GAME_FORM_SECTIONS` in `forms.py` is the single list of `GameForm` fields and
  of the panels the edit form groups them into.
- No test covers the game book and every write view needs a session, so visual
  checks of the edit form mean rendering the view in a Django shell
  (`RequestFactory`, `request.user = …`) and serving that HTML to Playwright via
  `page.route`.

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
