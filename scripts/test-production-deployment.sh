#!/usr/bin/env bash
set -Eeuo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo"

for script in scripts/bootstrap-production-host.sh scripts/configure-production-secrets.sh scripts/install-production-operations.sh scripts/backup-production.sh \
  scripts/export-fitness-data.sh scripts/restore-production-smoke.sh \
  scripts/import-fitness-data.sh scripts/deploy-production.sh; do
  bash -n "$script"
done

grep -Fq "VITE_SERVER_BASEURL = '/fg-api'" apps/miniworld-shell/env/.env.production
grep -Fq '@fitness_api path /fg-api/api/v1/fitness /fg-api/api/v1/fitness/*' deploy/production/Caddyfile
grep -Fq '@blocked_api path /fg-api /fg-api/* /api /api/* /docs /docs/*' deploy/production/Caddyfile
grep -Fq 'FITNESS_AGENT_PROVIDER: ${FITNESS_AGENT_PROVIDER:-deepseek}' deploy/production/compose.yml
grep -Fq 'FITNESS_AGENT_API_KEY: ${FITNESS_AGENT_API_KEY:-}' deploy/production/compose.yml
grep -Fq 'FITNESS_AGENT_MODEL: ${FITNESS_AGENT_MODEL:-deepseek-chat}' deploy/production/compose.yml
grep -Fq 'FITNESS_AGENT_TIMEOUT_SECONDS: ${FITNESS_AGENT_TIMEOUT_SECONDS:-30}' deploy/production/compose.yml
! grep -Eq 'ports:.*(5432|8000)' deploy/production/compose.yml
grep -Fq 'if RELEASE_SHA=$running_sha docker compose --env-file "$env_file"' scripts/deploy-production.sh
grep -Fq 'RELEASE_SHA=$running_sha PRODUCTION_ENV_FILE=$env_file' scripts/deploy-production.sh

echo "Production deployment static checks passed."
