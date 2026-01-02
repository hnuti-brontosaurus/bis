FROM node:25-alpine

RUN mkdir app
WORKDIR /app

EXPOSE 3001

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

CMD ["sh", "docker-entrypoint.sh"]
