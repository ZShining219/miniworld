#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 OUTPUT.dump" >&2
  exit 2
fi

output=$1
if [[ -e $output ]]; then
  echo "Refusing to overwrite existing file: $output" >&2
  exit 1
fi

if command -v docker-compose >/dev/null 2>&1; then
  compose=(docker-compose)
else
  compose=(docker compose)
fi

umask 077
"${compose[@]}" exec -T db pg_dump -U miniworld -d miniworld --format=custom \
  --table=fitness_plan --table=fitness_exercise \
  --table=fitness_session --table=fitness_set > "$output"
test -s "$output"
printf '%s\n' "$output"
