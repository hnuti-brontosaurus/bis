FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir -p /app /logs/backend
WORKDIR /app

# System dependencies:
# - binutils, libproj-dev, gdal-bin: GDAL/GEOS/PROJ for PostGIS/GeoDjango
# - postgresql-client: psql used in docker-entrypoint.sh
# - libheif-dev, build-essential, pkg-config: building pyheif from source
# - libpango-1.0-0, libpangoft2-1.0-0: weasyprint runtime deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    binutils libproj-dev gdal-bin \
    postgresql-client \
    libheif-dev build-essential pkg-config git \
    libpango-1.0-0 libpangoft2-1.0-0 \
    nano htop \
 && rm -rf /var/lib/apt/lists/*

# Place venv outside /app to avoid conflicts with volume mounts in dev
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="/venv/bin:$PATH"

# Install dependencies (cached Docker layer - only re-runs when deps change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

WORKDIR /app
COPY . .

ARG APP_PORT=8000
EXPOSE ${APP_PORT}

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

CMD ["sh", "docker-entrypoint.sh"]
