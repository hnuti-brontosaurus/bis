FROM node:25-alpine

RUN mkdir app
WORKDIR /app

EXPOSE 3001

# node:alpine sets ENTRYPOINT=["docker-entrypoint.sh"] — drop it so the
# script we COPY in is invoked once with the verb in $1, matching the
# frontend image's pattern.
ENTRYPOINT []

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

CMD ["sh", "docker-entrypoint.sh"]
