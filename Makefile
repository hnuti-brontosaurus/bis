SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.ONESHELL:

# run containers as the host user so files written from inside (migrations, build output)
# are owned by the host user, not root
export UID := $(shell id -u)
export GID := $(shell id -g)

CLEANUP := docker compose down -t 0 --remove-orphans

# Isolated test stack — separate compose project (`bis-test`), separate
# network and DB volume, no shared host ports. All test targets can run
# while `make dev` is up.
TEST_PROJECT := bis-test
TEST_FILES := -f docker-compose.yaml -f docker-compose.test.yaml
TEST_COMPOSE := docker compose -p $(TEST_PROJECT) $(TEST_FILES)
TEST_CLEANUP := $(TEST_COMPOSE) --profile dev --profile frontend --profile cookbook --profile backend --profile cypress --profile cypress-frontend down -t 0 -v --remove-orphans

.PHONY: build dev clean test test_backend test_frontend test_cookbook \
        cypress_frontend cypress_cookbook build_frontend build_cookbook

build: .env
	docker compose build

.env:
	cp .example.env .env

dev: clean
	trap '$(CLEANUP)' EXIT
	docker compose up

clean:
	$(CLEANUP)

test: test_backend test_frontend test_cookbook

# Backend pytest. Brings up only postgres + backend in the bis-test project,
# runs the entrypoint's `test` mode (pytest), tears down with the volume.
test_backend:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) run --rm --quiet-pull backend sh docker-entrypoint.sh test

# Frontend cypress — FULLY MOCKED. Specs use cy.intercept for every API call,
# so no backend, postgres, or seeded user is needed. The `frontend` compose
# profile only brings up nginx + frontend; cypress itself runs in the upstream
# cypress/included image. Type-check and unit tests also run inside the
# frontend container — no host yarn needed.
test_frontend:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) run --rm frontend sh docker-entrypoint.sh ci
	$(TEST_COMPOSE) --profile frontend up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile frontend --profile cypress-frontend run --rm cypress-frontend run $(if $(spec),--spec '$(spec)',) $(if $(grep),--env grep='$(grep)',)

# Cookbook cypress — REAL e2e against backend + postgres. The `cookbook`
# profile brings up nginx + cookbook + backend + postgres. Cypress itself
# runs in a third container (`cypress` profile, upstream cypress/included
# image) on the same docker network — no host Node toolchain involved.
# Chef seeding lives in cookbook/cypress.config.js (`before:spec`) and
# fetches `/api/cookbook/testing/seed/` directly.
test_cookbook:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile cookbook up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile cookbook --profile cypress run --rm cypress run $(if $(spec),--spec '$(spec)',) $(if $(grep),--env grep='$(grep)',)

# Interactive cypress for the frontend. WSLg / X11 socket forwarding gives
# the GUI a Windows window like any other WSL app.
cypress_frontend:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile frontend up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile frontend --profile cypress-frontend run --rm cypress-frontend open --project /e2e

# Interactive cypress for the cookbook — same real-backend stack as test_cookbook.
# The cypress container forwards X11 / Wayland sockets to the host (WSLg on
# Windows, native X11 on Linux) so the Cypress GUI shows up like any other
# WSL/Linux app.
cypress_cookbook:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile cookbook up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile cookbook --profile cypress run --rm cypress open --project /e2e

build_frontend:
	docker compose run --rm -e VITE_ENVIRONMENT=$${VITE_ENVIRONMENT:-dev} frontend sh docker-entrypoint.sh build

build_cookbook:
	docker compose run --rm cookbook sh docker-entrypoint.sh build
