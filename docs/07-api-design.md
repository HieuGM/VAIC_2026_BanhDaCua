# 07 — API Design (CONTRACT)

> **CONTRACT — chốt TRONG GIỜ ĐẦU** để 3 luồng song song không chặn nhau.
> 2 service: **FastAPI** (AI, `/api/v1`) + **Spring Boot** (data, `/data/v1`).
> Cập nhật: 2026-07-18 · Phiên bản: **v1.1** · Trạng thái: **Contract draft** (review AI+FE+data).

> **Nguyên tắc:** REST + JSON · error `{ "error": { "code", "message" } }` · **no auth** (đề tài scope; data-api internal, network = boundary) · Caddy route `/api/*`→FastAPI, `/data/*`→Spring Boot.

> ⚠️ **Thực tế (2026-07-18 + Recommendation A / ADR-008):** FE = React 18 + CRA (port 3000), **KHÔNG có Next.js Route Handler BFF**. FE gọi **`data-api` (8081) trực tiếp** cho cả data lookup và chat (`POST /data/v1/chat`). data-api đóng vai trò **chat BFF + persistence** rồi proxy sang chatbot-service `/api/v1/chat`. CORS cho `localhost:3000` ở Spring Boot 8081. Chatbot FastAPI hiện **không CORS middleware** (chỉ nhận call từ data-api, không từ browser).

---

## A. FastAPI — AI Gateway (`/api/v1`) — sở hữu AI team

> ⚠️ **Trạng thái thực tế (2026-07-18):** `POST /api/v1/chat` thực tế = **plain JSON, BLOCKING** (không SSE, không streaming, không token events). FE không gọi thẳng chatbot-service nữa — gọi qua data-api BFF (xem §B.5 / ADR-008). Phiên bản SSE + `token` event dưới đây là **đề xuất chưa hiện thực**, giữ roadmap.

### A.1 Chat (JSON blocking — thực tế)
- `POST /api/v1/chat` (port 8000, **không CORS middleware**)
  - **Request** (camelCase; alias snake_case accepted):
    ```json
    {
      "sessionId": "string (opaque, hiện không dùng do memory stub)",
      "text": "string",
      "lang": "vi",
      "userId": "string?",
      "userRole": "ANONYMOUS|USER|DOCTOR|ADMIN",
      "allowedPatientIds": ["string"],
      "context": {}
    }
    ```
  - **Response** (JSON, blocking):
    ```json
    {
      "answer": "string",
      "citations": [{ "source": "...", "url": "...", "snippet": "..." }],
      "confidence": 0.0,
      "guardrailFlags": ["emergency|out_of_scope|low_confidence|none"],
      "intent": "faq|booking|bhyt|pricing|emergency|out_of_scope",
      "route": "string",
      "redirection": { "channelType": "...", "url": "..." },
      "needsHandoff": false,
      "metadata": {}
    }
    ```
  - **Lưu ý:** `memory/session_memory.py` là STUB no-op → KHÔNG persist; `session_id` không có ý nghĩa nghiệp vụ cho đến khi data-api BFF chịu trách nhiệm persistence (ADR-008).

### A.1b Chat (SSE) — **đề xuất CHƯA hiện thực** (roadmap)
- `POST /api/v1/chat` (SSE) — req `{ sessionId, text, lang?:"vi" }`; events `token`{delta}, `final`{answer, citations[], confidence, guardrailFlags, intent, redirection?}. Đánh dấu **proposed**; không triển khai 48h (YAGNI).

### A.2 Citation / Session / Voice — **chưa implement** (roadmap)
- `GET /api/v1/citations/{chunkId}` → `{ source, sourceType, title, snippet, url, formCode? }`
- `POST /api/v1/session` → `{ sessionId }` · `DELETE /api/v1/session/{sessionId}` (R5) — hiện session_id opaque, không tạo session backend
- `POST /api/v1/asr` (multipart audio) → `{ text }` · `POST /api/v1/tts` { text } → audio (bonus)

