# 04 — Non-Functional Requirements

> **Mục đích:** performance, security/privacy, compliance, reliability, scalability, DX + cách verify.
> **Đọc sau:** `00-*`, `03-functional-requirements`.
> Cập nhật: 2026-07-17 · Phiên bản: **v1.1** · Trạng thái: **Review** (owner: Lead+DevOps — verify theo `00-team-working-guide` §7).

---

## Danh mục NFR
| NFR | Nhóm | P | Rubric | Verify |
|---|---|---|---|---|
| NFR-1 | Performance | **M** | 01 | eval latency P50/P95 |
| NFR-2 | Security & Privacy | **M** | 05 | review PII flow + mã hóa |
| NFR-3 | Compliance | **M** | 03,05 | checklist NĐ13/Luật KBChB |
| NFR-4 | Reliability (fail-safe) | **M** | 05 | test LLM-fail + emergency-fail |
| NFR-5 | Scalability (pilot) | S | 03 | load test session song song |
| NFR-6 | Maintainability & DX | **M** | 01 | `docker compose up` 1 lệnh |
| NFR-7 | i18n & Accessibility | **M** | 04 | a11y audit (Radix/ARIA) |
| NFR-8 | Observability | S | 01,05 | log/metric dashboard |
| NFR-9 | Constraints (48h/infra) | **M** | 03 | VPS spec check |

---

## NFR-1 — Performance
| Metric | Mục tiêu demo | Mục tiêu pilot | Verify |
|---|---|---|---|
| Chat end-to-end (P50) | ≤ 3s | ≤ 2s | eval set + APM |
| Chat end-to-end (P95) | ≤ 6s | ≤ 4s | eval set + APM |
| Retrieve top-k | ≤ 300ms | ≤ 150ms | benchmark Qdrant |
| ASR (nếu có) | ≤ 2s/câu | ≤ 1s | đo end-to-end voice |
| Time-to-first-token | ≤ 1.5s | ≤ 0.8s | SSE timestamp |

- Embedding/retrieve song song; rerank chỉ top-k nhỏ (≤20).

## NFR-2 — Security & Privacy (R5) — **ô 05 critical**
- **Không thu PII** không cần thiết (CCCD, số HS, chẩn đoán). Không yêu cầu đăng nhập BN cho MVP.
- Mã hóa **in-transit** (HTTPS/TLS qua Caddy) + **at-rest** (DB volume).
- Secrets qua env, không commit (`.env` đã gitignored).
- Session vô danh, **xoá được**, TTL ngắn (≤24h).
- Prompt injection mitigations: input sanitize, system prompt cứng, output guardrail.
- LLM on-prem path → **không egress PII** ra bên thứ 3 (ghi rõ `09-deployment`).
- **Verify:** rà data-flow diagram (PII không rò rỉ); mã hóa bật mặc định.

## NFR-3 — Compliance (ô 03, 05)
- **Nghị định 13/2023/NĐ-CP** (Bảo vệ dữ liệu cá nhân): consent/minimize, mục đích xử lý rõ, quyền xoá.
- **Luật Khám bệnh, chữa bệnh 2023** (hiệu lực 2025-01-01): bảo mật thông tin y tế.
- **On-prem-ready**: container chạy được trên infra BV, không phụ thuộc cloud cứng.
- DPIA rút gọn + data-flow trong `09-deployment`.
- **Verify:** checklist điều khoản + citation đúng số điều luật (verify ở `brainstorming` §5).

## NFR-4 — Reliability (fail-safe, KHÔNG fail-open)
- Demo: uptime trong phiên; LLM lỗi → fallback "tạm không trả lời được, vui lòng liên hệ tổng đài".
- **Guardrail emergency không bao giờ fail-open:** classifier lỗi → **mặc định ưu tiên cảnh báo cấp cứu**.
- Không crash trên input rác (UTF-8 tiếng Việt, teencode, emoji, ký tự dài).
- **Verify:** test cố ý — tắt LLM, feed emergency query → vẫn cảnh báo.

## NFR-5 — Scalability (pilot)
- Stateless API backend → scale ngang.
- Qdrant đủ cho KB BV (ước 10³–10⁴ chunks).
- Pilot: phục vụ song song hàng chục phiên.
- **Verify:** load test (vd locust/k6) ≥ 20 phiên đồng thời.

## NFR-6 — Maintainability & DX
- Repo công khai, README 1-lệnh `docker compose up`.
- Module tách: `ingest/`, `retrieval/`, `guardrail/`, `api/`, `web/`.
- Env-driven config; không hardcode.
- Eval set version-controlled (golden Q&A) → regression grounding.

## NFR-7 — Internationalization & Accessibility
- Tiếng Việt mặc định; label kỹ thuật song ngữ VN/EN (slide).
- WCAG cơ bản: contrast, label input, phím tab, ARIA cho chat (shadcn/Radix).
- Responsive mobile-first (BN dùng điện thoại).
- **Verify:** Lighthouse a11y ≥ 90; test keyboard-only navigation.

## NFR-8 — Observability
- Structured logging (session, intent, guardrail flags, latency).
- Metrics: request count, P95, emergency-triggered count, refusal count.
- Đánh giá định kỳ bằng eval set (FR-10).

## NFR-9 — Constraints (48h & infra)
- VPS hiện có (chưa rõ GPU) → LLM cloud API cho demo; ASR/TTS bonus.
- Docker Compose đơn máy cho demo; roadmap K8s/HA ở pilot.
- Bandwidth/cost LLM: cache câu FAQ phổ biến để giảm call.

## Liên quan
- [[03-functional-requirements]] · [[09-deployment-guide]] · [[00-competition-rubric-and-principles]]
- Privacy/data-flow: [[09-deployment-guide]]
