#!/usr/bin/env bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$repo_root"

tracked_paths=$(git ls-files)

forbidden_paths=$(printf '%s\n' "$tracked_paths" \
  | grep -E '(^|/)\.env$|(^|/).+\.(db|sqlite|sqlite3|log)$|(^|/)(uploads?|exports?|runtime-data|\.playwright-cli)(/|$)' \
  | grep -v '^apps/miniworld-shell/env/\.env$' \
  || true)
if [[ -n "$forbidden_paths" ]]; then
  echo "Tracked runtime or secret paths are not allowed:" >&2
  printf '%s\n' "$forbidden_paths" >&2
  exit 1
fi

secret_hits=$(git grep -nI -E 'BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}' -- . ':!goal/**' ':!**/*.md' || true)
secret_hits=$(printf '%s\n' "$secret_hits" | grep -Ev 'sk-example-|replace-locally|example|placeholder' || true)
if [[ -n "$secret_hits" ]]; then
  echo "Secret-like values found in tracked source files:" >&2
  printf '%s\n' "$secret_hits" >&2
  exit 1
fi

echo "Sensitive file scan passed: no tracked runtime data, private keys, or non-placeholder token patterns found."
