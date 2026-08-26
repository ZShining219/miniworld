#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! -s $1 ]]; then
  echo "Usage: $0 BACKUP.dump" >&2
  exit 2
fi

REPO_DIR=${MINIWORLD_REPO_DIR:-/srv/miniworld}
COMPOSE_FILE="$REPO_DIR/deploy/production/compose.yml"
ENV_FILE=${PRODUCTION_ENV_FILE:-/etc/miniworld/production.env}
RELEASE_SHA=${RELEASE_SHA:-$(cat /srv/miniworld-deployed-sha)}
export RELEASE_SHA PRODUCTION_ENV_FILE="$ENV_FILE"
smoke_db="fitness_restore_$(date +%s)_$$"

cleanup() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
    dropdb -U miniworld --if-exists "$smoke_db" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  createdb -U miniworld "$smoke_db"
db_password=$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db printenv POSTGRES_PASSWORD | tr -d '\r\n')
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm \
  -e "DATABASE_URL=postgresql://miniworld:${db_password}@db:5432/${smoke_db}" \
  api alembic upgrade head
for table in fitness_plan fitness_exercise fitness_session fitness_set; do
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
    pg_restore -U miniworld -d "$smoke_db" --data-only --exit-on-error \
      --table="$table" < "$1"
done

counts=$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  psql -U miniworld -d "$smoke_db" -Atc \
  "select (select count(*) from fitness_plan)||'/'||(select count(*) from fitness_exercise)||'/'||(select count(*) from fitness_session)||'/'||(select count(*) from fitness_set)")
printf 'restore counts plan/exercise/session/set: %s\n' "$counts"
