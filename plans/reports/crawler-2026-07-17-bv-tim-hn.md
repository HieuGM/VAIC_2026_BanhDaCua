# Crawler Report — Bệnh viện Tim Hà Nội (benhvientimhanoi.vn)

**Crawl date:** 2026-07-17
**Output dir:** `D:/Project/VAIC_2026_BanhDaCua/data/seed/crawled/`

---

## 1. Source verification (STEP 0)

| Item | Result |
|---|---|
| Official domain | `https://benhvientimhanoi.vn/` (HTTP 200, 184 KB homepage) |
| Domain confidence | **Confirmed** — matches existing in-house groundtruth `groundtruth_gioi_thieu_benh_vien_tim_ha_noi.txt` (SOURCE_01..04) and competition brief |
| robots.txt | **Empty** (no rules) — crawl unrestricted |
| sitemap.xml | Valid, 5 entries lastmod 2025-08-12. Includes `/, bao-lanh-vien-phi, lich-lam-viec-cua-bac-sy/trang-1, thong-tin-yhoc-cap-nhat/trang-1, hen-kham/index.html` |
| `<meta name="robots">` on `/he-thong/hen-kham/index.html` | `noindex,nofollow` (page still reachable, but not indexed by search engines) |
| Anti-imposter check | Sitemap `tinnhiemmang.vn/handle_cert?id=benhvientimhanoi.vn` cert present in footer. No competing domain. |

Pages fetched (live): `/`, `/vn/cong/thong-tin/gioi-thieu-chung`, `/vn/cong/thong-tin/co-cau-to-chuc`, `/vi/chuyen-de/lich-lam-viec-cua-bac-sy/trang-1`, `/he-thong/hen-kham/index.html`, `/vi/chi-tiet/pho-bien-kien-thuc/huong-dan-dat-lich-qua-zalominiapps-tai-benh-vien-tim-ha-noi-co-so-1`.

---

## 2. Per-target results

### Target 1 — Departments (`departments.json`) — 36 records
- **Source:** `gioi-thieu-chung` (text-extractable) + `co-cau-to-chuc` (sơ đồ dạng ảnh — không trích xuất được).
- **Complete:** 11 khoa lâm sàng + 5 khoa cận lâm sàng + 9 phòng chức năng + 6 đơn nguyên + Trung tâm Đào tạo + PKĐK CS2 + 2 khu TN CS1 (TN1, TN3) + Khoa Điều trị ban ngày.
- **Partial/gap:** Trang `co-cau-to-chuc` chỉ có ảnh `sodo.jpg` → không extract được mã khoa, người trưởng khoa. Mã khoa (`code`) trong JSON do team tự đặt, không phải mã chính thức của BV.
- **Confidence:** high cho danh mục; low cho thứ tự phân cấp chi tiết.

### Target 2 — Doctors (`doctors.json`) — 68 records
- **PUBLIC:** Tên bác sĩ **CÓ** công bố công khai tại `https://benhvientimhanoi.vn/vi/chuyen-de/lich-lam-viec-cua-bac-sy/trang-1` — không cần bịa.
- **Records:** 4 ban lãnh đạo (Hiền, Nga, Hùng, Hoàng Văn) + ~30 bác sĩ TN1 CS1 + ~25 TN3 CS1 + 7 TN CS2 + 10 PKĐK CS2.
- **Học vị:** Trích từ prefix trong lịch (`TS.BS`, `ThS.BS`, `BSCKII`, `BSCKI`, `BS`, `BSNT`).
- **GAPS (anti-hallucination):**
  - Trang `ban-lanh-dao` **không hiển thị chức danh bằng văn bản** — 4 lãnh đạo ghi chức danh dựa trên (a) trang giới thiệu chung có nhắc `Hoàng Văn – Phó Giám đốc`, (b) chữ ký phê duyệt QT.25.01 của Nguyễn Sinh Hiền với vai trò Giám đốc. Mức confidence: medium.
  - **Không có bio đầy đủ, không có avatarUrl** (site không publish).
  - Department inferred từ phòng khám trực — không phải phòng khoa chức danh chính thức. Một bác sĩ có thể thuộc nhiều khu (TN1+TN3).
  - Lịch khám là snapshot 29/6–19/7/2026; danh sách bác sĩ có thể thay đổi.

### Target 3 — BHYT policies (`bhyt-policies.json`) — 7 records
- **Cơ sở pháp lý confirmed:** `TT22/2023/TT-BYT` (bảng giá BHYT hiện hành) + `TT13/2020/TT-BYT` (điều kiện thanh toán cắt lớp vi tính). Trích nguyên văn từ file `banggiaBHYT.txt` (source: trang Bảng giá dịch vụ).
- **Mức giá BHYT cụ thể (sample):** Khám bệnh 42.100đ; Giường Nội khoa 255.300đ; Hồi sức tích cực 786.300đ.
- **Quy trình BHYT:** VssID/CCCD chip accepted (QT.25.01 bước 3); Đồng chi trả line chuyên khoa; Giấy chuyển tuyến; Hẹn khám lại/đóng dấu chương trình BHYT cả năm.
- **GAP:** `% chi trả tuyến chuyên khoa tim mạch cụ thể` KHÔNG hiển thị dưới dạng con số trực tiếp — chỉ nói "ký cam kết chi trả khoản chênh lệch giá dịch vụ". Phải hỏi BA/bệnh viện.
- **Quy định ưu tiên 154/QĐ-BV (12/01/2024):** citing exists in QT.25.01 but **list of priority categories NOT published as text** → confidence=low, nội bộ.

