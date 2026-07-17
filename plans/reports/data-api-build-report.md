# Data-API Build Report

**Branch:** `feat/data-api` (off `docs`)
**Module:** `data-api/` at repo root
**Stack:** Java 21 + Spring Boot 3.4.1 + Spring Data JPA + Flyway + PostgreSQL 16
**Status:** ✅ All 9 migrations apply cleanly against Postgres 16; `mvn compile` + `test-compile` green.

## File tree (data-api only)

```
data-api/
├── pom.xml                                  # Spring Boot 3.4.1, Java 21, Lombok, Flyway, PG, validation, web
├── Dockerfile                               # maven:3.9-eclipse-temurin-21 build → eclipse-temurin:21-jre-jammy runtime
├── .env.example                             # DB_HOST/DB_PORT/DB/DB_USER/DB_PASS/SERVER_PORT/CORS/DATA_API_KEY
├── README.md                                # Quick start, endpoints, env table
├── scripts/
│   ├── parse-schedule.py                    # raw schedule → V4
│   ├── parse-services.py                    # banggiaBHYT.txt + GiaDVBV → V5
│   ├── parse-procedures.py                  # QT.25.01 SOP → V8
│   └── seed-crawled.py                      # crawled JSON → V2, V3, V6, V7
└── src/main/
    ├── java/com/hanoiheart/dataapi/
    │   ├── DataApiApplication.java
    │   ├── config/{ApiKeyFilter,CorsConfig}.java
    │   ├── controller/{AppointmentSlot,BhytPolicy,Department,Doctor,GlobalExceptionHandler,HospitalInfo,HospitalService,Procedure,SupportChannel}Controller.java
    │   ├── dto/*.java                       # 11 records + PageResponse
    │   ├── entity/*.java                    # 11 entities + BaseEntity
    │   ├── repository/*.java                # 11 Spring Data JPA interfaces
    │   └── service/*.java                   # 8 services
    └── resources/
        ├── application.yml                  # env-driven datasource, CORS, optional X-API-Key
        └── db/migration/
            ├── V1__init_hospital.sql        # schema + indexes + UNIQUE(code) on services
            ├── V2__seed_departments.sql     # 36 depts (crawled)
            ├── V3__seed_doctors.sql         # 69 doctors (65 crawled + 4 schedule-only)
            ├── V4__seed_doctor_schedules.sql# 561 deduped schedule rows
            ├── V5__seed_services_and_prices.sql # 582 services + 705 prices
            ├── V6__seed_bhyt_policies.sql   # 7 BHYT policy records
            ├── V7__seed_support_channels.sql# 12 channels (incl. Zalo Mini App)
            ├── V8__seed_procedures.sql      # QT.25.01 (12 steps)
            └── V9__seed_hospital_info.sql   # hospital_info + priority_groups + mock slots
```

Root additions:
- `docker-compose.yml` — `postgres:16-alpine` (with healthcheck) + `data-api` service.

## Tables seeded (verified against live PG 16)

| Table | Rows | Source |
|---|---:|---|
| hospital_info | 1 | groundtruth + working-hours.md |
| departments | 36 | crawled/departments.json |
| doctors | 69 | crawled/doctors.json (65) + schedule-only (4) |
| doctor_schedules | 561 | parsed from raw Lich_kham_benh |
| services | 582 | parsed from banggiaBHYT.txt |
| service_prices | 705 | BHYT ceiling (701) + no_bhyt subset (4) |
| bhyt_policies | 7 | crawled/bhyt-policies.json |
| support_channels | 12 | crawled/channels.json (incl. Zalo Mini App CS1) |
| procedures | 12 | curated from raw QUY_TRINH QT.25.01 |
| priority_groups | 1 | anchor (QĐ154 roster not yet published) |
| appointment_slots | 179 | mock (derived from doctor_schedules, week of 2026-07-20) |

## REST endpoints (per docs/07 §B)

