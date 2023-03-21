FROM amancevice/pandas:1.5.3

RUN mkdir app
WORKDIR /app
RUN mkdir -p /logs/backend


ENV VIRTUAL_ENV=/venv

# 1 gdal
# 2 html to pdf
# 2 postgres
RUN apt update \
 && apt install -y \
    binutils libproj-dev gdal-bin \
    wkhtmltopdf \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/* \
 && python3 -m venv $VIRTUAL_ENV

# this 'activates' virtual environment, since classic activate does not work
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


WORKDIR /app
# Copy files
COPY . .

# default value 8000, can be overwritten in docker-compose build: args: APP_PORT: ...
ARG APP_PORT=8000
EXPOSE ${APP_PORT}

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

CMD ["sh", "docker-entrypoint.sh"]
