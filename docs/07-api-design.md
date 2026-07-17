# 07 — API Design (CONTRACT)

> **CONTRACT — chốt TRONG GIỜ ĐẦU** để 3 luồng song song không chặn nhau.
> 2 service: **FastAPI** (AI, `/api/v1`) + **Spring Boot** (data, `/data/v1`).
> Cập nhật: 2026-07-17 · Phiên bản: **v1.0** · Trạng thái: **Contract draft** (review AI+FE+data).

> **Nguyên tắc:** REST + JSON · error `{ "error": { "code", "message" } }` · demo auth `X-API-Key` (pilot: BV SSO) · Caddy route `/api/*`→FastAPI, `/data/*`→Spring Boot.

---

## A. FastAPI — AI Gateway (`/api/v1`) — sở hữu AI team, FE-facing

### A.1 Chat (SSE)
- `POST /api/v1/chat`
  - req: `{ sessionId, text, lang?:"vi" }`
  - SSE events:
    - `token` { delta } — stream answer
    - `final` { answer, citations[], confidence, guardrailFlags, intent, redirection? }
  - **guardrailFlags**: `emergency | out_of_scope | low_confidence | none`
  - **intent**: `faq | booking | bhyt | pricing | emergency | out_of_scope`

### A.2 Citation / Session / Voice
- `GET /api/v1/citations/{chunkId}` → `{ source, sourceType, title, snippet, url, formCode? }`
- `POST /api/v1/session` → `{ sessionId }` · `DELETE /api/v1/session/{sessionId}` (R5)
- `POST /api/v1/asr` (multipart audio) → `{ text }` · `POST /api/v1/tts` { text } → audio (bonus)

### A.3 Eval (internal)
- `POST /api/v1/_eval/run` → `{ accuracy, citationRate, emergencyRecall }`

> FE gọi FastAPI cho **chat + session + voice**. Data lookup thuần → Spring Boot (B).

---

## B. Spring Boot — Data Service (`/data/v1`) — sở hữu data dev

> Nguồn dữ liệu cấu trúc chính thức. FastAPI gọi qua adapter (swappable HIS). FE gọi trực tiếp để render UI.

### B.1 Master data
- `GET /data/v1/hospital-info` → `{ name, address[], hotline, workingHours, grade }`
- `GET /data/v1/departments?active=true` → `[{ id, code, name, floor, workingHours, phone }]`
- `GET /data/v1/doctors?department={id}` → `[{ id, code, fullName, degree, title, departmentId, bio, avatarUrl }]`
- `GET /data/v1/doctors/{id}/schedules?from&to` → `[{ dayOfWeek, startTime, endTime, shift, room }]`

### B.2 Services & pricing (citatable exact)
- `GET /data/v1/services?category=&department=` → `[{ id, code, name, category, departmentId }]`
- `GET /data/v1/services/{id}/prices` → `[{ audience: "BHYT|no_bhyt|foreigner", priceVnd, effectiveDate, sourceUrl }]`
- `GET /data/v1/bhyt-policies?category=` → `[{ code, title, summary, detailsMd, sourceUrl }]`

### B.3 KB content (source-of-truth text → AI ingest)
- `GET /data/v1/kb/articles?sourceType=&category=` → `[{ id, sourceType, sourceUrl, title, bodyMd, tags[] }]`
- `GET /data/v1/faqs?category=&golden=true` → `[{ id, question, answerMd, sourceUrl, isGolden }]`
- `GET /data/v1/procedures?code=QT.25.01` → `[{ stepNo, title, description, responsibleRole, relatedForm }]`
- `GET /data/v1/emergency-protocols` → `[{ code:"HD.25.01", triggerKeywords[], instructionMd, redirectChannelId }]`

### B.4 Channels & booking (mock)
- `GET /data/v1/channels` → `[{ channelType, label, url, phone }]`
- `GET /data/v1/appointment-slots?doctor&date` → `[{ start, end, capacity, booked, available }]` *(mock — prod = HIS)*

> All `GET` list endpoints: pagination `?page&size`, filter, `Accept-Language` header (R10). Admin CRUD (POST/PUT/DELETE) — nội bộ, guard `X-API-Key`, MVP có thể skip (seed qua Flyway).

---

## C. Cần chốt thêm
- [ ] Exact JSON schema `final` event (Zod shared FE↔FastAPI).
- [ ] `confidence` 0–1 + ngưỡng `low_confidence` (vd <0.4).
- [ ] Mã `intent` chuẩn (enum chốt).
- [ ] Rate limit + CORS (FE domain).
- [ ] Seed loader profile (`SPRING_PROFILES=seed`).

## D. Ví dụ integration
- **FE tra lịch BS:** `GET /data/v1/doctors/{id}/schedules` → render.
- **FE chat:** `POST /api/v1/chat` (SSE) → FastAPI retrieve Qdrant + (cần data) gọi `GET /data/v1/*` qua adapter → grounded answer.
- **Booking:** FE `GET /data/v1/channels` → nút redirect (R6).

## Liên quan
- [[03-functional-requirements]] · [[05-system-architecture]] · [[06-database-design]] · [[08-development-guide]]
