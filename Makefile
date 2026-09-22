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
TEST_CLEANUP := $(TEST_COMPOSE) --profile dev --profile frontend --profile cookbook --profile backend --profile playwright --profile playwright-frontend down -t 0 -v --remove-orphans

.PHONY: build dev clean test test_backend test_frontend test_cookbook \
        e2e_frontend e2e_cookbook build_frontend build_cookbook

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

# Frontend e2e — FULLY MOCKED. Specs stub every API call with page.route,
# so no backend, postgres, or seeded user is needed. The `frontend` compose
# profile only brings up nginx + frontend; Playwright itself runs in the
# upstream mcr.microsoft.com/playwright image. Type-check and unit tests also
# run inside the frontend container — no host yarn needed.
#
# `spec=` filters by file, `grep=` by title, `workers=` overrides parallelism.
test_frontend:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) run --rm frontend sh docker-entrypoint.sh check
	$(TEST_COMPOSE) --profile frontend up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile frontend --profile playwright-frontend run --rm $(if $(workers),-e PW_WORKERS=$(workers),) playwright-frontend test $(spec) $(if $(grep),--grep '$(grep)',)

# Cookbook e2e — REAL e2e against backend + postgres. The `cookbook` profile
# brings up nginx + cookbook + backend + postgres. Playwright runs in a third
# container on the same docker network — no host Node toolchain involved.
# Seeding lives in cookbook/e2e/global-setup.js, which POSTs to
# /api/cookbook/testing/seed/.
test_cookbook:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) run --rm cookbook sh docker-entrypoint.sh check
	$(TEST_COMPOSE) --profile cookbook up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile cookbook --profile playwright run --rm $(if $(workers),-e PW_WORKERS=$(workers),) playwright test $(spec) $(if $(grep),--grep '$(grep)',)

# Interactive Playwright for the frontend. UI mode is served over HTTP, so
# open http://localhost:8101 once the container reports it is listening.
e2e_frontend:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile frontend up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile frontend --profile playwright-frontend run --rm --service-ports playwright-frontend test --ui --ui-host=0.0.0.0 --ui-port=8100

# Interactive Playwright for the cookbook — same real-backend stack as
# test_cookbook. Open http://localhost:8100.
e2e_cookbook:
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile cookbook up --quiet-pull --wait -d
	$(TEST_COMPOSE) --profile cookbook --profile playwright run --rm --service-ports playwright test --ui --ui-host=0.0.0.0 --ui-port=8100

build_frontend:
	docker compose run --rm -e VITE_ENVIRONMENT=$${VITE_ENVIRONMENT:-dev} frontend sh docker-entrypoint.sh build

build_cookbook:
	docker compose run --rm cookbook sh docker-entrypoint.sh build
