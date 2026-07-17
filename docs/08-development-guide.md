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

## Liên quan
- [[07-api-design]] · [[09-deployment-guide]] · [[00-competition-rubric-and-principles]]
