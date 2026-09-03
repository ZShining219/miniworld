#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run this script as root." >&2
  exit 1
fi
if [[ $# -ne 1 || ! $1 =~ ^[0-9a-f]{40}$ ]]; then
  echo "Usage: $0 <40-character-lowercase-git-sha>" >&2
  exit 2
fi

target_sha=$1
repo=${MINIWORLD_REPO_DIR:-/srv/miniworld}
env_file=${PRODUCTION_ENV_FILE:-/etc/miniworld/production.env}
compose_file="$repo/deploy/production/compose.yml"
deployed_file=/srv/miniworld-deployed-sha
previous_sha=$(cat "$deployed_file" 2>/dev/null || true)
git_repo=(git -c "safe.directory=$repo" -C "$repo")
running_sha=$target_sha
if [[ $previous_sha =~ ^[0-9a-f]{40}$ ]]; then
  running_sha=$previous_sha
fi

test -f "$env_file"
test "$(stat -c '%a' "$env_file")" = 600

if [[ ! -d $repo/.git ]]; then
  install -d -m 0755 "$repo"
  git -C "$repo" init
fi
if ! "${git_repo[@]}" remote get-url origin >/dev/null 2>&1; then
  "${git_repo[@]}" remote add origin https://github.com/ZShining219/miniworld.git
fi

"${git_repo[@]}" fetch --prune origin \
  "+refs/heads/codex/bootstrap-langgraph:refs/remotes/origin/codex/bootstrap-langgraph"
"${git_repo[@]}" cat-file -e "${target_sha}^{commit}"
"${git_repo[@]}" merge-base --is-ancestor "$target_sha" origin/codex/bootstrap-langgraph

rollback() {
  status=$?
  if [[ $status -ne 0 && $previous_sha =~ ^[0-9a-f]{40}$ ]]; then
    echo "Deployment failed; restoring application commit $previous_sha (database is not downgraded)." >&2
    "${git_repo[@]}" checkout --detach --force "$previous_sha"
    export RELEASE_SHA=$previous_sha PRODUCTION_ENV_FILE=$env_file
    docker compose --env-file "$env_file" -f "$compose_file" up -d --no-build
  fi
  exit "$status"
}
trap rollback EXIT

if RELEASE_SHA=$running_sha docker compose --env-file "$env_file" \
  -f "$compose_file" ps -q db 2>/dev/null | grep -q .; then
  RELEASE_SHA=$running_sha PRODUCTION_ENV_FILE=$env_file \
    "$repo/scripts/backup-production.sh"
fi

"${git_repo[@]}" checkout --detach --force "$target_sha"
export RELEASE_SHA=$target_sha PRODUCTION_ENV_FILE=$env_file
docker compose --env-file "$env_file" -f "$compose_file" build api
docker compose --env-file "$env_file" -f "$compose_file" build web
docker compose --env-file "$env_file" -f "$compose_file" up -d --remove-orphans

for _ in $(seq 1 60); do
  if docker compose --env-file "$env_file" -f "$compose_file" exec -T api \
      curl -fsS http://127.0.0.1:8000/api/v1/health >/dev/null; then
    break
  fi
  sleep 2
done
docker compose --env-file "$env_file" -f "$compose_file" exec -T api \
  curl -fsS http://127.0.0.1:8000/api/v1/health >/dev/null

public_host=$(docker compose --env-file "$env_file" -f "$compose_file" exec -T web printenv PUBLIC_HOST | tr -d '\r\n')
for _ in $(seq 1 60); do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "https://${public_host}/" || true)
  [[ $code == 401 ]] && break
  sleep 2
done
test "$(curl -sS -o /dev/null -w '%{http_code}' "https://${public_host}/")" = 401

printf '%s\n' "$target_sha" > "$deployed_file"
chmod 0644 "$deployed_file"
trap - EXIT
echo "Deployed $target_sha; unauthenticated public access correctly returns 401."
