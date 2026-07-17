# Data-API Build Report (v2 — post corrections)

**Branch:** `feat/data-api` (off `docs`)
**Module:** `data-api/` at repo root
**Stack:** Java 21 + Spring Boot 3.4.1 + Spring Data JPA + Flyway + PostgreSQL 16
**Merge target:** HOLD — coordinator will create `develop` (off `docs`) and merge there. `main` comes later.
**Status:** ✅ All 9 migrations apply cleanly against PG16; `mvn compile` + `test-compile` green; spot-checks pass.

## v2 corrections applied

| Q | Action |
|---|---|
| Q2 procedures 12→11 | Merged step 9 (Hẹn tái khám) + step 10 (Thủ tục hành chính) — they share one responsibility row in canonical `docs/refer/Quytrinh.md` §V. Verified: `procedures=11` in PG. |
| Q5 no_bhyt prices 4→4082 | Rewrote `parse-services.py` to fully walk page-scrambled PDF text. Handles both formats: lone-STT-then-code (145 entries) and compact `<STT> <code> <name>` on one line (2798 entries). Synthesizes `NV-KB-*` / `NV-KSK-*` / `NV-GT-*` codes for section-1 entries without mã (Khám bệnh, ngày giường, khám sức khỏe, gây tê). Each row carries `[NQ45/2024; page N; confidence=high\|medium]` in `note` for traceability. |
| Q1, Q3, Q4 heuristics | Documented below (no change needed — accepted). |
| Merge gate | Holding; coordinator creates `develop` and merges. |

## File tree (data-api only)

```
data-api/
├── pom.xml                                  # Spring Boot 3.4.1, Java 21, Lombok, Flyway, PG, validation, web
├── Dockerfile                               # maven:3.9-eclipse-temurin-21 build → eclipse-temurin:21-jre-jammy runtime
├── .env.example
├── README.md
├── scripts/
│   ├── parse-schedule.py                    # raw schedule → V4
│   ├── parse-services.py                    # banggiaBHYT + GiaDVBV → V5 (full no_bhyt walk)
│   ├── parse-procedures.py                  # QT.25.01 SOP → V8 (11 steps)
│   └── seed-crawled.py                      # crawled JSON → V2, V3, V6, V7
└── src/main/
    ├── java/com/hanoiheart/dataapi/
    │   ├── DataApiApplication.java
    │   ├── config/{ApiKeyFilter,CorsConfig}.java
    │   ├── controller/*.java                # 9 controllers + GlobalExceptionHandler
    │   ├── dto/*.java                       # 11 records + PageResponse
    │   ├── entity/*.java                    # 11 entities + BaseEntity
    │   ├── repository/*.java                # 11 Spring Data JPA interfaces
    │   └── service/*.java                   # 8 services
    └── resources/
        ├── application.yml
        └── db/migration/
            ├── V1__init_hospital.sql        # schema + indexes + UNIQUE(code) on services + bhyt_policies table
            ├── V2__seed_departments.sql     # 36 depts (crawled)
            ├── V3__seed_doctors.sql         # 69 doctors (65 crawled + 4 schedule-only)
            ├── V4__seed_doctor_schedules.sql# 561 deduped schedule rows
            ├── V5__seed_services_and_prices.sql # 3008 services + 4783 prices (BHYT + no_bhyt)
            ├── V6__seed_bhyt_policies.sql   # 7 BHYT policy records
            ├── V7__seed_support_channels.sql# 12 channels (incl. Zalo Mini App)
            ├── V8__seed_procedures.sql      # QT.25.01 (11 steps)
            └── V9__seed_hospital_info.sql   # hospital_info + priority_groups + mock slots
```

Root addition: `docker-compose.yml` — `postgres:16-alpine` (healthcheck) + `data-api` service.

## Tables seeded (verified live against PG16)

