# 03 — Functional Requirements

> **Mục đích:** feature breakdown + user story + MoSCoW + acceptance criteria (AC) + traceability.
> **Đọc sau:** `00-*`, `02-business-analysis`.
> Cập nhật: 2026-07-17 · Phiên bản: **v1.1** · Trạng thái: **Review** (owner: Lead+AI+FE — verify theo `00-team-working-guide` §7).

> **MoSCoW:** **M**=Must(48h) · **S**=Should · **C**=Could · **W**=Won't(48h).

---

## Danh mục FR
| FR | Tên | P | Owner | UC | Rubric |
|---|---|---|---|---|---|
| FR-1 | Hỏi đáp KB grounded | **M** | AI | UC-1,6 | 01,02,05 |
| FR-2 | Phát hiện & xử lý cấp cứu (kill switch) | **M** | AI | UC-4 | 05 |
| FR-3 | Out-of-scope & no-medical-advice gate | **M** | AI | UC-5 | 05 |
| FR-4 | Đặt khám redirect | **M** | FE | UC-3 | 01,03 |
| FR-5 | BHYT & giá theo KB | **M** | AI | UC-2 | 03,05 |
| FR-6 | Citation & trust UI | **M** | FE | UC-1 | 04,05 |
| FR-7 | Refusal khi thiếu thông tin | **M** | AI | UC-1 | 05 |
| FR-8 | Suggested questions & handoff | **S** | FE | UC-1 | 04 |
| FR-9 | ASR/TTS tiếng Việt (bonus) | **C** | FE+AI | UC-7 | 02,04 |
| FR-10 | Admin/eval (nội bộ) | **S** | AI | — | 01,02 |
| FR-11 | Session & privacy | **M** | AI+FE | — | 05 |

> **MoSCoW count:** 7 Must · 2 Should · 1 Could · (0 Won't). **Đường an toàn 48h = 7 Must + 1 Should (FR-8).**

---

## FR-1 — Hỏi đáp KB grounded (R1, R9) — **M** | 01,02,05
- **Story:** Là BN, tôi hỏi info BV và nhận câu trả lời **đúng + có nguồn**.
- **Flow:** query → intent=faq → retrieve KB → rerank → LLM grounded → answer + citations.
- **AC:**
  - [ ] Trả lời dựa trên chunk KB thật (rerank score ≥ ngưỡng); không đủ → kích FR-7.
  - [ ] Hiển thị ≥1 citation (tên trang / bước SOP / mã form).
  - [ ] Hỗ trợ multi-turn (≤5 lượt ngữ cảnh).
  - [ ] Coverage ≥ 7 nhóm chủ đề `00-hospital-domain-rules` §5.

## FR-2 — Phát hiện & xử lý cấp cứu (R2) — **M (kill switch)** | 05
- **Story:** Là BN có dấu hiệu nguy hiểm, tôi được **ngay lập tức** hướng dẫn cấp cứu, KHÔNG tư vấn.
- **Flow:** query → emergency classifier (rule + LLM) → nếu dương → ngắt luồng, cảnh báo nổi, nút 115 + khoa Cấp cứu BVT.
- **AC:**
  - [ ] **Recall 100%** trên emergency eval set.
  - [ ] KHÔNG trả về tư vấn/chẩn đoán/kê đơn.
  - [ ] Thông điệp theo `HD.25.01`: gọi 115 / đến khoa Cấp cứu BVT.
  - [ ] Priority cao nhất, ngắt QA thường; **fail-safe** (classifier lỗi → ưu tiên cảnh báo, không fail-open).

## FR-3 — Out-of-scope & no-medical-advice gate (R4, R7) — **M** | 05
- **AC:**
  - [ ] Phát hiện câu ngoài phạm vi / yêu cầu y lệnh cá nhân / giải thích KQ CLS.
  - [ ] Từ chối lịch sự + điều hướng (Bs / quầy / kênh phù hợp).

## FR-4 — Đặt khám redirect (R6) — **M** | 01,03
- **AC:**
  - [ ] Intent=booking → nút/redirect Website / Zalo Mini App / Tổng đài (chính thức).
  - [ ] (S) Có API mock → tra slot giả; roadmap thật ghi rõ (ôm ô 03).

## FR-5 — BHYT & giá theo KB (R3) — **M** | 03,05
- **AC:**
  - [ ] Trả lời general policy từ KB.
  - [ ] Không cam kết % chi trả cụ thể khi thiếu → điều hướng quầy kế toán.

## FR-6 — Citation & trust UI (R9) — **M** | 04,05
- **AC:**
  - [ ] Mỗi câu có badge nguồn; click → xem snippet KB gốc.
  - [ ] Confidence indicator (THẤP → khuyến nghị xác nhận kênh người).

## FR-7 — Refusal khi thiếu thông tin (R1) — **M** | 05
- **AC:**
  - [ ] Không có chunk đủ độ tin → "Tôi chưa có đủ thông tin chính thức…" + điều hướng kênh hỗ trợ.
  - [ ] KHÔNG bịa (no hallucination) — kiểm bằng eval.

## FR-8 — Suggested questions & handoff — **S** | 04
- **AC:** gợi ý câu hỏi tiếp theo; nút "nói với nhân viên" → hotline.

## FR-9 — ASR/TTS tiếng Việt (bonus) — **C** | 02,04
- **AC:** mic → PhoWhisper ASR → pipeline → TTS (Viettel/FPT); nút mic + playback.

## FR-10 — Admin/eval (nội bộ) — **S** | 01,02
- **AC:** endpoint/internal page chạy golden Q&A set → report accuracy/citation/emergency recall.

## FR-11 — Session & privacy (R5) — **M** | 05
- **AC:**
  - [ ] Session id ngẫu nhiên, **không yêu cầu PII**.
  - [ ] Nút xoá lịch sử; log ẩn danh; TTL ngắn (≤24h).

---

## Ma trận FR ↔ Rubric
| FR | 01 Tech | 02 AI Arch | 03 Pilot | 04 UX | 05 Safety | 06 Demo |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| FR-1 grounded QA | ✅ | ✅ | | | ✅ | ✅ |
| FR-2 emergency | | ✅ | | | ✅ | ✅ |
| FR-3 OOS gate | | ✅ | | | ✅ | |
| FR-4 booking | ✅ | | ✅ | ✅ | | ✅ |
| FR-5 BHYT/pricing | | | ✅ | | ✅ | ✅ |
| FR-6 citation UI | | | | ✅ | ✅ | ✅ |
| FR-7 refusal | | ✅ | | | ✅ | |
| FR-8 suggested/handoff | | | | ✅ | | ✅ |
| FR-9 ASR/TTS | | ✅ | | ✅ | | ✅ |
| FR-10 eval | ✅ | ✅ | | | ✅ | |
| FR-11 session/privacy | | | | | ✅ | |

## Liên quan
- [[02-business-analysis]] · [[04-non-functional-requirements]] · [[00-hospital-domain-rules]]
- Contract implement: [[07-api-design]]
