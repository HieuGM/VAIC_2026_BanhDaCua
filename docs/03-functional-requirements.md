# 03 — Functional Requirements

> Feature breakdown + user story + MoSCoW + acceptance criteria. Ánh xạ sang rubric.
> Đọc sau `00-*`, `02-business-analysis`. Cập nhật: 2026-07-17 · Trạng thái: Draft v1.

> **MoSCoW:** M = Must (48h) · S = Should · C = Could · W = Won't (48h).

---

## FR-1 — Hỏi đáp KB grounded (R1, R9) — **M** | rubric 01,02,05
- **Story:** Là BN, tôi hỏi info BV và nhận câu trả lời **đúng + có nguồn**.
- **Flow:** query → intent=faq → retrieve KB → rerank → LLM grounded → answer + citations.
- **AC:**
  - [ ] Trả lời dựa trên chunk KB thật (score ≥ ngưỡng); không → kích FR-7.
  - [ ] Hiển thị ≥1 citation (tên trang / bước SOP / mã form).
  - [ ] Hỗ trợ multi-turn (≤5 lượt ngữ cảnh).
  - [ ] Coverage ≥ nhóm chủ đề §5 `00-hospital-domain-rules`.

## FR-2 — Phát hiện & xử lý cấp cứu (R2) — **M (kill switch)** | rubric 05
- **Story:** Là BN có dấu hiệu nguy hiểm, tôi được **ngay lập tức** hướng dẫn cấp cứu, KHÔNG tư vấn.
- **Flow:** query → emergency classifier (rule + LLM) → nếu dương → ngắt luồng, cảnh báo nổi, nút 115 + khoa Cấp cứu.
- **AC:**
  - [ ] Recall 100% trên emergency eval set.
  - [ ] KHÔNG trả về tư vấn điều trị/chẩn đoán/kê đơn.
  - [ ] Thông điệp theo `HD.25.01`: gọi 115 / đến khoa Cấp cứu BVT.
  - [ ] Priority cao nhất, ngắt QA thường.

## FR-3 — Out-of-scope & no-medical-advice gate (R4, R7) — **M** | rubric 05
- **AC:**
  - [ ] Phát hiện câu ngoài phạm vi / yêu cầu y lệnh cá nhân / giải thích KQ CLS.
  - [ ] Từ chối lịch sự + điều hướng (Bs / quầy / kênh phù hợp).

## FR-4 — Đặt khám redirect (R6) — **M** | rubric 01,03
- **AC:**
  - [ ] Intent=booking → nút/redirect Website / Zalo Mini App / Tổng đài (chính thức).
  - [ ] (S) Nếu có API mock → tra slot giả; roadmap thật ghi rõ.

## FR-5 — BHYT & giá theo KB (R3) — **M** | rubric 05
- **AC:**
  - [ ] Trả lời general policy từ KB.
  - [ ] Không cam kết % chi trả cụ thể khi thiếu → điều hướng quầy kế toán.

## FR-6 — Citation & trust UI (R9) — **M** | rubric 04,05
- **AC:**
  - [ ] Mỗi câu có badge nguồn; click → xem snippet KB gốc.
  - [ ] Confidence indicator (cao/THẤP → khuyến nghị xác nhận kênh người).

## FR-7 — Refusal khi thiếu thông tin (R1) — **M** | rubric 05
- **AC:**
  - [ ] Không có chunk đủ độ tin → "Tôi chưa có đủ thông tin chính thức…" + điều hướng kênh hỗ trợ.
  - [ ] KHÔNG bịa (no hallucination) — kiểm bằng eval.

## FR-8 — Suggested questions & handoff — **S** | rubric 04
- **AC:** gợi ý câu hỏi tiếp; nút "nói với nhân viên" → hotline.

## FR-9 — ASR/TTS tiếng Việt (bonus) — **C** | rubric 02,04
- **AC:** mic → PhoWhisper ASR → pipeline → TTS (Viettel/FPT).

## FR-10 — Admin/eval ( nội bộ ) — **S** | rubric 01,02
- **AC:** endpoint/internal page chạy golden Q&A set → report accuracy/citation/emergency recall.

## FR-11 — Session & privacy (R5) — **M** | rubric 05
- **AC:** session id ngẫu nhiên, không yêu cầu PII, nút xoá lịch sử, log ẩn danh.

---

## Ma trận FR ↔ Rubric
| FR | 01 Tech | 02 AI Arch | 03 Pilot | 04 UX | 05 Safety |
|---|:-:|:-:|:-:|:-:|:-:|
| FR-1 grounded QA | ✅ | ✅ | | | ✅ |
| FR-2 emergency | | ✅ | | | ✅ |
| FR-3 OOS gate | | ✅ | | | ✅ |
| FR-4 booking | ✅ | | ✅ | ✅ | |
| FR-5 BHYT/pricing | | | ✅ | | ✅ |
| FR-6 citation UI | | | | ✅ | ✅ |
| FR-7 refusal | | ✅ | | | ✅ |
| FR-8 suggested/handoff | | | | ✅ | |
| FR-9 ASR/TTS | | ✅ | | ✅ | |
| FR-10 eval | ✅ | ✅ | | | ✅ |

## Liên quan
- [[02-business-analysis]] · [[04-non-functional-requirements]] · [[00-hospital-domain-rules]]
