# 02 — Business Analysis

> Actor, use case, domain model, pain points. Đọc sau `00-*`.
> Cập nhật: 2026-07-17 · Trạng thái: Draft v1.

---

## 1. Stakeholders

| Actor | Mục tiêu | Đau thơ |
|---|---|---|
| **Bệnh nhân (BN) & người nhà** | Được info nhanh, chính xác, 24/7; biết phải làm gì | Chờ tổng đài, info mâu thuẫn, không biết quy trình |
| **Nhân viên CSKH / tổng đài / reception** | Giảm câu hỏi lặp, tập sự cố phức tạp | Quá tải câu lặp, trả lời chậm |
| **Phòng IT BVT** | Triển khai an toàn trên infra BV, bảo mật | Phải on-prem-capable, tuân thủ NĐ13/Luật KBChB |
| **Ban lãnh đạo BVT** | Tăng trải nghiệm BN, giảm chi phí, image | ROI, pilot pathway |
| **Giám khảo VAIC** | Đánh giá engineering + AI + pilot + safety | Rubric 6 ô (xem `00-competition`) |

## 2. Use Cases

### UC-1: Hỏi thông tin chung (FAQ)
- **Ai:** BN/người nhà.
- **Muốn:** Đặt khám thế nào? giờ làm việc? chuyên khoa nào? lịch BS?
- **Hệ thống:** Trả lời grounded + citation từ KB.
- **AC:** câu trả lời có nguồn; đúng theo KB.

### UC-2: Hỏi quyền lợi BHYT & giá
- **Muốn:** Quyền lợi BHYT tim mạch, đồng chi trả, phí khám, phí CLS.
- **AC:** trả lời general policy từ KB; KHÔNG cam kết % cụ thể nếu thiếu → điều hướng quầy kế toán (R3).

### UC-3: Đặt khám (redirect)
- **Muốn:** Đặt lịch khám.
- **Hệ thống:** Hiển thị nút/redirect → Website / Zalo Mini App / Tổng đài (R6). Nếu có API → tra slot (mock + roadmap).
- **AC:** nút điều hướng đúng kênh chính thức.

### UC-4: Phát hiện cấp cứu (KILL SWITCH)
- **Kích:** mô tả triệu chứng nguy hiểm (đau ngực dữ dội, khó thở, ngất…).
- **Hệ thống:** **ngắt luồng thường**, cảnh báo nổi, hướng dẫn 115 / khoa Cấp cứu BVT (R2). KHÔNG tư vấn điều trị.
- **AC:** recall 100% trên test set cấp cứu.

### UC-5: Câu ngoài phạm vi
- **Kích:** hỏi y lệnh cá nhân, kết quả CLS, chủ đề phi BV.
- **Hệ thống:** từ chối lịch sự + điều hướng (R7, R4).

### UC-6: Tái khám / vào viện
- **Muốn:** thủ tục hẹn khám lại, vào viện.
- **AC:** trả lời theo `QT.25.01` bước 9 + `QT.25.04`.

### UC-7 (bonus): Hội thoại giọng nói
- ASR → RAG → TTS tiếng Việt.

## 3. Domain Model (thực thể nghiệp vụ)

| Entity | Mô tả | Trường chính (gợi ý) |
|---|---|---|
| `PatientQuery` | Câu hỏi phiên | sessionId, text, lang, createdAt |
| `KnowledgeChunk` | Mảnh KB được embed | id, source, sourceType(web/sop/form), title, text, embedding |
| `RetrievalResult` | Kết quả retrieve | chunkId, score, rerankScore |
| `Answer` | Câu trả lời | text, citations[], confidence, guardrailFlags |
| `GuardrailEvent` | Sự kiện safety | type(emergency/out_of_scope/refusal), triggered, handledAt |
| `Redirection` | Chuyển kênh | channel(web/zalo/hotline/emergency), url, reason |
| `Intent` | Phân loại ý định | faq/booking/bhyt/pricing/emergency/out_of_scope |

## 4. Domain Rules (tóm tắt — chi tiết `00-hospital-domain-rules` §4)
R1 Grounding · R2 Emergency kill switch · R3 BHYT theo KB · R4 Không can thiệp lâm sàng · R5 Privacy · R6 Booking redirect · R7 Out-of-scope → điều hướng · R8 Ưu tiên QĐ154 · R9 Citation · R10 Tiếng Việt đúng thuật ngữ.

## 5. Pain → Value map (dùng cho pitch rubric 03)
| Pain | Giải pháp AI | Giá trị định lượng |
|---|---|---|
| Câu lặp quá tải tổng đài | Tự phục vụ 24/7 | Giảm 40–60% cuộc gọi lặp (ước tính) |
| Info mâu thuẫn | Grounding 1 nguồn chính thức | Trải nghiệm đồng nhất |
| Không biết dấu hiệu nguy hiểm | Emergency triage | An toàn BN, chuyển Cấp cứu kịp |
| Đặt khám khó tìm | Redirect 1 chạm | Tăng conversion đặt khám |

## 6. Liên quan
- [[00-hospital-domain-rules]] · [[03-functional-requirements]] · [[01-project-overview]]
