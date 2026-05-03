#!/bin/sh
set -e

# Wait for nginx + dependencies to respond before launching cypress. Replaces
# the host-side `npx wait-on` calls the Makefile used to do.
#
# WAIT_FOR_URLS is a space-separated list of URLs to probe. Defaults to the
# cookbook stack (frontend SPA + backend API via nginx). The frontend profile
# (mock-only) overrides it to just nginx root.
: "${WAIT_FOR_URLS:=http://nginx/api/ http://nginx/cookbook/}"

echo "cypress: waiting for $WAIT_FOR_URLS ..."
for url in $WAIT_FOR_URLS; do
  until wget -q -O /dev/null "$url"; do sleep 1; done
done
echo "cypress: ready."

exec cypress "$@"
