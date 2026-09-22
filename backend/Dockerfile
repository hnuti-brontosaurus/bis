FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /uvx /bin/

# One dependency is a git+https URL, so resolving the lock file needs git.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/venv
WORKDIR /app
COPY pyproject.toml uv.lock ./
# --compile-bytecode: without it the venv ships ~10 .pyc for ~5900 .py files and
# every container start recompiles the whole dependency tree, which costs ~3.5s
# and is then thrown away with the container's writable layer.
RUN uv sync --frozen --no-install-project --compile-bytecode


FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.10 /uv /uvx /bin/

# Runtime shared libraries only — the toolchain that builds the venv stays in
# the builder stage. pyheif needs nothing here: its wheel bundles its own
# libheif/libde265/libaom under site-packages/pyheif.libs.
# - libgdal36, libgeos-c1t64: GeoDjango dlopens these by path, see settings.py
# - libpango*, fonts-dejavu-*: weasyprint PDF rendering
# - nano, htop: for `docker exec -it bis-backend sh`
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    libgdal36 libgeos-c1t64 \
    libpango-1.0-0 libpangoft2-1.0-0 fonts-dejavu-core fonts-dejavu-mono \
    nano htop \
 && rm -rf /var/lib/apt/lists/*

# Place venv outside /app to avoid conflicts with volume mounts in dev
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="/venv/bin:$PATH"
COPY --from=builder /venv /venv

RUN mkdir -p /app /logs/backend
WORKDIR /app
COPY . .

ARG APP_PORT=8000
EXPOSE ${APP_PORT}

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

CMD ["sh", "docker-entrypoint.sh"]
