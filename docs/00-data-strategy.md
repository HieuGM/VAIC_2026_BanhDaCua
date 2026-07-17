# 00 — Data Strategy: KB vs Database

> **File nền tảng — BẮT BUỘC ĐỌC.** Phân biệt **Knowledge Base (KB)** vs **Database (DB)**, map nguồn dữ liệu hiện có, liệt kê data còn thiếu.
> **Đọc cùng:** `00-hospital-domain-rules`, `06-database-design`, `brainstorming`.
> Cập nhật: 2026-07-17 · Phiên bản: **v1.0** · Trạng thái: **Review** (owner: BA + Spring Boot + AI).

---

## 1. Phân biệt KB vs Database (cốt lõi)

| | **Database (PostgreSQL — Spring Boot)** | **Knowledge Base (text → Qdrant vectors — AI)** |
|---|---|---|
| **Dạng** | Cấu trúc, **bảng, cột** (tabular) | Văn bản **prose** (câu/đoạn) |
| **Truy vấn** | SQL: filter/sort/join chính xác | Semantic: embedding + similarity |
| **Loại câu hỏi** | **Look-up chính xác**: "Giá khám?", "BS X khám phòng mấy thứ mấy?", "Số ĐT đặt khám?" | **Mở, diễn giải**: "Quy trình khám thế nào?", "Bệnh viện có chuyên khoa gì, thế mạnh gì?" |
| **Trả lời** | Row chính xác (42.100đ, phòng 3 thứ 5) | Đoạn văn trích từ KB + citation |
| **Hallucination?** | Không — số liệu exact, citable theo row | Phải guardrail: chỉ khi chunk đủ score (R1,R7) |
| **Sở hữu** | Spring Boot (schema `hospital`) | AI team (Qdrant; text nguồn lưu ở `kb_articles` PG) |

> **Nguyên tắc:** *fact chính xác → DB; narrative/mở → KB.* Cùng 1 file nguồn thường **feed cả hai** (xem §3).

## 2. Kiến trúc dữ liệu 3 lớp

```
            ┌─ DATABASE (PostgreSQL, Spring Boot) ─────────────────────┐
 sources ──▶│  schema `hospital`: bảng cấu trúc (doctors, services,     │
 (raw .txt) │   prices, schedules, procedures, kb_articles, faqs...)    │
            └───────────────┬───────────────────────────────────────────┘
                            │  kb_articles / faqs (text nguồn)
                            ▼
            ┌─ KB (Qdrant, AI team) ───────────────────────────────────┐
            │  collection kb_chunks: chunk + embed (BGE-M3) → retrieve  │
            └───────────────────────────────────────────────────────────┘
```

- **PG `kb_articles`** = kho text nguồn (source-of-truth). Spring Boot lưu, **AI team chunk+embed sang Qdrant**.
- → DB và KB **không tách bạch hoàn toàn**: text KB cũng nằm trong PG, chỉ vector nằm Qdrant.

## 3. Data inventory — map 6 file hiện có (`docs/data/`)

| File | Loại | → Database (cấu trúc) | → KB (text→vector) |
|---|---|---|---|
| `GiaDVBV_tim_HN.txt` (bảng giá DV, NQ45/2024) | bảng + ghi chú | `services`, `service_prices` (nhóm: khám+giường, XN, thủ thuật+CĐHA, CNT, CLVT, can thiệp TM) | ghi chú chính sách giá → `kb_articles` |
| `banggiaBHYT.txt` (TT22/2023) | bảng (`STT\|mã\|tên\|giá\|ghichú`) | `service_prices` (audience=BHYT, mã tương đương), `bhyt_policies` | policy TT22/2023/TT13/2020 → `bhyt_policies.details_md` |
| `Lich_kham_benh_29.6-19.7.2026.txt` | bảng (tuần\|khu\|phòng\|ngày\|BS) | `doctors` (tên+học vị TS/ThS/BSCKII), `doctor_schedules`, `departments` (khu TN1/2), `support_channels` (19001082, 0869032338, web, fanpage) | (tùy chọn) "cách đọc lịch" |
| `Huong_dan_dat_lich_kham.txt` | prose + struct | `support_channels` (hotline C1/C2, web booking URL, PKĐK), `hospital_info` (C1: 92 Trần Hưng Đạo · C2: 695 Lạc Long Quân) | hướng dẫn đặt khám → `kb_articles`/`faqs` |
| `groundtruth_gioi_thieu...txt` | prose + SOURCE URL | `hospital_info` (tên, sứ mệnh, cơ cấu) | article giới thiệu → `kb_articles` (SOURCE_01–04) |
| `QUY_TRINH_DON_TIEP...txt` (=Quytrinh.md) | prose + struct | `procedures` (QT.25.01, 11 bước) | SOP narrative → `kb_articles` |

