#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $(uname -s) != Darwin ]]; then
  echo "This helper currently uses the macOS hidden-password dialog." >&2
  exit 1
fi

password=$(osascript -e 'text returned of (display dialog "设置 Fitness 手机访问密码" default answer "" with hidden answer buttons {"取消", "继续"} default button "继续")')
confirm=$(osascript -e 'text returned of (display dialog "再次输入 Fitness 手机访问密码" default answer "" with hidden answer buttons {"取消", "继续"} default button "继续")')
if [[ -z $password || $password != "$confirm" ]]; then
  echo "Passwords are empty or do not match." >&2
  exit 1
fi

hash=$(printf '%s\n' "$password" | docker run --rm -i caddy:2.10.2-alpine \
  caddy hash-password --algorithm bcrypt)
unset password confirm
db_password=$(openssl rand -hex 32)
temp_file=$(mktemp)
cleanup() {
  rm -f "$temp_file"
}
trap cleanup EXIT
chmod 600 "$temp_file"
printf '%s\n' \
  "PUBLIC_HOST=103-52-153-212.sslip.io" \
  "POSTGRES_DB=miniworld" \
  "POSTGRES_USER=miniworld" \
  "POSTGRES_PASSWORD='$db_password'" \
  "BASIC_AUTH_HASH='$hash'" > "$temp_file"
unset db_password hash

ssh miniworld-prod-root 'install -d -m 0755 /etc/miniworld'
scp -q "$temp_file" miniworld-prod-root:/etc/miniworld/production.env
ssh miniworld-prod-root 'chown root:root /etc/miniworld/production.env && chmod 600 /etc/miniworld/production.env'
echo "Production secrets installed with mode 600; no plaintext password was saved."
