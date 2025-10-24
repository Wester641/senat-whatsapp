# ─────────────────────────────────────────────
# 🚧 Stage 1: Builder - Install dependencies
# ─────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock* ./

# Install dependencies including psycopg2
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY . .

RUN uv run python manage.py collectstatic --noinput

# ─────────────────────────────────────────────
# 🐳 Stage 2: Runtime - Slim final image
# ─────────────────────────────────────────────
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 django && \
    mkdir -p /app/logs /app/media && \
    chown -R django:django /app

WORKDIR /app

COPY --from=builder --chown=django:django /app/.venv /app/.venv
COPY --chown=django:django manage.py ./
COPY --chown=django:django settings ./settings
COPY --chown=django:django legal_form ./legal_form
COPY --from=builder --chown=django:django /app/staticfiles ./staticfiles
COPY --chown=django:django entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=settings.settings

USER django

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/service-types/ || exit 1

ENTRYPOINT ["./entrypoint.sh"]