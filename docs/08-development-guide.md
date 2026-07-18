# 08 — Development Guide

> **STUB — chưa có nội dung.**
> Cập nhật: 2026-07-17 · Trạng thái: TODO.

## Khung cần điền
- [ ] **Local setup**: prerequisites (Node 20, Python 3.12, Docker), `docker compose up`, env vars (`.env.example`).
- [ ] **Cấu trúc repo**: `web/` (Next.js), `api/` (FastAPI), `ingest/`, `eval/`, `docs/`.
- [ ] **Git workflow**: nhánh `main` (ổn định), nhánh feature `feat/*`, `docs/*`; PR + review; conventional commits.
- [ ] **Coding standards**: Python (ruff/black, type hints), TS (eslint/prettier); module < 200 dòng.
- [ ] **Test**: pytest (API/guardrail/eval), vitest (FE); CI tối thiểu.
- [ ] **KB build**: lệnh ingest crawl + SOP → Qdrant.

## Env vars (dự kiến)
- `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`
- `EMBED_MODEL`, `QDRANT_URL`, `QDRANT_KEY`
- `CRAWL_SEED_URLS`, `GUARDRAIL_EMERGENCY_THRESHOLD`
- `ASR_*`, `TTS_*` (bonus)

### data-api (Spring Boot 8081) — chat BFF (ADR-008, implemented)
- `SERVER_PORT` (default `8081`)
- `CORS_ALLOWED_ORIGINS` (default `http://localhost:3000`)
- `CHATBOT_BASE_URL` (default `http://localhost:8000`) — target chatbot-service cho `POST /api/v1/chat` proxy.
- `hanoi-heart.chatbot.{connect-timeout-ms, read-timeout-ms}` trong `application.yml` (timeout RestClient).

### frontend (React 18 CRA 3000)
- `REACT_APP_API_BASE_URL` (default `http://localhost:8081`) — axios `baseURL` trỏ tới data-api.

## Liên quan
- [[07-api-design]] · [[09-deployment-guide]] · [[00-competition-rubric-and-principles]]