| Table | Rows | Source |
|---|---:|---|
| hospital_info | 1 | groundtruth + working-hours.md |
| departments | 36 | crawled/departments.json |
| doctors | 69 | crawled/doctors.json (65) + schedule-only (4) |
| doctor_schedules | 561 | parsed from raw Lich_kham_benh |
| services | 3008 | banggiaBHYT (582) + GiaDVBV (2426 unique new) |
| service_prices | 4783 | BHYT ceiling (701) + no_bhyt NQ45/2024 (4082) |
| bhyt_policies | 7 | crawled/bhyt-policies.json |
| support_channels | 12 | crawled/channels.json (incl. Zalo Mini App CS1) |
| procedures | **11** | curated from raw QUY_TRINH QT.25.01 (was 12, corrected) |
| priority_groups | 1 | anchor (QĐ154 roster not yet published) |
| appointment_slots | 179 | mock (derived from doctor_schedules) |

### Service category breakdown

| Category | Count |
|---|---:|
| consultation | 15 (BHYT + NV-KB- synthetic codes for section 1) |
| lab | 672 |
| procedure | 1769 |
| ct | 304 |
| intervention | 170 |
| mri | 78 |

### Price audience breakdown

| Audience | Count | Law basis |
|---|---:|---|
| BHYT | 701 | TT22/2023/TT-BYT (+ TT13/2020 for some CLVT) |
| no_bhyt | 4082 | NQ45/2024/NQ-HĐND Hà Nội (per-row page+confidence annotated) |

### Spot-check sample (PG query)

```
   code    |     name      | audience | price_vnd | campus
-----------+---------------+----------+-----------+--------
 KB-0001   | Khám bệnh     | BHYT     |     42100 | (ceiling)
 NV-KB-0001| Giá Khám bệnh | no_bhyt  |     50600 | CS1
 NV-KB-0001| Giá Khám bệnh | no_bhyt  |     50600 | CS2
```

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

CORS allows `http://localhost:3000` by default. Demo `X-API-Key` filter — disabled when `DATA_API_KEY` empty.

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

## Documented heuristics (Q1/Q3/Q4 — accepted)

### Q1: KHTN_CS2 mapping
- **Decision:** `KHTN_CS2` (Khu Khám bệnh Tự nguyện CS2 — 5 rooms 306-311) → `kham-benh-tu-nguyen` (umbrella crawled dept covering both CS1 + CS2 TN).
- **Alternative considered:** `phong-kham-da-khoa-cs2` (closer geographically to CS2). Rejected because PKĐK is the multi-specialty clinic (RHM/TMH/MẮT/etc.) at section C, not the TN rooms.
- **Impact:** All schedule rows in CS2 Khu TN FK to one umbrella dept. Doctor→schedule queries by `department=kham-benh-tu-nguyen` will return CS2 TN doctors.

### Q3: Multi-department doctors
- **Heuristic:** Crawled `doctors.json` `department` field may be "Ban Giám đốc / Khoa Khám bệnh Tự nguyện 1". The parser picks the LAST segment after `/` (the clinical unit) and matches its normalized name against `departments.json` to resolve `department_id`.
- **Example:** "Vũ Quỳnh Nga" (Ban Giám đốc + Khoa TN1) → `department_id = (SELECT id FROM departments WHERE code='kham-benh-tu-nguyen-1')`.
- **Impact:** `/doctors?department={id}` returns doctors whose clinical work is in that department, regardless of administrative title.
- **Limitation:** Doctors with no extractable clinical department (e.g., pure admin) have `department_id=NULL`.

### Q4: BHYT variant codes
- **Behavior:** `banggiaBHYT.txt` repeats codes for variants (e.g., `22.0275.1327` appears for "Scangel/Gelcard trên máy tự động" AND "trên máy bán tự động"). Each variant becomes its own `service_prices` row with the variant note preserved.
- **Service dedup:** `services` table uses `code` as `UNIQUE` constraint; first variant wins the `name`. Subsequent variants appear only in `service_prices.note`.
- **Impact:** `GET /services/{id}/prices` may return 2-3 BHYT rows for the same code. Client must display variant notes.

