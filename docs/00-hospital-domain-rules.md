# 00 — Nghiệp vụ & Quy tắc domain Bệnh viện Tim Hà Nội

> **File nền tảng — BẮT BUỘC ĐỌC.** Nguồn sự thật (ground truth) cho toàn bộ AI grounding & business logic.
> Nguồn: Đề bài "Hanoi Heart Hospital" + SOP `QT.25.01` (`docs/refer/Quytrinh.md`).
> Cập nhật: 2026-07-17 · Trạng thái: Living doc.

---

## 1. Fact bệnh viện

| Mục | Giá trị |
|---|---|
| Tên | Bệnh viện Tim Hà Nội (BVT) |
| Hạng | Bệnh viện chuyên khoa tim mạch **hạng I** — trung tâm chuyển tuyến đầu ngành tim mạch |
| Lưu lượng | **~2.500–3.000 bệnh nhân ngoại trú/ngày** |
| Phạm vi SOP | Khu Khám bệnh **Tự nguyện 1, Cơ sở 1** |
| Mã quy trình | QT.25.01 · Ban hành 05/12/2024 · Lần 07 |

---

## 2. Glossary (thuật ngữ — AI PHẢI dùng đúng)

| Viết tắt | Nghĩa | Viết tắt | Nghĩa |
|---|---|---|---|
| BHYT | Bảo hiểm y tế | BN | Bệnh nhân |
| CCCD | Căn cước công dân | CLS | Cận lâm sàng (siêu âm, XQ, ĐT, XN…) |
| HA | Huyết áp | XN | Xét nghiệm |
| BVT | Bệnh viện Tim | XQ | X-Quang |
| KQ | Kết quả | TKQ | Trả kết quả |
| HS | Hồ sơ | Bs | Bác sĩ |
| ĐD | Điều dưỡng | TS / Ths | Tiến sỹ / Thạc sỹ |
| DHST | Dấu hiệu sinh tồn | HDV | Hướng dẫn viên |

---

## 3. Quy trình đón tiếp & khám ngoại trú (11 bước — QT.25.01)

| # | Bước | Trách nhiệm | Điểm AI liên quan |
|---|---|---|---|
| 1 | Nhận đặt lịch khám Tự nguyện 1 + tư vấn quy trình (ĐT/Web/Fanpage) | NV CSKH (Phòng Công tác xã hội) | **Đặt khám redirect**, FAQ quy trình |
| 2 | Lấy số tiếp nhận (có lịch → quầy tư vấn; không lịch → cây lấy số tự động) | HDV tiếp đón | Hướng dẫn lấy số |
| 3 | Đăng ký khám (BHYT/không, mới/tái khám, giấy chuyển viện, VssID/CCCD gắn chip, CCCD) | NV tư vấn tiếp đón | Quy trình + giấy tờ cần mang |
| 4 | Thu phí + xử lý BHYT, đóng dấu ưu tiên (QĐ154) | Kế toán | Bảng giá, quyền BHYT |
| 5 | Đo DHST (HA, mạch, chiều cao, cân nặng, BMI, nhiệt độ) | NV đo DHST | ⚠️ Bất thường → cấp cứu (HD.25.01) |
| 6 | Phát số phân phòng; hướng dẫn CLS; kiểm soát KQ; bất thường → cấp cứu | ĐD/HDV bàn TKQ | ⚠️ Triage cấp cứu (HD.25.01) |
| 7 | Hướng dẫn BN chờ theo phòng (màn hình 4 số: phòng+STT, loa gọi) | HDV hành lang | Hướng dẫn khu vực chờ |
| 8 | Khám, kê đơn, giải thích, hẹn khám lại, chuyển điều trị ban ngày/cấp cứu/vào viện | Bs phòng khám | ❌ AI KHÔNG can thiệp lâm sàng |
| 9 | Hẹn tái khám, đóng dấu BHYT (nội trú/chương trình bệnh mãn tính), thủ tục vào viện (QT.25.04) | ĐD/HDV hành chính | Hẹn khám lại, thủ tục BHYT |
| 10 | Duyệt đơn BHYT, thu phí chênh lệch/đơn dịch vụ | Kế toán thuốc | Quyền lợi thuốc BHYT |
| 11 | Lĩnh thuốc BHYT / mua thuốc → kết thúc | Nhà dịch vụ, quầy thuốc | Kết thúc luồng |

### Các chỉ định CLS thường gặp (tầng thực hiện)
Siêu âm tim (T2) · Điện tim (T2) · Siêu âm bụng (T1) · SA mạch/thận-chi/tuyến giáp (T2) · X-Quang (T1) · XN máu (T1) · ABI (T1).

