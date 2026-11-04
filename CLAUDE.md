# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BIS (Brontosaurus Information System) is a full-stack web application for managing the Brontosaurus movement, a Czech youth organization. It handles event management, volunteering opportunities, user profiles, donations tracking, and a cookbook system.

**Tech Stack:**
- Backend: Django 4.x + Django REST Framework + PostgreSQL/PostGIS
- Frontend: React 18 + TypeScript + Redux Toolkit (RTK-Query)
- Cookbook: Vue 3 + Vite (separate SPA)
- Nest box database (`nest_boxes/`, at `/budky/`): Vue 3 + Vite + naive-ui + MapLibre, a third SPA
- Infrastructure: Docker + Docker Compose + Nginx

## Common Commands

### Development
```bash
make build            # Build all Docker images (run first)
make dev              # Start all services with live-reload
make clean            # Stop all containers and remove orphans
make prodlike         # Backend + nginx as prod runs them: gunicorn, 1 CPU / 900M, postgres 0.5 CPU / 200M
```

`make prodlike` is for measuring performance (`docker-compose.prodlike.yaml`);
`BACKEND_CPUS` / `BACKEND_MEMORY` override the backend's limits, and `docker
update --cpus` changes postgres' on the fly. It runs `ENVIRONMENT=dev` so the
debug toolbar and SQL middleware don't skew timings.

Concurrent requests share the backend's CPU limit: three simultaneous
changelist loads each take about three times as long. gunicorn's 8 threads
overlap only the time spent waiting on postgres, and a second worker would not
help either while the limit is 1 CPU, since both would share that one CPU.

### Testing
```bash
make test              # Run all tests (backend + frontend + cookbook + nest boxes)
make test_backend      # Run pytest tests only
make test_frontend     # check_frontend + e2e_frontend
make test_cookbook     # check_cookbook + e2e_cookbook
make check_frontend    # Frontend type-check + vitest, in-container
make check_cookbook    # Cookbook vitest, in-container
make e2e_frontend      # Frontend Playwright — FULLY MOCKED (page.route). Containerized.
make e2e_cookbook      # Cookbook Playwright — REAL e2e against backend + postgres. Containerized.
make ui_frontend       # Interactive frontend Playwright UI mode → http://localhost:8101
make ui_cookbook       # Interactive cookbook Playwright UI mode → http://localhost:8100
make test_nest_boxes   # check_nest_boxes + e2e_nest_boxes
make check_nest_boxes  # Nest box vitest, in-container
make e2e_nest_boxes    # Nest box Playwright — REAL e2e against backend + postgres, like the cookbook
make ui_nest_boxes     # Interactive nest box Playwright UI mode → http://localhost:8102
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
- `nest_boxes` profile → nginx + nest_boxes + backend + postgres — used by `e2e_nest_boxes` / `ui_nest_boxes`.
- `playwright-nest-boxes` profile → nest box Playwright runner, mounts `nest_boxes/`, UI on 8102.

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
`backend/media`, `backend/frontend_static`, `backend/cookbook_static` and
`backend/nest_boxes_static` each
carry a force-added `.gitkeep` despite being gitignored.

### CI (`.github/workflows/ci.yml`)
`pre-commit`, `test-backend`, `check-frontend`, `check-cookbook`,
`check-nest-boxes`, `e2e-frontend`, `e2e-cookbook`, `e2e-nest-boxes` and
`build` all run in parallel; the deploy jobs need all nine. Only `build` writes the buildx (`cache-to: type=gha`) and
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