## Data gaps / R1 anti-hallucination notes

- **Doctor bio / avatar** — null for all. Crawled source has no bio text or avatar URLs (R1).
- **QĐ154 priority-group roster** — only anchor row seeded; structured list not publicly published. Marked low-confidence in `bhyt-policies.json` ("bhyt-uu-tien").
- **BHYT copay %** — no numeric percentage published; only procedural summary (TT22/2023, TT13/2020 verbatim).
- **Hospital grade** — null; not on public site.
- **No_bhyt page-scramble residue:** Some entries in `GiaDVBV_tim_HN.txt` have STT split across page boundaries or name truncated; parser captures what it can. Each emitted row carries a `confidence=high|medium` flag in `note`. ~145 entries had lone-STT format (older pages), ~2798 used compact `<STT> <code> <name>` format (newer pages). 56 codes overlap with BHYT set; 2426 are new services.
- **Source typo preserved:** `16.31` end-time in raw schedule line 738 (Nội chung CXK CS2) — faithful to source, annotated in V4.
- **Schedule-only doctors (4)** — flagged `source=schedule-derived` in V3.

## Coordinator verify gate

Independent spot-checks the coordinator can run:

```sql
-- 1. Procedure count = 11
SELECT count(*) FROM hospital.procedures WHERE code='QT.25.01';
-- 2. No garbage doctors (no 'tc', 'tmch', 'khong-co-lich')
SELECT code, full_name FROM hospital.doctors WHERE code IN ('tc','tmch','khong-co-lich','hc','pk4');
-- 3. Khám bệnh price cross-check (BHYT 42.100 vs no_bhyt 50.600)
SELECT s.code, s.name, sp.audience, sp.price_vnd, sp.campus
FROM hospital.services s JOIN hospital.service_prices sp ON sp.service_id=s.id
WHERE s.name ILIKE '%khám bệnh%' LIMIT 10;
-- 4. Doctor schedule spot-check (Hoàng Văn Phòng 4 sáng)
SELECT d.full_name, ds.room, ds.shift, ds.start_time, ds.end_time, ds.effective_date
FROM hospital.doctor_schedules ds JOIN hospital.doctors d ON d.id=ds.doctor_id
WHERE d.full_name = 'Hoàng Văn' ORDER BY ds.effective_date LIMIT 5;
-- 5. Sample 2 prices vs raw (cross-check first 2 GiaDVBV entries)
SELECT s.code, s.name, sp.price_vnd, sp.audience, sp.campus, sp.note
FROM hospital.services s JOIN hospital.service_prices sp ON sp.service_id=s.id
WHERE s.code IN ('01.0303.0001','01.0021.0001') ORDER BY s.code, sp.audience, sp.campus;
```

All seeded records trace to either:
1. `data/seed/crawled/*.json` (crawled from `benhvientimhanoi.vn`, includes `sourceUrl`)
2. `data/raw/*.txt` (raw text, page+confidence annotated for no_bhyt prices)

## Unresolved questions (still open)

1. **Q1 KHTN_CS2:** keep umbrella mapping (`kham-benh-tu-nguyen`) or switch to `phong-kham-da-khoa-cs2`? Documented above.
2. **Q3 multi-dept:** heuristic picks clinical unit; acceptable for filtering? Documented above.
3. **Q4 BHYT variants:** keep as own rows (current) or collapse? Documented above.
4. **PDF source for cleaner no_bhyt:** current parse is best-effort against page-scrambled text. If original PDF `Tim Hà Nội.docx.pdf` (in `docs/refer/`) is parseable, could yield cleaner extraction. Defer unless required.
5. **Merge sequencing:** awaiting coordinator to create `develop` off `docs`, then merge `feat/data-api` PR.
