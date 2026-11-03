FROM node:26-alpine

RUN mkdir app
WORKDIR /app

EXPOSE 3003

# node:alpine sets ENTRYPOINT=["docker-entrypoint.sh"]; drop it so the script
# copied in below gets the verb in $1, like the cookbook and frontend images.
ENTRYPOINT []

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

CMD ["sh", "docker-entrypoint.sh"]