> **Chất lượng:** tên BS, giá, SĐT, địa chỉ = **thật, chính thức** (từ site/SOP BV) → an toàn dùng, không hallucinate.

## 4. Data còn THIẾU (cần BA/team bổ sung)

| # | Gap | Ảnh hưởng | Đâu |
|---|---|---|---|
| 1 | **HD.25.01 + bộ từ khoá cấp cứu** (đau ngức dữ dội, khó thở, ngất, vã mồ hôi lạnh, tê/yếu nửa người…) | **R2 kill switch** — sống còn ô 05 | `data/content/emergency.md` |
| 2 | **Department roster + mô tả** (chuyên khoa có tên: tim mạch can thiệp, RL nhịp, tim bẩm sinh… + tầng/giờ) | UC-1 FAQ chuyên khoa | `data/seed/departments.json` |
| 3 | **Doctor metadata** (BS→chuyên khoa, bio, avatar) — lịch chỉ có tên+học vị | UC-1 tra BS | `data/seed/doctors.json` |
| 4 | **Golden FAQ Q&A ≥30** (7 nhóm: đặt khám, quy trình, BHYT, giá, giờ/BS, cấp cứu, tái khám) | eval + KB | `data/seed/faqs.json` |
| 5 | **BHYT policy prose** (quyền lợi, đồng chi trả, chuyển tuyến, VssID/CCCD chip) — chỉ đang có bảng giá | UC-2 | `data/content/bhyt/` |
| 6 | **QT.25.04 (thủ tục vào viện)** — SOP nhắc nhưng chưa có nội dung | UC-6 | `data/content/procedures/` |
| 7 | **QĐ154 nhóm ưu tiên** — SOP nhắc, chưa có DS | R8 | `data/seed/priority-groups.json` |
| 8 | **Giờ làm việc/khám theo phòng** (đang rời rạc 8h–16h T2–T7) | UC-1 giờ | `data/seed/` |

## 5. Folder convention (đề xuất — gộp về root `data/`)

```
data/
├── raw/        ← 6 file docs/data/*.txt HIỆN TẠI (scrape/extract nguồn) — chuyển vào đây
├── content/    ← markdown KB curated: bhyt/, emergency/, procedures/
└── seed/       ← JSON/CSV cấu trúc (parse từ raw) → nạp PG (Flyway/seed loader)
```

> **Action đề xuất:** dời `docs/data/*.txt` → `data/raw/`. `content/`+`seed/` là derived (parse thủ công/script từ raw). `raw` lớn → gitignore; `content`+`seed` commit (source-of-truth demo).

## 6. Sở hữu & anti-hallucination
- **BA** owns `raw/` + `content/` (curate, ghi SOURCE URL).
- **Spring Boot dev** owns `seed/` (parse raw→JSON/CSV) + PG `hospital`.
- **AI team** owns `kb_articles`→Qdrant ingest + schema `ai`.
- **Kỷ luật (R1):** *chỉ ghi nội dung xuất hiện trên nguồn chính thức, KHÔNG suy diễn* — đã làm đúng ở `groundtruth_*` (ghi rõ "không tự suy diễn chức danh/dữ liệu thiếu"). Áp dụng cho **toàn bộ** data. BS/giá/SĐT từ lịch+bảng giá = thật → dùng được; bất cứ gì tự biên soạn → ghi rõ "sample/representative" + SOURCE.

## 7. Liên quan
- [[06-database-design]] · [[00-hospital-domain-rules]] · [[02-business-analysis]]
- Nguồn gốc: `docs/refer/Quytrinh.md` · `docs/data/` · `brainstorming` §Verify