| Method | Path | Notes |
|---|---|---|
| GET | `/data/v1/hospital-info` | Single master row |
| GET | `/data/v1/departments?active=&page=&size=` | Paginated |
| GET | `/data/v1/doctors?department={id}&page=&size=` | Paginated; filter by dept |
| GET | `/data/v1/doctors/{id}` | |
| GET | `/data/v1/doctors/{id}/schedules?from=&to=` | ISO date filter |
| GET | `/data/v1/services?category=&department=&page=&size=` | category: consultation/lab/procedure/mri/ct/intervention |
| GET | `/data/v1/services/{id}/prices` | audience: BHYT/no_bhyt |
| GET | `/data/v1/bhyt-policies?category=` | category: general/cardiac/cross_ref/copay |
| GET | `/data/v1/procedures?code=QT.25.01` | |
| GET | `/data/v1/channels` | All active support channels |
| GET | `/data/v1/appointment-slots?doctor=&date=` | Mock |

CORS allows `http://localhost:3000` by default (configurable via `CORS_ALLOWED_ORIGINS`).
Demo `X-API-Key` filter — disabled when `DATA_API_KEY` is empty.

## How to run

### Docker compose (preferred)
```bash
docker compose up --build postgres data-api
# API at http://localhost:8081/data/v1/hospital-info
```

### Maven local
```bash
cp data-api/.env.example data-api/.env
docker compose up -d postgres
cd data-api && mvn spring-boot:run
```

## Env vars

| Var | Default | Description |
|---|---|---|
| `DB_HOST` | localhost | Postgres host |
| `DB_PORT` | 5432 | Postgres port |
| `DB` | hanoi_heart | Database name |
| `DB_USER` | hanoiheart | DB user |
| `DB_PASS` | hanoiheart | DB password |
| `SERVER_PORT` | 8081 | HTTP port |
| `CORS_ALLOWED_ORIGINS` | http://localhost:3000 | Comma-separated FE origins |
| `DATA_API_KEY` | (empty) | If set, requires `X-API-Key` header on `/data/**` |

## Data gaps / R1 anti-hallucination notes

- **Doctor bio / avatar** — null for all. Crawled source has no bio text or avatar URLs (R1).
- **QĐ154 priority-group roster** — only anchor row seeded; structured list not publicly published.
- **BHYT copay %** — no numeric percentage published; only procedural summary (TT22/2023, TT13/2020 verbatim).
- **Hospital grade** — null; not on public site.
- **`no_bhyt` service prices** — full price table (`GiaDVBV_tim_HN.txt`, 24K lines) is page-scrambled PDF text without stable codes; only 4 high-signal rows (Khám bệnh, ngày giường types) extracted. Recommend obtaining the original PDF for complete seeding.
- **Source typo** — `16.31` end-time in raw schedule line 738 (faithful, annotated in V4).
- **Schedule-only doctors (4)** — `Lê Thanh Nam`, `Phan Thành Nam` (CS2 TN mức 3 substitutes across weeks) + 2 others parsed from schedule but absent from crawled roster; flagged `source=schedule-derived` in V3.

## Unresolved questions

1. **KHTN_CS2 mapping** — `Khu Khám bệnh Tự nguyện CS2` (5 rooms 306-311) currently FKs to umbrella `kham-benh-tu-nguyen`. Should it instead map to `phong-kham-da-khoa-cs2`? They are technically distinct in source layout.
2. **QT.25.01 step count** — docs/06 §3.3 says "11 bước" but source lists 12 numbered steps (step 12 is "lĩnh thuốc / kết thúc"). Seeded all 12. Confirm desired canonical count.
3. **Doctor→department FK for "Ban Giám đốc / Multi-dept" doctors** — current heuristic picks the LAST segment after `/` in crawled `department` field. Doctors spanning multiple departments (e.g., Vũ Quỳnh Nga = Ban Giám đốc + Khoa TN1) are assigned to the clinical unit only. Acceptable for `/doctors?department=` filtering?
4. **V5 service_prices dedup** — banggiaBHYT repeats codes for variants (e.g., `22.0275.1327` for auto vs semi-auto analyzer). Each gets its own price row. Confirm this is desired vs. merging.
5. **No-bhyt price table** — 24K-line `GiaDVBV_tim_HN.txt` is page-scrambled; only 4 rows seeded. Should I attempt full parse (best-effort) or wait for cleaner source?

## Coordinator review history
- ✅ All 8 prior flags addressed (garbage rows, undercount, "(Chiều nghỉ)" split, degree regex, room sub-letter P405.A, dup schedules, annotation slugs, source typo).
- ✅ Reconciled against crawled ground-truth JSON (`doctors.json` 68, `departments.json` 36, `bhyt-policies.json` 7, `channels.json` 12 with Zalo).
