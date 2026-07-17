# 00 — Tiêu chí chấm điểm & Nguyên tắc đề tài (VAIC 2026)

> **File nền tảng — BẮT BUỘC ĐỌC ĐẦU TIÊN.** Mọi thành viên & AI agent PHẢI đọc file này trước khi làm bất kỳ task nào.
> Nguồn: Vietnam AI Innovation Challenge (VAIC) 2026 — RUBRIC chính thức (100đ) + Đề bài *"Intelligent AI Customer Care Assistant for Hanoi Heart Hospital"*.
> Cập nhật: 2026-07-17 · Trạng thái: Living doc.

---

## 1. Tổng quan cuộc thi

| Mục | Giá trị |
|---|---|
| Tên | Vietnam AI Innovation Challenge 2026 (VAIC) |
| Đề bài | Trợ lý CSKH AI tích hợp website **Bệnh viện Tim Hà Nội (BV Tim HN)** |
| Mục tiêu | Giảm tải câu hỏi lặp cho tổng đài/website/reception; trả lời chính sách/thủ tục/BHYT/giá/lich bác sĩ; phát hiện cấp cứu |
| Domain | **Y tế** — nghiêm ngặt về an toàn thông tin, **KHÔNG được hallucinate** |
| Thời gian | **48 giờ** (hackathon) |
| Team | 3 web + 2 AI engineer + 1 BA (tất cả dùng AI agent) |

---

## 2. Bảng tiêu chí chấm điểm (100đ) — RUBRIC

| # | Tiêu chí | Trọng số | Định hướng chấm (suy diễn từ category + đề bài) |
|---|---|---:|---|
| **01** | **Technical Implementation & Engineering Depth** | **20** | Code chạy thật, kiến trúc vững, xử lý edge case, CI/CD, chất lượng engineering. Không demo tĩnh. |
| **02** | **AI-Native Architecture & Innovation** | **20** | RAG/agent design xứng đáng domain, không chỉ "chatbot bọc API". Đổi mới phù hợp y tế (grounding, triage, multi-channel). |
| **03** | **Business Viability & Pilot Pathway** | **20** | Có đường **pilot thật** tại BV, ROI định lượng, khả năng triển khai, business case. Chiều dễ zero nhất nếu làm ngoài hoàn toàn. |
| **04** | **AI-Native UX & Design Thinking** | **15** | UX hội thoại tự nhiên tiếng Việt, design thinking, accessibility, handoff mượt sang kênh người/nút đặt khám. |
| **05** | **AI Safety, Grounding & Trust** | **15** | **KHÔNG hallucinate**, grounding có trích nguồn, xử lý cấp cứu đúng, bảo mật dữ liệu y tế. |
| **06** | **Presentation, Demo & Defensibility** | **10** | Demo mượt ≤5', slide thuyết phục, **biện hộ được** mọi quyết định kỹ thuật (defensible). |

> **Trọng số chiến lược:** 01+02+03 = **60đ** (3 ô nặng nhất) + 05 = **15đ** (kill switch). Tổng 75đ tập trung ở "engineering thật + kiến trúc AI + pilot + safety". 04+06 = 25đ bổ trợ.

---

## 3. Decode từng tiêu chí → "Lấy điểm thế nào"

### 01 — Technical Implementation (20đ)
- ✅ Code production-grade: typing, error handling, logging, test tối thiểu.
- ✅ Repo công khai có README rõ, Docker chạy 1 lệnh.
- ✅ Edge case: KB thiếu, query ngoài phạm vi, input rác tiếng Việt (dấu, teencode).
- ✅ Không hardcode; config qua env.

### 02 — AI-Native Architecture (20đ)
- ✅ Pipeline RAG rõ: ingest (crawl + SOP) → chunk → embed → vector store → retrieve → rerank → LLM grounded → citation.
- ✅ Guardrail tách lớp (classifier emergency + intent router + refusal gate).
- ✅ Innovation điểm cộng: hybrid search, confidence score, multi-turn memory, ASR/TTS tiếng Việt, agent tool-calling (lookup lịch/giá).
- ❌ "Bọc GPT" thuần = mất nặng ô này.

