#!/usr/bin/env bash

set -euo pipefail

UV_CACHE_DIR="${UV_CACHE_DIR:-.cache/uv}"
export UV_CACHE_DIR

uv run --package app pytest backend/tests -q
uv run --package app ruff check backend/app backend/tests
uv run --package app mypy backend/app
uv run --package app ty check backend/app

(
  cd frontend
  bun run build
  bun run lint
  bun run test
)
