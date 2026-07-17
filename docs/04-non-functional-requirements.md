# 04 — Non-Functional Requirements

> Performance, security, scalability, compliance, reliability. Đọc sau `00-*`, `03-functional`.
> Cập nhật: 2026-07-17 · Trạng thái: Draft v1.

---

## NFR-1 — Performance
| Metric | Mục tiêu (demo) | Mục tiêu (pilot) |
|---|---|---|
| Chat end-to-end (P50) | ≤ 3s | ≤ 2s |
| Chat end-to-end (P95) | ≤ 6s | ≤ 4s |
| Retrieve top-k | ≤ 300ms | ≤ 150ms |
| ASR (nếu có) | ≤ 2s / câu | ≤ 1s |
| Time-to-first-token | ≤ 1.5s | ≤ 0.8s |

- Embedding/retrieve chạy song song; rerank chỉ top-k nhỏ.

## NFR-2 — Security & Privacy (R5) — **rubric 05 critical**
- **Không thu PII** không cần thiết (CCCD, số HS, chẩn đoán). Không yêu cầu đăng nhập BN cho MVP.
- Mã hóa **in-transit** (HTTPS/TLS via Caddy) và **at-rest** (DB volume).
- Secrets qua env, không commit (`.env` đã gitignored).
- Session vô danh, **xoá được**, TTL ngắn (vd 24h).
- Prompt injection mitigations: input sanitize, system prompt cứng, output guardrail.
- Không gửi PII ra LLM bên thứ 3 (nếu on-prem path) → ghi rõ trong `09-deployment`.

## NFR-3 — Compliance (rubric 03, 05)
- **Nghị định 13/2023/NĐ-CP** (Bảo vệ dữ liệu cá nhân): consent/minimize, xử lý 목 đích rõ, quyền xoá.
- **Luật Khám bệnh, chữa bệnh** (2023, hiệu lực 2025-01-01): bảo mật thông tin y tế.
- **On-prem-ready**: kiến trúc container chạy được trên infra BV, không phụ thuộc cloud cứng.
- Ghi rõ DPIA rút gọn + data flow trong `09-deployment`.

## NFR-4 — Reliability & Availability
- Demo: uptime trong phiên demo; fallback: nếu LLM lỗi → trả fallback "tạm không trả lời được, vui lòng liên hệ tổng đài".
- Guardrail **không bao giờ fail-open** ở emergency: khi classifier lỗi → mặc định **coi trọng безопасности** (ưu tiên cảnh báo cấp cứu).
- Không crash trên input rác (UTF-8 tiếng Việt, teencode, emoji).

## NFR-5 — Scalability (pilot)
- stateless API backend → scale ngang.
- Vector DB Qdrant enough cho KB BV (ước 10^3–10^4 chunks).
- Target pilot: phục vụ song song hàng chục phiên (suffice cho CSKH web).

## NFR-6 — Maintainability & DX
- Repo công khai, README 1-lệnh `docker compose up`.
- Cấu trúc module tách biệt: `ingest/`, `retrieval/`, `guardrail/`, `api/`, `web/`.
- Env-driven config; không hardcode.
- Eval set version-controlled (golden Q&A) → regression grounding.

## NFR-7 — Internationalization & Accessibility
- Tiếng Việt là mặc định; UI label song ngữ VN/EN ở phần kỹ thuật (slide).
- WCAG cơ bản: contrast, label cho input, phím tab, ARIA cho chat.
- Responsive mobile-first (BN dùng điện thoại).

## NFR-8 — Observability
- Structured logging (session, intent, guardrail flags, latency).
- Metrics cơ bản: request count, P95, emergency-triggered count, refusal count.
- Đánh giá định kỳ bằng eval set (FR-10).

## NFR-9 — Constraints (48h & infra)
- VPS hiện có (chưa rõ GPU) → LLM cloud API cho demo; ASR/TTS bonus nếu đủ thời gian.
- Docker Compose đơn máy cho demo; roadmap K8s/HA ở pilot.
- Bandwidth/cost LLM: cache câu FAQ phổ biến để giảm call.

## Liên quan
- [[03-functional-requirements]] · [[09-deployment-guide]] · [[00-competition-rubric-and-principles]]
