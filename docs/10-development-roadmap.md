# 10 — Development Roadmap (living doc)

> **STUB — chưa có nội dung.** Sẽ điền timeline 48h + % tiến độ.
> Cập nhật: 2026-07-17 · Trạng thái: TODO.

## Khung cần điền
- [ ] **Phase 0 — Foundation (Giờ 0–2):** chốt API contract (`07`), setup repo/Docker scaffold, seed KB (SOP + site crawl), env.
- [ ] **Phase 1 — Core RAG (Giờ 2–20):** ingest + retrieve + grounded answer + citation; guardrail emergency + OOS.
- [ ] **Phase 2 — Web UI (song song):** chat UI, citation, suggested Q, redirect buttons, responsive.
- [ ] **Phase 3 — Integration & bonus (Giờ 20–36):** booking redirect, ASR/TTS nếu đủ thời gian, eval set, handoff.
- [ ] **Phase 4 — Hardening & demo (Giờ 36–48):** deploy VPS, quay video ≤5', slide, project description, PDF.

## Parallel streams (không phụ thuộc — sau khi contract chốt)
| Luồng | Sở hữu | Đầu ra |
|---|---|---|
| Web FE | 3 web | chat UI + integration |
| AI/Backend | 2 AI | RAG + guardrail + eval |
| Data/Content/Demo | 1 BA | KB content, golden Q&A, slide, kịch bản video |

## % Tiến độ
- [ ] Phase 0: 0% · [ ] Phase 1: 0% · [ ] Phase 2: 0% · [ ] Phase 3: 0% · [ ] Phase 4: 0%

## Liên quan
- [[01-project-overview]] · [[07-api-design]] · [[11-project-changelog]]
