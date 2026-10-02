#!/usr/bin/env bash
set -Eeuo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

base_ref=${MINIWORLD_BASE_REF:-origin/main}
branch=$(git branch --show-current)
if [[ -z "$branch" || "$branch" == "main" || "$branch" != codex/* ]]; then
  echo "Preflight requires a codex/* implementation branch; got '$branch'." >&2
  exit 2
fi
if ! git rev-parse --verify "$base_ref^{commit}" >/dev/null 2>&1; then
  echo "Base ref '$base_ref' is unavailable; run 'git fetch origin' first." >&2
  exit 2
fi

git diff --check
./scripts/ci/check-sensitive-files.sh

changed_paths=$( {
  git diff --name-only "$base_ref"...HEAD
  git diff --name-only
  git diff --cached --name-only
  git ls-files --others --exclude-standard
} | sed '/^$/d' | sort -u )
if [[ -z "$changed_paths" ]]; then
  echo "Preflight found no changes relative to $base_ref." >&2
  exit 2
fi
printf 'Preflight scope (%s):\n%s\n' "$base_ref" "$changed_paths"

has_path() {
  grep -Eq "(^|/)${1}(/|$)" <<<"$changed_paths"
}
has_file() {
  grep -Eq "(^|/)${1}$" <<<"$changed_paths"
}

if has_path backend || has_file pyproject.toml || has_file uv.lock; then
  : "${UV_CACHE_DIR:=.cache/uv}"
  export UV_CACHE_DIR
  uv run --locked --package app pytest backend/tests -q
  uv run --locked --package app ruff check backend/app backend/tests
  uv run --locked --package app mypy backend/app
  uv run --locked --package app ty check backend/app
fi

if has_path frontend || has_file package.json || has_file bun.lock; then
  bun install --frozen-lockfile
  scripts/fetch-radar-demo-map.sh
  (cd frontend && bun run build && bun run lint && bun run test)
fi

if has_path apps/miniworld-shell || has_file pnpm-lock.yaml; then
  (cd apps/miniworld-shell && pnpm install --frozen-lockfile --ignore-scripts && pnpm init-baseFiles && pnpm build:h5 && pnpm type-check && pnpm test:run)
fi

if has_file compose.yml || has_path deploy/production || has_path scripts/ci; then
  ./scripts/test-production-deployment.sh
fi

if [[ ${MINIWORLD_RUN_INTEGRATION:-0} == 1 ]]; then
  ./scripts/test.sh
fi

echo "Agent delivery preflight passed. Ready for an allowlisted commit and routine code push."
