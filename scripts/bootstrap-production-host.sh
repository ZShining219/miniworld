#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run this script as root." >&2
  exit 1
fi

if [[ $(. /etc/os-release && printf '%s' "$ID") != ubuntu ]]; then
  echo "This bootstrap supports Ubuntu only." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl gnupg ufw fail2ban git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
printf '%s\n' \
  "Types: deb" \
  "URIs: https://download.docker.com/linux/ubuntu" \
  "Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}" \
  "Components: stable" \
  "Architectures: $(dpkg --print-architecture)" \
  "Signed-By: /etc/apt/keyrings/docker.asc" \
  > /etc/apt/sources.list.d/docker.sources
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker fail2ban

if ! swapon --show=NAME --noheadings | grep -Fxq /swapfile; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || printf '%s\n' '/swapfile none swap sw 0 0' >> /etc/fstab
fi

ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

install -d -m 0755 /etc/miniworld /srv/miniworld
install -d -m 0700 /var/backups/miniworld-fitness

echo "Host bootstrap complete. Create /etc/miniworld/production.env with mode 600 before deployment."
