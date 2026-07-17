# 02 — Business Analysis

> **Mục đích:** actor, use case, domain model, pain→value (input cho pitch ô 03 + UX ô 04).
> **Đọc sau:** `00-competition-rubric-and-principles`, `00-hospital-domain-rules`.
> Cập nhật: 2026-07-17 · Phiên bản: **v1.1** · Trạng thái: **Review** (owner: BA — verify theo `00-team-working-guide` §7).

---

## 1. Stakeholders
| Actor | Mục tiêu | Nỗi đau |
|---|---|---|
| **BN & người nhà** | Info nhanh, chính xác, 24/7; biết phải làm gì tiếp | Chờ tổng đài, info mâu thuẫn, không biết quy trình |
| **NV CSKH / tổng đài / reception** | Giảm câu lặp, tập sự cố phức tạp | Quá tải câu lặp, trả lời chậm |
| **Phòng IT BVT** | Triển khai an toàn trên infra BV, bảo mật | Yêu cầu on-prem-capable, tuân thủ NĐ13/Luật KBChB |
| **Ban lãnh đạo BVT** | Tăng trải nghiệm BN, giảm chi phí, image | ROI, pilot pathway |
| **Giám khảo VAIC** | Đánh giá engineering + AI + pilot + safety | Rubric 6 ô |

## 2. Use Cases (UC) — kèm priority & effort
> Priority: **M**=Must(48h) · **S**=Should · **C**=Could. Effort: thấp(TB)/cao.

| UC | Tình huống | Hệ thống xử lý | Rule | P | Effort | FR |
|---|---|---|---|---|---|---|
| **UC-1** FAQ | Đặt khám thế nào? giờ? chuyên khoa? lịch BS? | Grounded answer + citation | R1,R9 | M | TB | FR-1 |
| **UC-2** BHYT & giá | Quyền lợi BHYT tim mạch, đồng chi trả, phí khám/CLS | General policy từ KB; không cam kết % cụ thể → điều hướng kế toán | R3 | M | TB | FR-5 |
| **UC-3** Đặt khám | Muốn đặt lịch | Nút/redirect Website/Zalo Mini App/Tổng đài; mock slot + roadmap | R6 | M | TB | FR-4 |
| **UC-4** ⚠️ Cấp cứu | Mô tả triệu chứng nguy hiểm (đau ngực dữ dội, khó thở, ngất…) | **Ngắt luồng**, banner nổi, hướng dẫn 115/khoa Cấp cứu BVT; KHÔNG tư vấn | **R2** | **M** | TB | FR-2 |
| **UC-5** Ngoài phạm vi | Y lệnh cá nhân, KQ CLS, phi BV | Từ chối lịch sự + điều hướng | R7,R4 | M | TB | FR-3 |
| **UC-6** Tái khám/vào viện | Thủ tục hẹn lại, vào viện | Theo `QT.25.01` bước 9 + `QT.25.04` | R1 | S | TB | FR-1 |
| **UC-7** Voice (bonus) | Hội thoại giọng nói | ASR → RAG → TTS tiếng Việt | R10 | C | Cao | FR-9 |

> UC-1→UC-5 cover **đủ 6 yêu cầu đề bài** (FAQ, thủ tục, BHYT, giá, giờ/BS, cấp cứu).

## 3. Domain Model (thực thể nghiệp vụ)
| Entity | Mô tả | Trường chính |
|---|---|---|
| `PatientQuery` | Câu hỏi trong phiên | sessionId, text, lang, createdAt |
| `KnowledgeChunk` | Mảnh KB được embed | id, source, sourceType(web/sop/form), title, text, embedding |
| `RetrievalResult` | Kết quả retrieve/rerank | chunkId, score, rerankScore |
| `Answer` | Câu trả lời | text, citations[], confidence, guardrailFlags |
| `GuardrailEvent` | Sự kiện safety | type(emergency/out_of_scope/refusal), triggered, handledAt |
| `Redirection` | Chuyển kênh | channel(web/zalo/hotline/emergency), url, reason |
| `Intent` | Phân loại ý định | faq/booking/bhyt/pricing/emergency/out_of_scope |

## 4. Domain Rules (tóm tắt — chi tiết `00-hospital-domain-rules` §4)
**R1** Grounding · **R2** Emergency kill switch · **R3** BHYT theo KB · **R4** Không can thiệp lâm sàng · **R5** Privacy · **R6** Booking redirect · **R7** Out-of-scope→điều hướng · **R8** Ưu tiên QĐ154 · **R9** Citation · **R10** Tiếng Việt đúng thuật ngữ.

## 5. Pain → Value map (dùng cho pitch ô 03)
| Pain | Giải pháp AI | Giá trị định lượng |
|---|---|---|
| Câu lặp quá tải tổng đài | Tự phục vụ 24/7 | Giảm **40–60%** cuộc gọi lặp (ước tính) |
| Info mâu thuẫn | Grounding 1 nguồn chính thức | Trải nghiệm đồng nhất |
| Không biết dấu hiệu nguy hiểm | Emergency triage (R2) | An toàn BN, chuyển Cấp cứu kịp |
| Đặt khám khó tìm | Redirect 1 chạm (R6) | Tăng conversion đặt khám |

## 6. KPIs business (đo pilot — ô 03)
- % cuộc gọi/hỏi lặp giảm (đo before/after sampling tại tổng đài).
- Tỷ lệ BN tự giải quyết (deflection rate) không cần nhân viên.
- Thời gian lấy info P50/P95.
- Số case cấp cứu được AI bắt đúng (safety KPI).

## 7. Liên quan
- [[00-hospital-domain-rules]] · [[03-functional-requirements]] · [[01-project-overview]]
- Nguồn SOP: `docs/refer/Quytrinh.md` (QT.25.01)