A `RunPython` that deletes or updates rows goes in its own migration, never
next to schema operations on the same table: Postgres defers the FK triggers
of those writes to the end of the transaction, and an `ALTER TABLE` before then
fails with "pending trigger events". Test stacks skip migrations (`--run-syncdb`),
so only `make dev` against a database with rows catches it.

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
here), and a `ServerRedirect` route in `frontend/src/App.tsx`, outside the
authenticated routes: `/logout?next=<path>` navigates client-side too, signed
out, and under `AuthenticatedOutlet` would end on `/login`. The last one is
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
`bis/mcp_schema.py`) for staff and bot accounts. The game book and cookbook
are deliberately left out. It is **switched off in production** (`MCPPermission`
in `project/urls.py` denies everyone) until the data processing agreements are
in place; dev runs it as usual. What an account may see depends on the data
processing agreement behind its LLM, so it is set per user by two flags in
the user admin's "Interní data" (superusers only): `is_bot` (no roles, sees
every row, no inbox) and `sees_personal_data_over_mcp`. The Brontobot (ollama,
no DPA) has only `is_bot`, the chatbot (business ChatGPT with a DPA) both.

- **Health data** is never exposed: `health_issues` / `behaviour_issues` are not
  in the schema, and answers to health questions are null for everyone.
- **Personal data** (names, emails, phones, birthdays, addresses, contacts,
  free-text notes) is only for accounts with `sees_personal_data_over_mcp`. Everyone
  else, staff included, sees people as anonymous `UserType` rows (id, birth
  year, region).
- Those fields are in the schema for everyone, tagged by `personal()`; the
  `HidePersonalData` extension adds a validation rule that rejects them for
  any other account, so the query fails instead of returning nulls.
- Filters, ordering and aggregate paths may only walk fields the account can
  see (`_check_lookup`, `_aggregate_expression`): a filter on a hidden value is
  an oracle for it. `birth_year` is an alias for `birthday__year`.
- Person models (`User`, `EventApplication`, `Donor`, the address types) list
  their fields explicitly, so a new model field stays hidden until reviewed.
  Other models use `exclude=`.
- Questionnaire `Question`s and feedback `Inquiry`s carry a `sensitivity`
  (none / personal / health) that Groq assigns (`common/sensitivity.py`) right
  after a question is saved with new text, unless an identical question is
  already classified; `nightly` retries the rest via `classify_questions`.
  Distinct questions go in batches of 50, keyed by id: gpt-oss-120b allows
  8K tokens per minute and 200K per day, which one call per question would
  exhaust with the system prompt alone. The existing questions were classified
  once into data migrations (`questionnaire/0014`, `feedback/0022`). An
  unclassified question hides its answers from everyone. Answers and replies
  are masked per row by `_answer_visible`, aggregated through the same
  condition, and never filterable.
- `export=true` emails a full-PII XLSX to the signed-in user. A bot must
  instead name `export_to`, which has to belong to a `can_see_all` person
  other than a bot, so whoever drives the bot cannot route PII to an
  arbitrary inbox. Nobody else may pass `export_to`.
- Exports only work for models that are in
  `EXPORT_SERIALIZERS` in `xlsx_export/export.py`. Emailed exports go through
  `SavedFile.store`, which puts each file in a random directory: `/media` is
  served without authentication, so the directory name is the only thing
  keeping the file private. `nightly` deletes them after 14 days.
- `bis/tests/test_mcp_schema.py` requires every PII-named field to be tagged
  `personal()`. Add to `ALLOWED` only after deciding the field is not PII.

### Data sensitivity docs
`/docs/` is a public page listing the business data of BIS field by field as
public / internal / personal / secret, with filters. Framework, login and token
tables, technical models, `_`-prefixed helper columns, the cookbook and the
game book are left out (`UNDOCUMENTED_*`).
The levels live in `bis/data_sensitivity.py`, field by field, and a field takes
the strictest level of any of its uses. `bis/tests/test_data_sensitivity.py`
fails when a model field is unclassified, when a level disagrees with the MCP
schema (`personal()` ⇔ personal, other exposed fields public or internal), or
when the public `/api/web/` serializers show an internal or secret field — so
adding a model field means classifying it there.

The requirements and the private analysis of the old nest box app are in the
gitignored `old_budky/docs/`, next to a full copy of the old site that includes
credentials and logs.

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

### Cookbook photo galleries

