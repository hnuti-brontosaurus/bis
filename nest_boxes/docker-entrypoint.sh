#!/bin/sh

set -e
npm install --no-audit --no-fund

case "$1" in
    check)
        npm run test:unit
    ;;
    dev)
        npm run dev
    ;;
    *)
        npm run build
    ;;
esac
