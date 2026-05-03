FROM cypress/included:15.14.2

# Cookbook seed runs via an HTTP endpoint on the backend (api/cookbook/testing/seed/),
# not `docker exec` — so this image needs no extra tools beyond what cypress/included
# already provides.

COPY cypress-entrypoint.sh /usr/local/bin/cypress-entrypoint.sh
RUN chmod +x /usr/local/bin/cypress-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/cypress-entrypoint.sh"]
CMD ["run"]
