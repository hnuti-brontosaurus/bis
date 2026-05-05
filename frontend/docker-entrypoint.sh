#!/bin/sh

set -e

yarn install --frozen-lockfile

# Commands available using `docker-compose run frontend [COMMAND]`
case "$1" in
    node)
        node
    ;;
    test)
        yarn test
    ;;
    ci)
        # Used by `make test_frontend` — type-check + unit tests inside the
        # container so no host node is needed.
        yarn run test:types
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
