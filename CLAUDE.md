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
make test_frontend     # Frontend Cypress — FULLY MOCKED (cy.intercept). Containerized cypress.
make test_cookbook     # Cookbook Cypress — REAL e2e against backend + postgres. Containerized cypress.
make cypress_frontend  # Interactive frontend Cypress (containerized; uses WSLg / X11 to show GUI).
make cypress_cookbook  # Interactive cookbook Cypress (containerized; uses WSLg / X11 to show GUI).
```

Test stack profiles (`docker-compose.test.yaml`):
- `frontend` profile → nginx + frontend (no backend/DB) — used by `test_frontend` / `cypress_frontend`.
- `cookbook` profile → nginx + cookbook + backend + postgres — used by `test_cookbook` / `cypress_cookbook`.
- `backend` profile → backend + postgres (+ nginx) — used by `test_backend`.
- `cypress` profile → cookbook cypress runner. Built from `cookbook/cypress.Dockerfile` (cypress/included + docker CLI). Started on demand via `docker compose run --rm cypress`, never by `up`.
- `cypress-frontend` profile → frontend cypress runner. Reuses the same `bis-cypress` image, mounts `frontend/` instead, no docker socket. Started via `docker compose run --rm cypress-frontend`.

Both cypress runners are fully containerized — no host cypress binary is needed. They join the test docker network so `baseUrl` is `http://nginx/...`, mount `/tmp/.X11-unix` + `/mnt/wslg` (forwarding `DISPLAY` / `WAYLAND_DISPLAY` / `PULSE_SERVER`) so `cypress open` shows up via WSLg on Windows or native X11 on Linux.

Frontend type-check + unit tests also run in-container — `make test_frontend` invokes `docker compose run --rm frontend sh docker-entrypoint.sh ci` (see `frontend/docker-entrypoint.sh` for the `ci` mode), so no host yarn install is needed at all.

Cookbook seeding is exposed as a TEST-only Django endpoint at `POST /api/cookbook/testing/seed/` (`api/cookbook/views/testing.py`) — gated by `settings.TEST` so it 404s in production. The `before:spec` hook in `cookbook/cypress.config.js` `fetch`es it instead of shelling out to `docker exec`, which lets the cypress container stay minimal (no docker CLI, no socket mount, no docker-group GID handling).

Cookbook chef seeding lives in `cookbook/cypress.config.js` (`before:spec` hook), not in the Makefile, so interactive runs seed too. It calls `python manage.py testing_db cookbook`, which is idempotent.

Cookbook tests rely on real backend state. The `testing_db cookbook` seed provides everything specs need (chef + canonical recipe with photo); specs talk to the same HTTP API the SPA uses, not the ORM directly. Mutations within a test use uniquely-tagged values (e.g. `cypress-${Date.now()}`) so the assertion only depends on what *that* test wrote — not on global counts. The test DB volume is wiped on teardown.

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

### React/TypeScript
- One component per file, no default exports
- Use absolute imports
- Style with CSS modules + SCSS
- Forms use react-hook-form + yup validation

### Commit Messages
- Capital first letter, imperative style, no trailing period
- Follow with empty line, then details
- PRs with many small commits get squashed on merge

## Claude instructions
- When implementing new code / fixing a command, you are encouraged to update and CLAUDE.md with new findings about the repository to improve it
- No defensive fixes. Fix the root cause, keep it DRY, fail fast — no consumer-side guards or sanitizers for upstream bugs.
