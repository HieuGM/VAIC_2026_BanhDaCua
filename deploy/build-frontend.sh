#!/usr/bin/env bash
#
# deploy/build-frontend.sh — build the CRA bundle and copy it to the nginx docroot.
#
# Builds with REACT_APP_API_BASE_URL=/ so the browser calls /data/v1/* same-origin
# (reaching data-api THROUGH the host nginx proxy — no CORS, no hard-coded host).
#
# Usage:
#   bash deploy/build-frontend.sh                 # -> /var/www/heca/build
#   DEST=/var/www/my-site bash deploy/build-frontend.sh

set -euo pipefail

cd "$(dirname "$0")/.."

DEST="${DEST:-/var/www/heca/build}"

say()  { printf '\n\033[1;34m▶ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✔ %s\033[0m\n' "$*"; }

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node 20 (e.g. via nvm or nodesource)." >&2
  exit 1
fi

say "Install FE deps + build (same-origin API)"
cd frontend
npm ci
REACT_APP_API_BASE_URL=/ npm run build
cd ..

say "Copy bundle to $DEST"
sudo mkdir -p "$DEST"
sudo rsync -a --delete frontend/build/ "$DEST"/
ok "Frontend deployed to $DEST"
echo "Reload nginx if you changed assets:  sudo systemctl reload nginx"