A recipe, each recipe ingredient, step and tip has a `photos` gallery
(`RecipePhoto` / `RecipeIngredientPhoto` / `RecipeStepPhoto` /
`RecipeTipPhoto`, ordered by `order`; the first recipe photo is the cover).
The recipe save (`useRecipeSave.js`) sends only `{id, order}` of the photos
already saved, so drf-writable-nested reorders them and deletes the missing
ones, and then each new photo is POSTed on its own to its `recipe_*_photos`
endpoint with its `parent_id`. The uploads find their parent rows by position
in the saved recipe, so every child list needs an `order` field. The file is
read into base64 at upload time, not in a form rule: a collapsed step or
ingredient row unmounts its form.

Comments and private notes (`RecipeComment`, `RecipeNote`) are written by any
signed-in user, chef or not, and have galleries the same way
(`data/recipeComments.js`). They are not part of the recipe payload: a private
comment is visible only to its writer, the recipe's author and editors, a note
only to its writer.

### Cookbook servings

`RecipeIngredient.amount` is stored per one serving; every view multiplies it
by the servings shown. The recipe editor shows amounts for its own servings
input (initially `default_servings`) and divides by it on save, so the stored
values never depend on `default_servings`. With "recalculate" off, changing
the servings or an ingredient's unit leaves the typed numbers alone.

### Cookbook rich text

Every free-text cookbook field is an `HTMLField`, edited in the SPA by
`contrib/components/HtmlEditor.vue` (GenericForm `type: "html"`) and shown by
`components/app/HtmlText.vue` through `v-html`. That is safe only because the
API sanitizes on write: `SanitizesHTML` in `api/cookbook/serializers.py` maps
`HTMLField` to an nh3-cleaned field that keeps just what the editor's toolbar
can produce and drops empty paragraphs and repeated `<br>`s. A new HTML field
on a serializer without the mixin would be stored unsanitized. The editor's
Tiptap extensions and the nh3 allowlist have to change together.

The cookbook uses Tiptap rather than the TinyMCE the admin and game book use:
it is headless, so the toolbar is naive-ui buttons that follow the cookbook
theme, dark mode included. TinyMCE needs one skin per theme and cannot switch
skins on a live editor, and `@tinymce/tinymce-vue`'s `v-model` resets the
cursor while a format caret is open.

The editor's emoji button inserts plain unicode from `emoji-picker-element`,
with the English emojibase data bundled (there is no Czech data, so search
matches English names). Emoji are drawn in Noto Color Emoji everywhere: it
follows the body and display fonts in `theme.js`. `assets/noto-color-emoji.css`
declares it from fontsource's `.woff` files, not its stylesheet: the `.woff2`
files keep only the SVG colour table, which Chrome draws as blanks, while the
`.woff` files also keep COLRv1.

Single-line inputs take a `max_length` equal to the model's `max_length`.

### Cookbook articles

The cookbook menu entries under "Proč vegan?", "Tipy a triky" and "Přidej se"
are `Article`s, one per `Article.Slug`; the slug is also the route name and the
menu key, and the title comes from the `menu` translations. `ArticleViewSet`
creates a row on first lookup instead of seeding it, so articles survive
`testing_db dev`'s flush. Editors edit them in place on the page. Their
`content` is the only HTML field that allows headings (`h2`, `h3` — the `<h1>`
is the page title), quotes, horizontal rules and images: `ArticleHTMLField`
on the backend, `HtmlEditor`'s `rich` and `uploadImage` props on the frontend.
A new article needs a slug, a migration, a path in `router.js` and a menu
entry.

An inserted image is POSTed to `article_images` right away and the editor
puts its `src` (the `large` thumbnail, a relative `/media/` path) into the
content. The content is the source of truth: the article save drops any
`<img>` that is not one of the article's `ArticleImage`s and deletes every
`ArticleImage` the content no longer references, so an image removed from the
text, or uploaded and then cancelled, is gone on the next save. Its size is a
`size-*` class picked in the editor's bubble menu (small left — the default —
small right, medium, full); the sanitizer allows only those classes, and below
600px every size is full width.

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

