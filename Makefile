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
TEST_CLEANUP := $(TEST_COMPOSE) --profile dev --profile frontend --profile cookbook --profile backend down -t 0 -v --remove-orphans

.PHONY: build dev clean test test_backend test_frontend test_cookbook \
        cypress_frontend cypress_cookbook build_frontend build_cookbook \
        install_frontend install_cookbook

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
# profile only brings up nginx + frontend (backend/postgres are gated behind
# the `backend` profile in docker-compose.test.yaml).
test_frontend: install_frontend
	yarn --cwd frontend run test:types
	yarn --cwd frontend run test:unit
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile frontend up --quiet-pull -d
	yarn --cwd frontend run wait-on http-get://localhost:8090
	yarn --cwd frontend run cypress run --config baseUrl=http://localhost:8090 \
		$(if $(spec),--spec '$(spec)',) $(if $(grep),--env grep='$(grep)',)

# Cookbook cypress — REAL e2e against backend + postgres. The `cookbook`
# profile brings up nginx + cookbook + backend + postgres. Chef seeding lives
# in cookbook/cypress.config.js (`before:spec`) so it runs in both `cypress
# run` and `cypress open`.
test_cookbook: install_cookbook
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile cookbook up --quiet-pull -d
	npx --yes wait-on http-get://localhost:8090/api/
	npx --yes wait-on http-get://localhost:8090/cookbook/
	(cd cookbook && npx cypress run \
		--config baseUrl=http://localhost:8090/cookbook/ \
		--env BACKEND_CONTAINER=bis-test-backend,TEST_USER_EMAIL=test@test.local,API_BASE_URL=http://localhost:8090/api/cookbook)

# Interactive cypress for the frontend — same mock-only stack as test_frontend.
cypress_frontend: install_frontend
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile frontend up --quiet-pull -d
	yarn --cwd frontend run wait-on http-get://localhost:8090
	yarn --cwd frontend run cypress open --config baseUrl=http://localhost:8090

# Interactive cypress for the cookbook — same real-backend stack as test_cookbook.
cypress_cookbook: install_cookbook
	trap '$(TEST_CLEANUP)' EXIT
	$(TEST_COMPOSE) --profile cookbook up --quiet-pull -d
	npx --yes wait-on http-get://localhost:8090/api/
	npx --yes wait-on http-get://localhost:8090/cookbook/
	(cd cookbook && npx cypress open \
		--config baseUrl=http://localhost:8090/cookbook/ \
		--env BACKEND_CONTAINER=bis-test-backend,TEST_USER_EMAIL=test@test.local,API_BASE_URL=http://localhost:8090/api/cookbook)

build_frontend:
	docker compose run --rm frontend sh docker-entrypoint.sh build

build_cookbook:
	docker compose run --rm cookbook sh docker-entrypoint.sh build

# Always run yarn install — cypress's postinstall downloads its binary into
# ~/.cache/Cypress (not part of node_modules), so a cached node_modules alone
# is not enough for `cypress run` on a fresh CI runner.
install_frontend:
	yarn --cwd frontend install --frozen-lockfile

install_cookbook:
	yarn --cwd cookbook install --frozen-lockfile