### 03 — Business Viability & Pilot (20đ)
- ✅ Pilot pathway cụ thể: demo trên VPS → container → deploy sang infra BV → tích hợp API/Zalo thật (roadmap).
- ✅ ROI: giảm % cuộc gọi tổng đài, tiết kiệm FTE reception, giảm thời gian chờ thông tin.
- ✅ Stakeholder map: BV (IT, CS, lâm sàng), bệnh nhân, người nhà.
- ⚠️ **Khoảng cách lớn nhất** — phải có kế hoạch thật ngay cả khi API chưa có.

### 04 — AI-Native UX (15đ)
- ✅ Chat UI y tế: tin cậy, rõ nguồn, nút hành động (đặt khám, gọi cấp cứu), suggested questions.
- ✅ Handoff sang người (hotline) khi AI hết khả năng.
- ✅ Responsive mobile (bệnh nhân dùng điện thoại), a11y cơ bản.
- ✅ Giọng điệu chuyên nghiệp, đồng cảm, không lo lắng hóa.

### 05 — Safety, Grounding & Trust (15đ) — **KILL SWITCH**
- ✅ Mọi trả lời **ground vào KB chính thức** (website BV + SOP `QT.25.01`), **trích nguồn**.
- ✅ Thiếu TT → nói rõ + điều hướng kênh hỗ trợ; **KHÔNG bịa**.
- ✅ **Phát hiện cấp cứu** (đau ngực dữ dội, khó thở, ngất, teo ngực…) → KHÔNG tư vấn điều trị → chuyển khoa Cấp cứu / 115.
- ✅ Không chẩn đoán, không kê đơn, không giải thích kết quả CLS.
- ✅ Privacy: không thu PII không cần thiết, mã hóa, tuân thủ NĐ 13/2023 + Luật Khám bệnh, chữa bệnh.

### 06 — Presentation & Defensibility (10đ)
- ✅ Slide: problem → solution → architecture → demo → pilot → safety.
- ✅ Demo ≤5' chạy thật trên deployed URL.
- ✅ Defensible: giải thích **tại sao** chọn X (RAG thuần vs fine-tune, cloud vs on-prem, mock vs real API).

---

## 4. Deliverables (bắt buộc nộp)

| # | Đầu ra | Ghi chú |
|---|---|---|
| 1 | **Presentation slides** | Problem → Solution → Arch → Demo → Pilot → Safety |
| 2 | **Demo video (≤ 5 phút)** | Quay màn hình demo thật + voice-over |
| 3 | **GitHub repository (public)** | Repo này; README rõ ràng |
| 4 | **Live deployed URL** | Demo trên VPS (Docker) |
| 5 | **Project description** | Text ngắn giới thiệu dự án |
| 6 | **PDF** | Gói tài liệu (có thể là slide/report xuất PDF) |

---

## 5. Nguyên tắc chiến lược (smart 48h)

1. **Safety trước, tính năng sau.** Ô 05 là điều kiện sống còn ở y tế → làm sai = loại, bất kể ô khác cao.
2. **Chọn lát cắt hẹp + sâu + defensible.** 48h không làm hết → ưu tiên 01+02+03+05. UX(04) đẹp vừa đủ, không over-polish.
3. **Demo thật trên VPS**, không mock-up tĩnh. Docker 1 lệnh chạy.
4. **Mock integration có kế hoạch thật.** API/Zalo chưa có → mock + tài liệu hóa roadmap pilot rõ (ôm điểm 03).
5. **Mỗi trả lời phải có nguồn.** Citation là bằng chứng grounding (ôm điểm 05).
6. **Agent dùng docs là trung tâm.** Mọi spec chỉ tồn tại trong `docs/` — code agent đọc docs để làm.
7. **Song song hóa, không phụ thuộc.** Chia luồng web / AI / data độc lập (xem `10-development-roadmap.md`).

---

## 6. Out-of-scope (KHÔNG làm trong 48h)

- Chẩn đoán y khoa / khuyến nghị điều trị / giải thích kết quả.
- Tích hợp thật HIS/API BV (chỉ mock + roadmap).
- Đào tạo fine-tune model riêng (chỉ prompt + RAG).
- Auth bệnh nhân / hồ sơ bệnh án trực tuyến (PII).
- Mobile native app (chỉ web responsive).

---

## 7. Liên quan

- Nghiệp vụ/domain rule: [[00-hospital-domain-rules]]
- Tổng quan dự án & stack: [[01-project-overview]]
- Quy trình 11 bước (SOP gốc): `docs/refer/Quytrinh.md` (QT.25.01)
