# 10 — Development Roadmap (living doc)

> **STUB — chưa có nội dung.** Sẽ điền timeline 48h + % tiến độ.
> Cập nhật: 2026-07-18 · Trạng thái: TODO.

## Khung cần điền
- [x] **Phase 0 — Foundation (Giờ 0–2):** chốt API contract (`07`), setup repo/Docker scaffold, seed KB (SOP + site crawl), env.
- [ ] **Phase 1 — Core RAG (Giờ 2–20):** ingest + retrieve + grounded answer + citation; guardrail emergency + OOS.
- [~] **Phase 2 — Web UI (song song) — chat BFF + FE wiring ĐÃ implement local (2026-07-18):** data-api chat BFF (commit `de120e2`) + React FE wiring (commit `f780d35`) trên nhánh `feat/data-api-chat-bff`. Unit/integration test data-api 11/11 pass. **Pending:** real-chatbot E2E (AI team chạy chatbot local — Python 3.14 + ML deps), browser E2E, merge `develop`. Chi tiết: `11` [Unreleased].
- [ ] **Phase 3 — Integration & bonus (Giờ 20–36):** booking redirect, ASR/TTS nếu đủ thời gian, eval set, handoff.
- [ ] **Phase 4 — Hardening & demo (Giờ 36–48):** deploy VPS, quay video ≤5', slide, project description, PDF.

## Parallel streams (không phụ thuộc — sau khi contract chốt)
| Luồng | Sở hữu | Đầu ra |
|---|---|---|
| Web FE | 3 web | chat UI + integration |
| AI/Backend | 2 AI | RAG + guardrail + eval |
| Data/Content/Demo | 1 BA | KB content, golden Q&A, slide, kịch bản video |

## % Tiến độ
- [x] Phase 0: 100% · [ ] Phase 1: 0% · [~] Phase 2: 60% (BFF+FE wiring done local, E2E+merge pending) · [ ] Phase 3: 0% · [ ] Phase 4: 0%

## Liên quan
- [[01-project-overview]] · [[07-api-design]] · [[11-project-changelog]]
