# 07 — API Design (CONTRACT)

> **v0 DRAFT — chốt contract TRONG GIỜ ĐẦU** để 3 luồng (FE/AI/BA) song song không chặn nhau.
> Cập nhật: 2026-07-17 · Trạng thái: Contract draft (cần review chốt).

## Nguyên tắc
- REST + JSON; base path `/api/v1`.
- Streaming SSE cho chat (token stream) — endpoint `/chat` dạng SSE.
- Error format thống nhất: `{ "error": { "code", "message" } }`.
- Auth demo: API key header (`X-API-Key`); pilot: OAuth/BV SSO.

## Endpoints (draft)

### Chat
- `POST /api/v1/chat` (SSE)
  - req: `{ sessionId, text, lang?:"vi" }`
  - events: `token` (stream), `final` { answer, citations[], confidence, guardrailFlags, intent, redirection? }
  - **guardrailFlags**: `emergency | out_of_scope | low_confidence | none`

### Citação
- `GET /api/v1/citations/{chunkId}` → `{ source, sourceType, title, snippet, url, formCode? }`

### Session
- `POST /api/v1/session` → `{ sessionId }`
- `DELETE /api/v1/session/{sessionId}` (R5 — xoá lịch sử)

### Voice (bonus)
- `POST /api/v1/asr` (multipart audio) → `{ text }`
- `POST /api/v1/tts` (req `{ text }`) → audio stream

### Booking redirect
- `GET /api/v1/channels` → danh sách kênh chính thức (web/zalo/hotline/emergency) + url
- (mock) `GET /api/v1/appointments/slots?doctor&date` → slot giả

### Admin/Eval (internal)
- `POST /api/v1/_eval/run` → chạy golden set → `{ accuracy, citationRate, emergencyRecall }`

## Cần chốt thêm
- [ ] Exact JSON schema cho `final` event.
- [ ] Quy ước `confidence` (0–1) + ngưỡng low_confidence.
- [ ] Mã `intent` chuẩn (faq/booking/bhyt/pricing/emergency/out_of_scope).
- [ ] Rate limit cơ bản.

## Liên quan
- [[03-functional-requirements]] · [[05-system-architecture]] · [[08-development-guide]]
