#!/usr/bin/env bash
set -euo pipefail

# Open common firewall ports using ufw (Ubuntu) if available

if ! command -v ufw >/dev/null 2>&1; then
  echo "ufw not found; skipping firewall configuration." >&2
  exit 0
fi

sudo ufw allow OpenSSH || true
sudo ufw allow 80/tcp || true
sudo ufw allow 443/tcp || true
sudo ufw allow 8000/tcp || true

# Optional monitoring
sudo ufw allow 3000/tcp || true
sudo ufw allow 9090/tcp || true

echo "Confirming rules:" 
sudo ufw status numbered || true
