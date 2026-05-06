#!/bin/sh

set -e
yarn install --frozen-lockfile

# Commands available using `docker compose run cookbook [COMMAND]`
case "$1" in
    node)
        node
    ;;
    test)
        yarn test
    ;;
    check)
        # Used by `make test_cookbook` — unit tests inside the container so
        # no host node is needed. Cypress e2e runs in a separate container.
        yarn run test:unit
    ;;
    dev)
        echo "Running Server..."
        yarn dev
    ;;
    *)
        yarn build
    ;;
esac