### Nest box app

`nest_boxes/` is the SPA of the nest box database, served at `/budky/` (vite
`base`, from `APP_PATH` in `src/config.js`). The spec lives in the gitignored
`old_budky/docs/` (`implementation.md`, `design.md`, `visual-design.md`, the
mockups in `mockups/`). It shares no code with the cookbook.

- **npm, not yarn.** It runs on `node:26-alpine`, which no longer ships yarn,
  so the lockfile is `package-lock.json` and the entrypoint runs `npm install`.
- **Dev port 3003** (`bis-nest-boxes`); 3002 is often taken on the host.
- **Login** is the Django session that every BIS login creates
  (`django_login` in `api/auth/views.py`), the same thing the MCP OAuth flow
  relies on, so the SPA keeps no token of its own. The axios client sends
  the `csrftoken` cookie back as `X-CSRFToken`, so the `/api/nest_boxes/`
  views need DRF `SessionAuthentication` (and `whoami` should
  `ensure_csrf_cookie`). Signing in goes to
  `/logout?next=/login?next=/budky/…`: the BIS frontend keeps its token in
  localStorage `persist:auth` for longer than the session lives, and with a
  stale one `/login` would bounce straight back without a session. A route
  with `meta.requiresLogin` redirects only once `whoami` said anonymous; a
  failed `whoami` leaves `me` null, which is unknown, not anonymous.
- **Theme:** `src/composables/theme.js` is the single palette (Light forest
  1 / Forest 3 from `visual-design.md`), feeding naive-ui and CSS variables
  named like the design doc's tokens (`surface2` → `--surface-2`, nested
  `map.forestLine` → `--map-forest-line`, `mk.nfInk` → `--mk-nf-ink`). The
  cookbook theme pitfalls apply, except there is no `SCALE`.
- **maplibre-gl 6** is ESM with named exports only, and finds its worker next
  to its own module, which Vite's pre-bundling and the build both lose;
  `components/map/maplibre.js` hands it the bundled worker (`?worker&url`).
- **The map style** is `MAP_STYLE_URL` (OpenFreeMap positron) recoloured by
  `styleFor` in `components/map/mapStyle.js`, with Czech names and
  hillshade/contours from AWS terrain tiles via maplibre-contour. Anything a
  component draws as a layer goes through `BaseMap`'s `setOverlay`, because
  the style is rebuilt on a theme switch and `setStyle` drops layers added
  with `addLayer`. DOM markers survive it.
- **E2e:** `e2e/global-setup.js` seeds once per run. The seeded area is shared
  with specs that reseed it mid-run, so the manager specs get an area of their
  own per test (`area` fixture in `e2e/support/manager.js`), and they look the
  seeded unit up through `public/areas/`: reseeding recomputes the budkař's
  roles, so a manager-only request can 403 for a moment.
- **Query lists:** the axios client sends arrays as the key repeated
  (`paramsSerializer: { indexes: null }`), which is what django-filter reads;
  the default `type[]=` is silently ignored.
- **Labels and inputs:** naive-ui's `n-input`, `n-input-number` and
  `n-date-picker` put a plain `id` on their wrapper; a `<label for>` needs
  `:input-props="{ id }"` to reach the input.
- **Wording:** a `Batch` is an "obchůzka" in every user-facing text, URLs
  included (`/obchuzka/<id>/`, `/obchuzky/`); code and the API keep `batch`.
- **Bottom sheet:** `MapPanelLayout`'s drag zone (handle + `#summary` slot)
  takes pointer capture, and a captured pointer's click lands on the zone, not
  on a button inside it; so a drag never starts on a button, link or input.