### Target 6 — Booking channels (`channels.json`) — 12 records
- **Hotline 19001082:** CONFIRMED (24/7, cả CS1+CS2).
- **Hotline 0869032338:** CONFIRMED (tư vấn giờ hành chính CS1, từ trang Lịch khám).
- **Web booking URL:** CONFIRMED `https://benhvientimhanoi.vn/he-thong/hen-kham/index.html`.
- **Zalo Mini App:** **CONFIRMED CÓ** — `https://zalo.me/s/2972821668579995579/` (rút trích từ raw HTML bài viết `huong-dan-dat-lich-qua-zalominiapps-tai-benh-vien-tim-ha-noi-co-so-1`, đăng 24/03/2026). Áp dụng **CS1 ONLY**.
- **Fanpage Facebook:** `facebook.com/BenhVienTimHaNoi.vn` (footer).
- **YouTube:** `youtube.com/BenhVienTimHaNoi92TranHungDao/featured` (footer).
- **Email:** `cskh@timhanoi.vn` (footer).
- **Added hotlines NOT in brief:** 02437589090 / 0961972097 (PKĐK CS2), 02439425880 (CT xã hội), 02439427791 (CS2 hành chính), 0969655335 (CS2 24/24h).

### Target 7 — Working hours (`working-hours.md`)
- **Cơ sở 1 (92 Trần Hưng Đạo):** PK TN1 7:00/7:30–16:00/16:30 T2–T7; TN3 6:30/7:30–16:30.
- **Cơ sở 2 (695 Lạc Long Quân):** TN CS2 7:00–16:30 T2–T6; PKĐK 7:30–16:30 T2–T6.
- **Đặt hẹn qua điện thoại:** 8:00–16:00 T2–T7.
- **Cấp cứu:** 24/7.
- **GAP:** Lịch PKĐK một số chuyên khoa dao động theo tuần (TMH, Sản, Nội Hô hấp).

---

## 3. Top gaps & unresolved (for BA)

1. **Sơ đồ tổ chức** chỉ là ảnh (`/files/logo/sodo.jpg`) → cần OCR hoặc xin file nội bộ để có mã khoa + trưởng khoa.
2. **Chức danh Ban lãnh đạo** không hiển thị trên trang `ban-lanh-dao` — cần xin CV hoặc quyết định bổ nhiệm.
3. **% đồng chi trả BHYT tuyến chuyên khoa cụ thể** — không có con số trực tiếp, chỉ có "ký cam kết chênh lệch". Cần hỏi kế toán BHYT của BV.
4. **Danh mục đối tượng ưu tiên** theo Quy định 154/QĐ-BV (12/01/2024) không công khai — cần xin văn bản.
5. **Zalo Mini App CS2** chưa xác nhận có riêng (brief chỉ có CS1). Cần xác nhận với IT BV.
6. **Avatar/bio bác sĩ** không publish — nếu chatbot cần, phải xin từ phòng Tổ chức cán bộ.
7. **AvatarUrl = null** cho mọi bác sĩ (site không có trang profile bác sĩ).

## 4. Anti-hallucination compliance

- ✅ Mọi record đều có `sourceUrl` trỏ tới trang thực trên `benhvientimhanoi.vn`.
- ✅ Không bịa tên bác sĩ — tất cả lấy từ trang `lich-lam-viec-cua-bac-sy` công khai.
- ✅ Không bịa giá — tất cả giá BHYT từ `banggiaBHYT.txt` (raw file có sẵn, source trang Bảng giá).
- ✅ Mọi trường "inferred" đánh dấu `confidence: medium|low` (4 lãnh đạo, QĐ 154).
- ✅ Trường thiếu → null/omit (avatarUrl, chức danh lãnh đạo).
- ✅ Email/phone/screenshot URL đều verified bằng curl trực tiếp.

## 5. Files delivered

```
D:/Project/VAIC_2026_BanhDaCua/data/seed/crawled/
├── departments.json    36 records  (11 KB)
├── doctors.json        68 records  (21 KB)
├── bhyt-policies.json   7 records  (6.8 KB)
├── channels.json       12 records  (4.2 KB)
└── working-hours.md    (~4.4 KB)
```

No git commits made (per task spec).

## 6. Unresolved questions

- Q1: Trang `co-cau-to-chuc` dạng ảnh `sodo.jpg` — BA có file PDF/Word chính thức để trích xuất cơ cấu tổ chức chi tiết (mã khoa, trưởng khoa, phân cấp)? → Cần xin BV.
- Q2: Có nên OCR ảnh `sodo.jpg` để bổ sung nhánh còn thiếu? (Cần xác nhận độ mới của ảnh — lastmod 2025-08-12.)
- Q3: Zalo Mini App có version CS2 không? Có OA ID riêng không?
- Q4: Có nên crawl thêm trang `bang-gia-dich-vu` để extract toàn bộ 800+ dòng giá BHYT / giá dịch vụ? Hiện chỉ sample các dòng chính.
- Q5: Trang `Bảo lãnh viện phí` (có trong sitemap) có thể bổ sung chính sách BHYT chi tiết — có cần fetch thêm?
