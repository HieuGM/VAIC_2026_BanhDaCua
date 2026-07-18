# 10 — Development Roadmap (living doc)

> **STUB — chưa có nội dung.** Sẽ điền timeline 48h + % tiến độ.
> Cập nhật: 2026-07-18 · Trạng thái: TODO.

## Khung cần điền
- [x] **Phase 0 — Foundation (Giờ 0–2):** chốt API contract (`07`), setup repo/Docker scaffold, seed KB (SOP + site crawl), env.
- [ ] **Phase 1 — Core RAG (Giờ 2–20):** ingest + retrieve + grounded answer + citation; guardrail emergency + OOS.
- [x] **Phase 2 — Web UI (2026-07-18, DONE):** chat BFF + FE wiring — merged `develop` (PR #5) + deployed LIVE. data-api chat BFF (`de120e2`) + React FE wiring (`f780d35`). E2E verify trên VPS `https://heca.tolalinhne.site`: chat RAG grounded. Chi tiết: `11` [Unreleased].
- [ ] **Phase 3 — Integration & bonus (Giờ 20–36):** booking redirect, ASR/TTS nếu đủ thời gian, eval set, handoff.
- [~] **Phase 4 — Hardening & demo:** deploy VPS **DONE** (LIVE `heca.tolalinhne.site`, 2026-07-18, Option B — xem `09` / `DEPLOY.md`). Còn: quay video ≤5', slide, project description, PDF.
- [~] **Phase 5 — CI/CD (2026-07-18, PR #7 chờ merge):** GitHub Actions build off-VPS + GHCR + auto-deploy VPS (push:`develop`→live). CPU-torch fix + gate, path filter, ensure-public, health check. Xem `DEPLOY.md` §11, `11` [Unreleased].

## Parallel streams (không phụ thuộc — sau khi contract chốt)
| Luồng | Sở hữu | Đầu ra |
|---|---|---|
| Web FE | 3 web | chat UI + integration |
| AI/Backend | 2 AI | RAG + guardrail + eval |
| Data/Content/Demo | 1 BA | KB content, golden Q&A, slide, kịch bản video |

## % Tiến độ
- [x] Phase 0: 100% · [ ] Phase 1: 0% (AI team) · [x] Phase 2: 100% (merged + deployed LIVE) · [ ] Phase 3: 0% · [~] Phase 4: deploy DONE, còn video/slide/desc · [~] Phase 5: CI/CD PR #7 chờ merge (GHCR + GitHub Actions auto-deploy)

## Liên quan
- [[01-project-overview]] · [[07-api-design]] · [[11-project-changelog]]
