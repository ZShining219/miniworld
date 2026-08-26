#!/usr/bin/env bash
set -Eeuo pipefail

REPO_DIR=${MINIWORLD_REPO_DIR:-/srv/miniworld}
COMPOSE_FILE="$REPO_DIR/deploy/production/compose.yml"
ENV_FILE=${PRODUCTION_ENV_FILE:-/etc/miniworld/production.env}
BACKUP_DIR=${FITNESS_BACKUP_DIR:-/var/backups/miniworld-fitness}
RELEASE_SHA=${RELEASE_SHA:-$(cat /srv/miniworld-deployed-sha 2>/dev/null || printf 'unknown')}
export RELEASE_SHA PRODUCTION_ENV_FILE="$ENV_FILE"

install -d -m 0700 "$BACKUP_DIR"
backup="$BACKUP_DIR/fitness-$(date -u +%Y%m%dT%H%M%SZ)-${RELEASE_SHA:0:12}.dump"
umask 077

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  pg_dump -U miniworld -d miniworld --format=custom \
    --table=fitness_plan --table=fitness_exercise \
    --table=fitness_session --table=fitness_set > "$backup"

test -s "$backup"
find "$BACKUP_DIR" -type f -name 'fitness-*.dump' -mtime +7 -delete
printf '%s\n' "$backup"
