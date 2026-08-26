#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! -s $1 ]]; then
  echo "Usage: $0 FITNESS.dump" >&2
  exit 2
fi

REPO_DIR=${MINIWORLD_REPO_DIR:-/srv/miniworld}
COMPOSE_FILE="$REPO_DIR/deploy/production/compose.yml"
ENV_FILE=${PRODUCTION_ENV_FILE:-/etc/miniworld/production.env}
RELEASE_SHA=${RELEASE_SHA:-$(cat /srv/miniworld-deployed-sha)}
export RELEASE_SHA PRODUCTION_ENV_FILE="$ENV_FILE"

existing=$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  psql -U miniworld -d miniworld -Atc \
  "select (select count(*) from fitness_plan)+(select count(*) from fitness_exercise)+(select count(*) from fitness_session)+(select count(*) from fitness_set)")
if [[ $existing != 0 ]]; then
  echo "Production Fitness tables are not empty; refusing to import." >&2
  exit 1
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  pg_restore -U miniworld -d miniworld --data-only --exit-on-error < "$1"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  psql -U miniworld -d miniworld -Atc \
  "select 'plan='||(select count(*) from fitness_plan)||',exercise='||(select count(*) from fitness_exercise)||',session='||(select count(*) from fitness_session)||',set='||(select count(*) from fitness_set)||',active='||(select count(*) from fitness_session where status='ACTIVE')"
