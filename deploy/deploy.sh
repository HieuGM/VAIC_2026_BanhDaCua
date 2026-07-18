#!/usr/bin/env bash
#
# deploy/deploy.sh — build + start the BACKEND stack (Option B).
# Run from anywhere:  bash deploy/deploy.sh
#
# This script does:  preflight checks -> docker compose build -> docker compose up -d
# for the backend services (postgres + data-api + chatbot).
#
# NOT handled here (do manually — see DEPLOY.md):
#   PHẦN 0  get NVIDIA_API_KEY / FPT_CLOUD_KEY / OPENAI_API_KEY + DNS A record
#   PHẦN 2  create .env + chatbot-service/.env (cp from *.example, fill secrets)
#   PHẦN 4  FIRST-TIME ingest:  docker compose run --rm chatbot python -m rag.ingest.run_ingest
#   PHẦN 5  FE build + copy:    bash deploy/build-frontend.sh
#   PHẦN 6  host nginx site:    cp deploy/nginx/*.conf -> /etc/nginx/sites-available/ + enable
#
# Why no nginx here: the VPS runs nginx on the host (serves /var/www/* + proxies /data
# to 127.0.0.1:8081). nginx is NOT a container in this stack.

set -euo pipefail

# Always run docker compose from the repo root (parent of this script).
cd "$(dirname "$0")/.."

say()  { printf '\n\033[1;34m▶ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m⚠ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✔ %s\033[0m\n' "$*"; }

say "Preflight checks"

if ! command -v docker >/dev/null 2>&1; then
  warn "Docker not found. Install:  curl -fsSL https://get.docker.com | sh"
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  warn "Docker Compose plugin missing. Install Docker (get.docker.com)."
  exit 1
fi
ok "docker $(docker --version | awk '{print $3}' | tr -d ,) + compose $(docker compose version | awk '{print $4}' | tr -d ,)"

if [ ! -f .env ]; then
  warn ".env missing. Run:  cp .env.example .env   (then set DB_PASS)"
  exit 1
fi
ok ".env present"

if [ ! -f chatbot-service/.env ]; then
  warn "chatbot-service/.env missing. Run:"
  warn "  cp chatbot-service/.env.example chatbot-service/.env"
  warn "then fill NVIDIA_API_KEY / FPT_CLOUD_KEY / OPENAI_API_KEY."
  exit 1
fi
ok "chatbot-service/.env present"

say "Build backend images (postgres is a pulled image; data-api + chatbot build, ~10–15 min first run)"
docker compose build

say "Start backend stack"
docker compose up -d --remove-orphans

say "Status"
docker compose ps

printf '\n'
ok "Backend is up."
printf '  data-api (host-local): http://127.0.0.1:8081\n'
printf '  Logs                 : docker compose logs -f chatbot\n'
warn "Next (see DEPLOY.md):"
warn "  1. Ingest KB (first time): docker compose run --rm chatbot python -m rag.ingest.run_ingest"
warn "  2. Build + copy FE       : bash deploy/build-frontend.sh"
warn "  3. Enable host nginx site: sudo cp deploy/nginx/*.conf /etc/nginx/sites-available/ && sudo ln -sf /etc/nginx/sites-available/heca.tolalinhne.site.conf /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx"