- **Map of areas** (`AreasMapView`, `/mapa/`) has two modes, `?mode=boxes` for
  managers only: area bubbles from the public endpoints, or every manageable box
  from `boxes/map/` (an unpaginated light serializer; the box page loads the
  rest). It reuses the area page's `BoxFilters` / `BoxList`; `BoxList` renders
  20 rows and more as they scroll into sight. A click on a single marker or
  bubble selects its row in the panel, a second click opens it (the area page
  only for managers), and a merged bubble or cluster zooms to fit its members; opening and acting start from the list. Boxes cluster below zoom 14 the way areas merge
  (`BoxClusters`, same `MERGE_GAP`, a merged bubble's thick outline). The landing map
  groups by region instead (`public/regions/`: outline, a point inside, box
  count), so the public never gets a box's coordinates.
- **Built static** goes to `nest_boxes/dist`, which CI copies to
  `backend/nest_boxes_static/`; production nginx serves it like the
  cookbook's (`deployments/base`).
- **Volunteer pages** (`/d/<token>/…`, `views/link/`) work offline. The
  `link` store (`data/link.js`) keeps the link payload in IndexedDB
  (`data/offline.js`) and falls back to it when `GET links/<token>/` gets no
  answer. Checks, photos and new boxes go into the outbox
  (`data/outbox.js`) first and are sent in the order they were saved, on
  `online`, every 30 s and after each save. The ids are client UUIDs, so
  resends are idempotent; a resent photo replaces the one with the same
  `order` (`LinkCheckPhotosView`). A 410 drops everything of that link, a
  4xx is kept as rejected and skipped, a 5xx or no answer stops the run.
- **Service worker** (vite-plugin-pwa `generateSW`, registered in `main.js`,
  icons generated from `public/logo.svg` by `pwaAssets`): the app shell is
  precached, map files on the map origins (anything with an extension:
  tiles, glyphs, sprites, DEM) are cache-first, and the style and TileJSON
  network-first, since they name the current tile version. Opening a link
  prefetches the area (`components/map/prefetch.js`): the tiles of every
  source in the style's TileJSON plus the DEM, over the boxes' bounds plus
  1 km, ≤4 requests at once and ≤3,000 tiles (OpenFreeMap's terms), whole
  zoom levels from the lowest. It just `fetch`es them, and the service
  worker stores them, so it waits until the worker controls the page. Dev
  has no service worker, so offline map tiles can only be tried on a build.

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

### Old BIS (1 April)

`backend/old_bis/` re-creates the pre-2023 PHP BIS at `/stary/`: its original
CSS and images, Django templates copied from saved pages, filled with live data
through `Permissions(..., "frontend")`. Links either move between its own
pages or do nothing (`href="#" onclick="return false"`); the only way out is
the "Zpět do nového BISu" button, so nothing sends an organizer to the admin.
The login form posts to the real `/api/auth/login/`. On 1 April (Prague)
`frontend/src/utils/redirectToOldBis.ts` sends the bare `/` there, unless the
"Zpět do nového BISu" button stored the year in localStorage
`old-bis-escaped`. Deep links (applications, `/login?next=`) are never
redirected. HTML fields (`DashboardItem`) render through the `plain_text`
filter, never `|safe`, because some items embed event names.

### Nest boxes

`backend/nest_boxes/` is the box database behind `/budky/`. Views stay thin:
permissions, spacing, check upserts, confirming and statistics live in
`nest_boxes/{permissions,boxes,checks,statistics}.py`.

- "In use" is `status = in_use` (`NestBox.objects.in_use()`). A box a
  volunteer hangs through a batch link is a planned box with no `created_by`
  (`NestBox.is_new`) plus a pending check in that batch that hangs it
  (`box_changes.hung`), created together by `checks.submit_box`; confirming the
  check hangs the box, deleting it deletes the box (`checks.delete_check`).
- A planned box that never hangs is deleted (`boxes.delete_box`), never
  cancelled; a box that did hang is ended.
- "Verified" is not stored: a box is verified once it has a confirmed check that
  is not historical (`NestBox.objects.with_is_verified()`, which
  `with_season_state()` includes). The API keeps `is_verified` as a field and
  a filter on that annotation; the check form of an unverified box, or one
  missing a required field, asks for its data and sends all of it.
- `checks.validate_check` is the check form's flow on the server (not found →
  only a note saying why; a check hanging a box → no cleaning questions; not
  cleaned → a reason, and contents only if `NestBoxNotCleanedReason.contents_known`).
  `checkForm.js` `validate` / `buildPayload` mirror it: change them together.
  "Nešla otevřít" is a not-cleaned reason, not a cleaning value. `contents` says
  what the box held this season (a nest or remains), not what is in it now.
- A box has one note, `note`, shown to managers and on batch links as
  "Poznámka pro dobrovolníky". `Area.note` and `Check.note` are internal.
- `NestBox.save()` sets `region` from the location and recomputes the stored
  `closest_distance` / `closest_same_type_distance` for the whole area in one
  SQL `UPDATE`. `bulk_create`, `bulk_update` and `QuerySet.update` skip that, so
  call `NestBox.recompute_distances(area_id)` after them.
- A box's state this season (planned / to check / attention / done) is
  defined once, `NestBox.objects.with_season_state()`; the SPA shows the
  API's `season_state` and only lays checks still in a phone's outbox over it
  (`reportedState` in `composables/boxes.js`). A pending check counts as
  confirmed, judged by what confirming it would leave on the box, so that
  annotation mirrors `checks._box_values`: change them together. Past seasons
  have no states (a box's past status is not kept); their map pie comes from
  the checks, see `statistics._states_per_area`. Tests pin the season by
  monkeypatching `Check.current_season`, there is no freezegun.
- Change a box through `boxes.update_box`, which writes `NestBoxHistory`;
  `box.save()` alone records nothing.
- `NestBox` and `Check` have client-generated UUID pks for offline use.
  Django forces an INSERT for an unsaved instance whose pk has a default, so
  saving a resend of an existing row needs `save(force_update=True)`.
- A FK to `Check` can't be called `check`: it shadows `Model.check()` and
  breaks the system checks. Hence `box_check`.
- The budkař role is `BrontosaurusMovement.nest_box_managers` (role slug
  `nest_box_manager`, `User.is_nest_box_manager`). It is deliberately not
  part of `is_staff`, and the admin shows the app to superusers only.

The API is `backend/api/nest_boxes/`, at `/api/nest_boxes/`:

- **Sign-in is the Django session**, not the token. The BIS login
  (`/api/auth/login/`) calls `django.contrib.auth.login`, so the session cookie
  is set for the whole origin; the token in `persist:auth` is the React app's
  own and its format belongs to redux-persist. Every nest box view therefore
  sets `authentication_classes = [SessionAuthentication]` (`NestBoxAPIMixin`),
  `whoami/` sets the `csrftoken` cookie (`ensure_csrf_cookie`), and the SPA
  sends it back as `X-CSRFToken` on writes — without it a signed-in write is a
  403. Anonymous requests (public pages, batch links) need no CSRF. The SPA
  signs in through `/logout?next=/login?next=/budky/…`: a stale BIS token with
  no session would make `/login` bounce straight back, logged out.
- `NestBoxAPIMixin.handle_exception` turns the domain's Django
  `ValidationError` into a 400, `BatchClosed` into a 410 and `ProtectedError`
  into a 400, so views call the domain functions without try blocks.
- Managers' querysets are filtered by `manageable_areas`, so another unit's
  rows are 404s; `IsManager` (`permissions.is_manager`) makes everything a 403
  for non-managers. A budkař without any area is still a manager.
- A batch link (`links/<token>/…`) shows only that batch's boxes and never
  volunteers' emails.
- `POST /api/nest_boxes/testing/seed/` (TESTING only, 404 elsewhere) resets the
  e2e fixture set from `nest_boxes/e2e_seed.py` and returns its ids: budkař
  `budkar@budky.nope` and the rightless `clen@budky.nope`, both with password
  `nest-boxes-e2e`, area "E2E Cibulka" with boxes 1, 2 (verified by a check
  last season), 3 (unverified) and planned P1, an open batch with token `…0001` (boxes 1, 2, P1) and a closed one
  with `…0002`. Box ids are fixed, area and batch ids are not. Specs sign in by
  POSTing to `/api/auth/login/`, which sets the session cookie. The same seed
  is `testing_db nest_boxes`.
- `update_box` clears `elevation` when the location changes;
  `fill_nest_box_elevations` (in `nightly`) fills empty ones from OpenTopoData
  `eudem25m`, 100 points a request, one request a second.
- `daily` sends `emails.open_batches_reminder` on Mondays: batches open over a
  week, to the area unit's board and the batch's author.

`import_old_nest_boxes <dump.sql>` replaces **all** nest box data (areas,
batches and photos included) with the old database. It reads the Adminer dump
in Python (`old_import/dump.py`) and never runs it; `old_import/plan.py`
applies the cleanup rules without the database, `old_import/load.py` writes.
The cleanup rules come from the private `old_budky/docs/` (implementation.md
lists them), so no note text or name from the dump may go into the code; rules
are regexes over note vocabulary and dates. Non-obvious parts:

- One old record can become several boxes: each replacement note ends a box
  (`worn_out`) and starts a new one with the same name and place. `old_id` is
  unique, so only the box hanging now carries it. A note calling the spot
  unsuitable (`notes.asks_to_move`) leaves the box as it is, to be moved; one
  saying the box won't be replaced ends it, for a missing or fallen tree or
  destruction if the note names one, else with no end reason
  (`notes.end_reason`).
- `note` is read by volunteers, so a box note that only says what the fields
  now hold (material, opening, a previous name, a replacement year that split
  the box) or that it was once found or measured stays out of it
  (`notes.is_recorded`). To-dos for the old app's managers stay in: a
  volunteer at the box is who can act on them.
- The 16 November 2025 Mikulčický batch is found by its date and a per-area
  occupied share under 25 %, not by area names; its blanks there are dropped.
- Area units are guessed from BIS activity (events organized since 2022, board
  membership) of the old users who entered the area's data, matched by email.
  Headquarters events are left out of that measure, since they are national
  and would win every area; headquarters is only the fallback.
- It writes with `bulk_create`, so no `NestBoxHistory` rows: a box's history
  before the import is its checks. Regions and distances are set afterwards.
- Output names old users by id only.

### Sentry
Org `hnuti-brontosaurus`, one project per app: `backend` (Django, also the
game book's server errors), `frontend`, `cookbook`, `nest-boxes` and
`game-book` (browser errors only, through the Sentry loader script in
`game_book/sentry.html`). The SPAs report only when built with
`VITE_ENVIRONMENT` `dev` or `prod`, which CI sets per deploy target, so local
dev sends nothing.

### Deploys and open tabs
Both SPAs are Vite builds whose `assets/` file names are content-hashed, and a
deploy replaces the whole static directory. The production nginx
(`deployments/base/configs/nginx.conf`) therefore serves every `index.html`
with `Cache-Control: no-cache` and `assets/` as `immutable`, and lets a missing
asset 404 instead of falling back to `index.html`. A tab opened before a deploy
still asks for the old chunks: the resulting `vite:preloadError` reloads the
page (`frontend/src/index.tsx`) or, in the cookbook, fully loads the route it
was navigating to (`router.onError` in `cookbook/src/router.js`).

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
Before writing frontend code, read `frontend/docs/style-guide.md` and, for
anything with a form, `frontend/docs/forms.md`. They hold the conventions
reviewers check for (naming, constants, user-facing text, promises, error
handling, form internals). In short:
- One component per file, no default exports
- Use absolute imports
- Style with CSS modules + SCSS
- Forms use react-hook-form + yup validation
- Czech UI strings inline, not added to the generated `translations.ts`
- Cancel resolves `null` rather than rejecting; errors are told apart by class, never by message

When review feedback names a convention the docs don't have yet, add it to
`style-guide.md` or `forms.md`.

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
