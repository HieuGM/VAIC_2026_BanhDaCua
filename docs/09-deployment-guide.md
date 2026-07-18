# 09 — Deployment Guide

> **Option B (2026-07-18): host nginx + docker backend.** Đã LIVE `https://heca.tolalinhne.site`.
> Runbook chi tiết từng lệnh: [`../DEPLOY.md`](../DEPLOY.md) (root). File này = tóm tắt kiến trúc.
> Cập nhật: 2026-07-18 · Trạng thái: **Deployed (demo)**.

## Kiến trúc — Option B
VPS đã chạy nginx host (multi-site) port 80. Docker chỉ chạy backend; FE host-built:

```
browser ──HTTPS──► host nginx :80
              │  serve SPA /var/www/heca/build   (static, rsync từ frontend/build)
              └─ proxy /data/* ──► 127.0.0.1:8081 (data-api container, host-local only)
                                       └─► chatbot :8000  (internal)
                                              └─► postgres (internal)
```

- **Chỉ `data-api` expose**, và chỉ `127.0.0.1:8081` (không public). `chatbot` + `postgres` nội bộ compose network.
- **FE không docker** — build CRA (`REACT_APP_API_BASE_URL=/` same-origin) → `rsync` vào `/var/www/heca/build`. Không CORS trong prod path.
- TLS: certbot trên host nginx (Cloudflare edge ở demo). CI/CD = phase kế tiếp (deferred).

## Artifact deploy-infra (PR #6, merged `bd6eef8`)
| File | Vai trò |
|---|---|
| `docker-compose.yml` | 3 service: postgres (`postgres:16-alpine`, tune `shared_buffers`) + data-api (build, `127.0.0.1:8081`, `JAVA_OPTS -Xmx256m`) + chatbot (build root context, volume `qdrant_data`) |
| `chatbot-service/Dockerfile` | multistage `python:3.11-slim`, venv `/opt/venv`, non-root `chatbot:1001`, HEALTHCHECK `/health`, bake `data/` KB cho ingest |
| `data-api/Dockerfile` | multistage `maven:3.9-temurin-21` build → `eclipse-temurin:21-jre` runtime, non-root `hanoiheart:1001` |
| `deploy/deploy.sh` | preflight → `docker compose build` + `up -d` (backend only) |
| `deploy/build-frontend.sh` | `npm ci` + build (`REACT_APP_API_BASE_URL=/`) → `rsync` vào `/var/www/heca/build` |
| `deploy/nginx/heca.tolalinhne.site.conf` | host nginx site: SPA root + `location /data/` proxy `127.0.0.1:8081` |
| `DEPLOY.md` (root) | runbook đầy đủ (PHẦN 0–10 + troubleshooting) |
| `.env.example` + `chatbot-service/.env.example` | DB pass + RAG/LLM keys template |

## VPS config (2 vCPU / 4GB RAM / 40GB SSD / Ubuntu LTS)
- `14.225.222.131`, domain `heca.tolalinhne.site`.
- Runtime RAM thực đo ~1.8/3.8GB: torch/sentence-transformers import **lazy** (chỉ load khi `provider=local`); prod dùng hosted API (NVIDIA NIM `bge-m3` embed + FPT Cloud `bge-reranker-v2-m3`) → RAM thấp.

## Known issue (deferred → CI/CD)
`requirements.txt:11` (`sentence-transformers`) kéo `torch` → image build tải cả stack **CUDA/nvidia (~3–4GB)** dù VPS không GPU. Image ~4–5GB, build ~40ph. Fix (phase CI/CD): CPU-only torch (`pip install --index-url https://download.pytorch.org/whl/cpu torch` trước `-r requirements.txt`) → image ~1.5GB, build 5ph. Chi tiết: `11` [Unreleased].

## Liên quan
- [`../DEPLOY.md`](../DEPLOY.md) · [[05-system-architecture]] §6 · [[10-development-roadmap]] · [[11-project-changelog]]
