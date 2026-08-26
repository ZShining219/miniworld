#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run this script as root." >&2
  exit 1
fi

repo=${MINIWORLD_REPO_DIR:-/srv/miniworld}
install -m 0644 "$repo/deploy/production/miniworld-fitness-backup.service" \
  /etc/systemd/system/miniworld-fitness-backup.service
install -m 0644 "$repo/deploy/production/miniworld-fitness-backup.timer" \
  /etc/systemd/system/miniworld-fitness-backup.timer
install -m 0644 "$repo/deploy/production/fail2ban-caddy-fitness.conf" \
  /etc/fail2ban/filter.d/caddy-fitness.conf
install -m 0644 "$repo/deploy/production/fail2ban-caddy-fitness.local" \
  /etc/fail2ban/jail.d/caddy-fitness.local

systemctl daemon-reload
systemctl enable --now miniworld-fitness-backup.timer
fail2ban-client reload
fail2ban-client status caddy-fitness
