# 09 — Deployment Guide

> **STUB — chưa có nội dung.**
> Cập nhật: 2026-07-17 · Trạng thái: TODO.

## Khung cần điền
- [ ] **Docker Compose**: services (web, api, qdrant, caddy) + volumes + networks. 1 lệnh `docker compose up -d`.
- [ ] **VPS deploy**: SSH, clone, env, compose, Caddy auto-TLS, domain → public URL.
- [ ] **CI/CD (GitHub Actions)**: lint+test on PR; build image; deploy on push `main`/tag.
- [ ] **Env management**: dev/staging/prod; secrets qua GitHub Secrets + `.env`.
- [ ] **On-prem pilot path**: cùng image chạy infra BV; LLM on-prem (Qwen2.5/Vistral); không data egress.
- [ ] **DPIA rút gọn + data flow** (rubric 03/05): thu/minimize/retention/xoá.

## Mục tiêu
- Demo: public URL chạy Docker trên VPS hiện có.
- Pilot: container portable sang infra BV, privacy-compliant.

## Liên quan
- [[04-non-functional-requirements]] · [[05-system-architecture]] · [[10-development-roadmap]]
