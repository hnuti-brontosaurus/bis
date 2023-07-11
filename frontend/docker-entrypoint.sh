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
    dev)
        echo "Running Server..."
        yarn start
    ;;
    *)
        yarn build
    ;;
esac
