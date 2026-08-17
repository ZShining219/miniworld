FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.11.24 /uv /uvx /bin/

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="/app/backend"

COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/pyproject.toml

RUN uv sync --frozen --no-install-workspace --package app

COPY backend backend

WORKDIR /app/backend
EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
