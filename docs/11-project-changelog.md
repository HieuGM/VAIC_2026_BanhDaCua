# 11 — Project Changelog

> Lịch sử version dự án. Format: [Keep a Changelog] + SemVer.
> Cập nhật: 2026-07-17 · Trạng thái: Living doc.

## [Unreleased]
### Added
- Bộ tài liệu nền tảng (`docs/`): `00` rubric + domain rules, `01` overview, `02` business analysis, `03` FR, `04` NFR.
- Stub `05`–`11` (architecture, DB, API contract v0, dev guide, deploy, roadmap, changelog).
- `.gitignore` (loại trừ toolkit & artifact).
- Nhánh `docs` khởi tạo.
- **Data backend (Spring Boot 3.4.1 + Java 21)**: 8 REST controller `/data/v1/*` (hospital-info, departments, doctors + schedules, services + prices, bhyt-policies, procedures, channels, appointment-slots mock) — Flyway `V1`–`V9`, schema `hospital`, PG16.
- **Seed (verified, R1 medical safety)**: 3008 services, 4783 prices (701 BHYT + 4082 no_bhyt `NQ45/2024`), 11 procedures (QT.25.01 per `Quytrinh.md` §V — 11 responsibility rows), doctors/schedules/departments/BHYT/channels; nguồn `benhvientimhanoi.vn` + `NQ45/2024` + `TT22/2023`.
- **Crawl** 5 gap endpoints từ `benhvientimhanoi.vn` → `data/seed/crawled/*.json` (mỗi record có `sourceUrl` + `confidence`).
- Nhánh `feat/data-api` → merge `develop` (FF @`818f2ec`, gitflow; `main` release sau).

### Fixed
- `docs/01` + `docs/06`: tiền tố data service `/api/v1/*` → `/data/v1/*` cho khớp contract `07-api-design` (2-service split: `/api/v1`=FastAPI AI, `/data/v1`=Spring Boot data).

### Changed
- Working reports (`data-api-build-report`, crawler) dời `plans/reports/` (repo) → Claudekit toolkit (gitignored, local-only).

## [0.0.0] — 2026-07-17
- Khởi tạo repo, tiếp nhận đề bài VAIC 2026 (Hanoi Heart Hospital), nguồn `docs/refer/`.
