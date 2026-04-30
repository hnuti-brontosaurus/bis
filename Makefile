SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.ONESHELL:

# run containers as the host user so files written from inside (migrations, build output)
# are owned by the host user, not root
export UID := $(shell id -u)
export GID := $(shell id -g)

# `--profile dev` makes `down` see profiled services too (backend/frontend/cookbook),
# so they're cleaned up along with nginx/postgres. Without it compose only acts on
# services that have no profile, leaving stale profiled containers behind.
CLEANUP := docker compose --profile dev down -t 0 --remove-orphans
TEST_FILES := -f docker-compose.yaml -f docker-compose.override.yaml -f docker-compose.test.yaml

.PHONY: build dev backend frontend clean test test_backend test_frontend test_e2e \
        open_cypress init_test_db build_frontend build_cookbook _prepare_test_env

build: .env
	docker compose build

.env:
	cp .example.env .env

dev: clean
	trap '$(CLEANUP)' EXIT
	docker compose --profile dev up

backend:
	trap '$(CLEANUP)' EXIT
	docker compose --profile backend up

frontend:
	trap '$(CLEANUP)' EXIT
	docker compose --profile frontend up

clean:
	$(CLEANUP)

test: test_backend test_frontend

test_backend: _prepare_test_env
	trap '$(CLEANUP)' EXIT
	docker compose $(TEST_FILES) run --rm --quiet-pull backend sh docker-entrypoint.sh test

test_frontend: node_modules/cypress/bin/cypress
	yarn --cwd frontend run test:types
	yarn --cwd frontend run test:unit
	trap '$(CLEANUP)' EXIT
	docker compose --profile frontend $(TEST_FILES) up --quiet-pull -d
	yarn --cwd frontend run wait-on http-get://localhost:3000
	yarn --cwd frontend run e2e:ci $(if $(spec),--spec '$(spec)',) $(if $(grep),--env grep='$(grep)',)

test_e2e: node_modules/cypress/bin/cypress _prepare_test_env
	trap '$(CLEANUP)' EXIT
	docker compose --profile dev $(TEST_FILES) up --quiet-pull -d
	yarn --cwd frontend run wait-on http-get://localhost/api/
	yarn --cwd frontend run wait-on http-get://localhost:3000
	yarn --cwd frontend run cypress run

open_cypress: node_modules/cypress/bin/cypress _prepare_test_env
	trap '$(CLEANUP)' EXIT
	docker compose --profile dev $(TEST_FILES) up --quiet-pull -d
	yarn --cwd frontend run wait-on http-get://localhost/api/
	yarn --cwd frontend run cypress open

init_test_db:
	docker compose run --rm backend sh docker-entrypoint.sh manage migrate
	docker compose run --rm backend sh docker-entrypoint.sh manage testing_db

build_frontend:
	docker compose run --rm frontend sh docker-entrypoint.sh build

build_cookbook:
	docker compose run --rm cookbook sh docker-entrypoint.sh build

node_modules/cypress/bin/cypress:
	yarn --cwd frontend install --frozen-lockfile

_prepare_test_env:
	rm -Rf ./*data_test
	docker volume rm -f postgresqldata_test
	docker volume create postgresqldata_test
