# Deploy Guide — Hanoi Heart Hospital (Option B: host nginx + docker backend)

VPS: **2 vCPU / 4GB RAM / 40GB SSD / Ubuntu LTS** (`14.225.222.131`).
Domain: `heca.tolalinhne.site` → `14.225.222.131`.

**Architecture** — the VPS already runs nginx on port 80 (multi-site). Docker runs the backend only:

```
browser ──► host nginx :80
              │  serve SPA  /var/www/heca/build   (static files on disk)
              └─ proxy /data/* ──► 127.0.0.1:8081 (data-api container)
                                       └─► chatbot :8000  (internal)
                                              └─► postgres (internal)
```

- Only `data-api` is exposed, and only on `127.0.0.1:8081` (host-local, NOT public).
- `chatbot` + `postgres` are internal to the compose network.
- CI/CD is deferred — images are **built on the VPS**.

---

## 0. Prerequisites (once)

```bash
# Docker + compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker

# Host nginx (if not already installed)
sudo apt-get update && sudo apt-get install -y nginx

# Firewall
sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp
```

DNS: A record `heca.tolalinhne.site` → `14.225.222.131`.
```bash
dig +short heca.tolalinhne.site   # = 14.225.222.131
```

Node (for building the FE on the host):
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 1. Get the code

```bash
git clone https://github.com/HieuGM/VAIC_2026_BanhDaCua.git
cd VAIC_2026_BanhDaCua
git checkout develop        # or the deploy branch until merged
```

## 2. Configure secrets

```bash
# Root compose env (DB password, CORS)
cp .env.example .env
nano .env                   # set DB_PASS, CORS_ALLOWED_ORIGINS

# chatbot RAG/LLM keys (NVIDIA NIM embed + FPT Cloud rerank + OpenAI LLM)
cp chatbot-service/.env.example chatbot-service/.env
nano chatbot-service/.env   # fill NVIDIA_API_KEY, FPT_CLOUD_KEY, OPENAI_API_KEY
```

## 3. Build + start the backend

```bash
bash deploy/deploy.sh       # = docker compose build  +  docker compose up -d  (postgres, data-api, chatbot)
docker compose ps           # all Up/healthy
```

## 4. Ingest the knowledge base (FIRST TIME ONLY)

Embedded Qdrant is **single-process** — ingest with the chatbot server stopped (the
script above starts it, so stop it first, or run ingest before the first `up`):

```bash
docker compose stop chatbot
docker compose run --rm chatbot python -m rag.ingest.run_ingest
docker compose start chatbot
```

Expect `Done: upserted N points; collection 'hospital_kb' now has N.` (N ≠ 0). The
`qdrant_data` volume persists — re-run only when the KB changes (add `--recreate`).

## 5. Build + deploy the frontend

```bash
bash deploy/build-frontend.sh          # npm build -> /var/www/heca/build (same-origin API)
# or a custom docroot: DEST=/var/www/your-site bash deploy/build-frontend.sh
```

## 6. Install the host nginx site

```bash
sudo cp deploy/nginx/heca.tolalinhne.site.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/heca.tolalinhne.site.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```
(If your nginx uses `conf.d/` instead of `sites-enabled/`, copy the file to `/etc/nginx/conf.d/`.)

## 7. Verify

```bash
curl -I http://heca.tolalinhne.site                       # HTTP/1.1 200
curl http://heca.tolalinhne.site/data/v1/chat/sessions    # 200 / []
curl -s http://127.0.0.1:8081/data/v1/chat/sessions       # data-api directly (host-local)
docker compose exec chatbot curl -s localhost:8000/health # {"status":"ok"}
```
Open `http://heca.tolalinhne.site` → chat widget answers (RAG-grounded).

## 8. TLS via certbot (host nginx — your familiar flow)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d heca.tolalinhne.site
# certbot edits the site conf in place (adds 443 ssl) + reloads nginx automatically.
```

## 9. Operations

```bash
docker compose logs -f chatbot          # tail a service
docker compose logs -f data-api
docker compose restart data-api         # restart one service
docker compose down                     # stop backend (keeps volumes)
docker compose down -v                  # STOP + DROP data — destructive

# Update code (backend):  git pull && bash deploy/deploy.sh
# Update frontend:        bash deploy/build-frontend.sh
# Reload nginx (conf/assets changed):  sudo systemctl reload nginx
```

## 10. Troubleshooting

| Symptom | Check |
|---|---|
| 502 Bad Gateway | data-api not up on 127.0.0.1:8081 — `docker compose ps`, `docker compose logs data-api` |
| Chat returns fallback `upstream_error` | `docker compose logs chatbot` — wrong/missing API key, or KB not ingested (step 4) |
| RAG answers empty / "chưa đủ thông tin" | KB not ingested — run step 4, check `N ≠ 0` |
| SPA loads but API 404 | nginx `/data/` proxy missing, or site conf not enabled (`sudo nginx -t`) |
| data-api OOM-killed | raise `JAVA_OPTS -Xmx` in `docker-compose.yml` |
| Port 80 busy | another site on nginx — check `/etc/nginx/sites-enabled/` |

## Notes / out of scope

- **FHIR service** is NOT in this stack. `chatbot` keeps the default `fhir_base_url`
  → FHIR-path queries fail fast, the graph falls back to RAG/public tools. Add a FHIR
  container + `FHIR_BASE_URL` if needed.
- **CI/CD + GHCR** (build off-VPS, pull on VPS) = separate phase.