### A.3 Eval (internal)
- `POST /api/v1/_eval/run` → `{ accuracy, citationRate, emergencyRecall }`

> **Lưu ý routing (2026-07-18 + ADR-008):** FE **không** gọi thẳng FastAPI cho chat/session nữa. Chat → `data-api POST /data/v1/chat` (BFF persist + proxy). Data lookup thuần → Spring Boot trực tiếp. Voice/ASR/TTS (nếu wire) có thể vẫn qua FastAPI khi đã implement.

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

> All `GET` list endpoints: pagination `?page&size`, filter, `Accept-Language` header (R10). Admin CRUD (POST/PUT/DELETE) — nội bộ, MVP skip (seed qua Flyway).

### B.5 Chat BFF + Persistence — **Recommendation A / ADR-008** (sở hữu data dev)

> FE gọi 3 endpoint này để chat + load lịch sử. data-api persist vào schema `hospital` (`chat_sessions`/`chat_messages`, Flyway) rồi proxy JSON đến chatbot-service `/api/v1/chat`. No streaming (YAGNI). No auth.

- **`POST /data/v1/chat`** — gửi tin nhắn, nhận answer + citations
  - Request:
    ```json
    { "sessionId": "string?", "text": "string", "lang": "vi?" }
    ```
    `sessionId` null/empty → data-api tạo session mới.
  - Response:
    ```json
    {
      "sessionId": "string",
      "answer": "string",
      "citations": [{ "source": "...", "url": "...", "snippet": "..." }],
      "confidence": 0.0,
      "intent": "string",
      "guardrailFlags": ["..."],
      "redirection": { "channelType": "...", "url": "..." },
      "needsHandoff": false,
      "metadata": {}
    }
    ```
  - Side-effects: data-api persist user message → gọi chatbot `/api/v1/chat` → persist assistant reply + citations. JSON blocking.

- **`GET /data/v1/chat/sessions`** — list session của user/anon token
  - Query: `?page&size` (PageResponse `{total,page,size,totalPages,items[]}`), filter `?lang`, `?anonToken`.
  - items: `[{ id, createdAt, updatedAt, lang, anonToken?, messageCount, lastSnippet }]`

- **`GET /data/v1/chat/sessions/{sessionId}/messages`** — history 1 session
  - Response: `PageResponse<{ id, role:"user|assistant|system", content, citations[], intent, route, guardrailFlags[], createdAt }>`

> **CORS:** Spring Boot ở 8081 cho phép `localhost:3000` (dev). Prod qua Caddy cùng domain → không CORS.

---

## C. Cần chốt thêm
- [ ] Exact JSON schema `final` event (Zod shared FE↔FastAPI).
- [ ] `confidence` 0–1 + ngưỡng `low_confidence` (vd <0.4).
- [ ] Mã `intent` chuẩn (enum chốt).
- [ ] Rate limit + CORS (FE domain).
- [ ] Seed loader profile (`SPRING_PROFILES=seed`).

## D. Ví dụ integration

> ⚠️ **Cập nhật (2026-07-18):** FE thực tế = React 18 + CRA (port 3000), gọi data-api trực tiếp ở 8081. **KHÔNG có Next.js BFF proxy**. FE gọi chat qua `POST /data/v1/chat` (data-api BFF), không gọi thẳng FastAPI.

- **FE tra lịch BS:** `GET /data/v1/doctors/{id}/schedules` → render.
- **FE chat:** `POST /data/v1/chat` (JSON, data-api BFF) → data-api persist + proxy `POST /api/v1/chat` (JSON, chatbot-service) → grounded answer + citations.
- **FE load history:** `GET /data/v1/chat/sessions` + `GET /data/v1/chat/sessions/{id}/messages`.
- **Booking:** FE `GET /data/v1/channels` → nút redirect (R6).

## Liên quan
- [[03-functional-requirements]] · [[05-system-architecture]] · [[06-database-design]] · [[08-development-guide]]
