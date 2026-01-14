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
make dev              # Start all services with live-reload (auto-detects OS)
make backend          # Run backend only
make frontend         # Run frontend only
make clean            # Stop all containers and remove orphans
```

### Testing
```bash
make test             # Run all tests (backend + frontend)
make test_backend     # Run pytest tests only
make test_frontend    # Run Cypress tests only
make open_cypress     # Open Cypress interactive test runner
```

### Backend-specific
```bash
docker exec -it bis-backend sh                          # Shell into backend container
docker exec -it bis-backend python manage.py <command>  # Run Django management command
docker exec -it bis-backend python manage.py migrate    # Apply migrations
docker exec -it bis-backend python manage.py reset      # Import old database
docker exec -it bis-backend python manage.py testing_db # Create test database
```

### Frontend-specific
```bash
yarn --cwd frontend generate-api     # Regenerate RTK-Query types from OpenAPI
yarn --cwd frontend lint             # Run ESLint
yarn --cwd frontend format           # Run Prettier
```

### Pre-commit hooks
Backend uses black + isort for Python formatting (configured in `.pre-commit-config.yaml`).

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
├── src/
│   ├── app/          # Redux store and RTK-Query services
│   ├── pages/        # Public pages (login, event registration, feedback)
│   ├── org/pages/    # Organizer pages (event management)
│   ├── user/pages/   # User profile pages
│   ├── components/   # Reusable React components
│   ├── features/     # Redux slices (auth, form, systemMessage, ui)
│   └── hooks/        # Custom React hooks

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