### Lưu ý cho BN (từ SOP — AI có thể nhắc lại)
- BN ngồi chờ sảnh sofa khu KBTN1; **không tự ý đi làm xét nghiệm**, **không tự xuống T1**. NV gọi tên theo thứ tự.
- **Không cần chờ lấy KQ** — KQ tự chuyển về khu chờ KBTN1 (T2).

### Văn bản/forms liên quan (AI phải biết tồn tại, không bịa nội dung)
- `BM.25.01.01` — Phiếu tiếp nhận ban đầu (HA, mạch, chiều cao, cân nặng, BMI, nhiệt độ).
- Phiếu hướng dẫn làm xét nghiệm (bảng chỉ định + tầng).
- `HD.25.01` — Hướng dẫn chuyển cấp cứu (xử lý bất thường DHST/CLS).
- `QT.25.04` — Quy trình thủ tục vào viện/chuyển tuyến.
- `QĐ 154` (của BVT) — Danh mục đối tượng ưu tiên.

---

## 4. DOMAIN RULES — AI PHẢI THỰC THI (R1–R10)

> Đây là hard rules. Vi phạm = lỗi nghiêm trọng (đánh vào ô Safety 05).

- **R1 — Grounding bắt buộc.** Mọi câu trả lời phải dựa trên KB chính thức (website BV + SOP `QT.25.01` + forms). Không có bằng chứng → kích hoạt R7.
- **R2 — Xử lý cấp cứu (kill switch).** Phát hiện dấu hiệu: đau ngực dữ dội/ép chặt, khó thở, ngất/xỉu, vã mồ hôi lạnh, teo cơ mặt/nửa người… → **KHÔNG** tư vấn/kê đơn/chẩn đoán → **ngay lập tức** hướng dẫn gọi **115** hoặc đến **khoa Cấp cứu BVT** theo `HD.25.01`. Phản hồi ưu tiên cao nhất, ngắt luồng thường.
- **R3 — BHYT theo KB.** Chỉ giải thích quyền lợi/general policy có trong KB. **Không** cam kết mức chi trả/phần trăm cụ thể nếu thiếu thông tin → điều hướng quầy kế toán.
- **R4 — Không can thiệp lâm sàng.** Không chẩn đoán, không kê đơn, không giải thích kết quả CLS/đơn thuốc, không khuyến nghị liều. → Điều hướng bác sĩ.
- **R5 — Privacy/Bảo mật.** Không yêu cầu/lưu PII không cần thiết (CCCD, số HS, chẩn đoán). Mã hóa at-rest/in-transit. Tuân thủ **NĐ 13/2023/NĐ-CP** + **Luật Khám bệnh, chữa bệnh**. Khả năng xoá session.
- **R6 — Booking redirect.** Yêu cầu đặt/hẹn khám → điều hướng kênh chính thức: **Website / Zalo Mini App / Tổng đài CSKH** (theo SOP bước 1). AI không tự đặt lịch nếu chưa tích hợp API thật.
- **R7 — Out-of-scope → từ chối lịch sự + điều hướng.** Câu ngoài phạm vi CSKH (y lệnh, kết quả cá nhân, chủ đề phi y tế của BV) → nói rõ không hỗ trợ + đề xuất kênh phù hợp.
- **R8 — Đối tượng ưu tiên (QĐ154).** Nhắc quyền ưu tiên nếu có trong KB; không tự xếp loại ưu tiên cho cá nhân.
- **R9 — Citation.** Mỗi câu trả lời kèm nguồn (tên trang KB / bước SOP / mã form).
- **R10 — Ngôn ngữ.** Tiếng Việt tự nhiên, thuật ngữ y khoa đúng (xem §2), giọng điệu chuyên nghiệp, đồng cảm, không gây hoang mang.

---

## 5. Câu hỏi thường gặp (nhóm chủ đề — seed KB)

1. **Đặt khám:** cách đặt, chọn bác sĩ, khu Tự nguyện 1, mang giấy tờ gì.
2. **Quy trình khám:** 11 bước rút gọn, lấy số, đo DHST, làm CLS, lĩnh thuốc.
3. **BHYT:** quyền lợi, giấy chuyển tuyến, VssID/CCCD chip, đồng chi trả.
4. **Giá dịch vụ:** phí khám, chênh lệch BHYT, phí CLS (theo KB công khai).
5. **Giờ làm việc / lịch bác sĩ:** khung giờ, chuyên khoa, lịch trực.
6. **Cấp cứu:** dấu hiệu nguy hiểm → 115 / khoa Cấp cứu.
7. **Tái khám / vào viện:** hẹn khám lại, thủ tục QT.25.04.

---

## 6. Liên quan

- Tiêu chí & nguyên tắc đề tài: [[00-competition-rubric-and-principles]]
- Phân tích business (actor/use case): [[02-business-analysis]]
- Yêu cầu chức năng (FR): [[03-functional-requirements]]
- SOP gốc (QT.25.01): `docs/refer/Quytrinh.md`
