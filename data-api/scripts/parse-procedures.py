#!/usr/bin/env python3
"""
parse-procedures.py — Emit V8__seed_procedures.sql from raw SOP text.

Source: data/raw/QUY_TRINH_DON_TIEP_BENH_NHAN_KHU_TU_NGUYEN_1_CS1.txt
Per docs/06 the SOP is QT.25.01 (12 steps as written in the source; the docs
say "11" but the file actually lists 12 numbered steps; we seed all 12).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "data" / "raw" / "QUY_TRINH_DON_TIEP_BENH_NHAN_KHU_TU_NGUYEN_1_CS1.txt"
OUT = (REPO / "data-api" / "src" / "main" / "resources" / "db" / "migration"
       / "V8__seed_procedures.sql")
SOURCE_URL = "https://benhvientimhanoi.vn/vn/huong-dan-kham-benh/quy-trinh-kham-chua-benh"
TITLE = "Quy trinh don tiep benh nhan va kham chua benh ngoai tru tai khu TN1 Co so 1"
SOURCE_DOC = "QT.25.01 (lan ban hành 07, 05/12/2024) - Bệnh viện Tim Hà Nội"

STEPS = [
    (1,  "Nhận đặt lịch khám TN1 và tư vấn",
         "Nhận đặt lịch khám Tự nguyện 1 và tư vấn quy trình khám qua điện thoại, Website, Fanpage. BN đặt lịch được nhân viên tư vấn và thông báo thông tin đã đặt khám gồm: mã đặt lịch (số thứ tự tự tiếp nhận), ngày khám và bác sĩ khám (nếu có). BN không đặt lịch đến lấy số trực tiếp tại cây lấy số tự động khu Tự nguyện 1.",
         "Nhân viên tổ chăm sóc khách hàng - phòng Công tác xã hội", "BM.25.01.01"),
    (2,  "BN lấy số để tiếp nhận",
         "BN đã đặt lịch vào thẳng quầy tư vấn dành cho BN đã đặt lịch trước. BN không đặt lịch đến lấy số thứ tự tại cây lấy số tự động. HDV hướng dẫn BN khu vực lấy số và ổn định trật tự khu vực chờ tiếp nhận.",
         "Nhân viên tổ tư vấn và tiếp đón khám bệnh - Hướng dẫn viên", None),
    (3,  "Tiếp nhận thông tin đăng ký khám",
         "Tiếp nhận thông tin đăng ký khám bệnh Tự nguyện 1 (BN có BHYT/không BHYT; tái khám/khám mới). Khai phiếu đăng ký, xuất trình CCCD hoặc giấy tờ tùy thân, thẻ BHYT/VssID/CCCD gắn chip, giấy chuyển viện (nếu có). BN có giấy chuyển tuyến ký cam kết đồng ý chi trả chênh lệch giá dịch vụ. BN thuộc diện ưu tiên (QĐ154) được đóng dấu 'ưu tiên'.",
         "Nhân viên tổ tư vấn và tiếp đón khám bệnh", None),
    (4,  "Thu phí và tiếp nhận BHYT (nếu có)",
         "BN có BHYT xuất trình các giấy tờ cần thiết. Nhân viên kế toán thông báo phí khám, phí chênh lệch BHYT (nếu có) và thực hiện thu phí. Hướng dẫn BN sang bàn đo dấu hiệu sinh tồn, chiều cao, cân nặng.",
         "Nhân viên kế toán", None),
    (5,  "Đo dấu hiệu sinh tồn, chiều cao, cân nặng",
         "Tại bàn đo DHST: nhân viên đo DHST, chiều cao, cân nặng, ghi phiếu tiếp nhận. Ưu tiên thực hiện cho những BN thuộc đối tượng ưu tiên. Các trường hợp bất thường báo bác sĩ hoặc chuyển cấp cứu theo HD.25.01.",
         "Nhân viên đo dấu hiệu sinh tồn", None),
    (6,  "Phân phòng và hướng dẫn làm CLS",
         "Điều dưỡng phát số phân phòng cho BN chưa được khám. Với BN có chỉ định cận lâm sàng: hướng dẫn các mục phải làm (siêu âm tim, siêu âm bụng mạch, XQ, điện tim, ABI...), ghi số thứ tự, tích mục phải làm vào phiếu hướng dẫn, đưa BN đi làm CLS và lấy kết quả về. Kiểm soát kết quả CLS, chuyển cấp cứu các trường hợp bất thường theo HD.25.01.",
         "Điều dưỡng, HDV tại bàn phân phòng - Trả kết quả", None),
    (7,  "Ổn định khu vực BN ngồi chờ khám",
         "HDV hướng dẫn BN ngồi ở sảnh chờ theo số phòng khám của bác sĩ đã đăng ký. Quan sát BN, báo lại điều dưỡng bàn Trả kết quả các thông tin bác sĩ báo lại, các trường hợp hỏng phần mềm/máy gọi số, BN thắc mắc ngoài khả năng giải quyết.",
         "HDV hành lang", None),
    (8,  "Khám bệnh và kê đơn",
         "Bác sĩ gọi lần lượt theo số khám, thực hiện khám và kê đơn trên phần mềm: khai thác dịch tễ, bệnh sử, triệu chứng cơ năng và thực thể; giải thích tình trạng, chỉ định CLS, kê đơn; hướng dẫn sử dụng thuốc, chế độ ăn uống, tập luyện; thông báo lịch khám lại; in phiếu vào viện/chuyển viện nếu cần (theo HD.25.01).",
         "Bác sĩ tại các phòng khám", None),
    (9,  "Hẹn khám lại và đóng dấu chương trình",
         "ĐD kiểm tra đơn thuốc (đủ thuốc, đúng ngày). BN dịch vụ: hướng dẫn tái khám và mua thuốc tại nhà thuốc bệnh viện. BN BHYT: đóng dấu Kiểm soát BHYT; đóng dấu chương trình quản lý bệnh mạn tính hoặc đóng dấu hẹn khám lần 2 + ngày chuyển tuyến tùy hồ sơ ngoại trú.",
         "Điều dưỡng bàn hẹn khám lại", None),
    (10, "Thủ tục hành chính",
         "Nếu BN có chỉ định nhập viện: hướng dẫn và làm thủ tục nhập viện theo quy trình tiếp nhận BN nhập viện điều trị nội trú (QT.25.04). Làm thủ tục chuyển tuyến, cấp giấy nghỉ ốm theo yêu cầu bác sĩ phòng khám và các thủ tục hành chính khác.",
         "Điều dưỡng viên bàn làm thủ tục hành chính", None),
    (11, "Duyệt đơn thuốc BHYT và thu phí chênh lệch",
         "Kế toán thu tiền đồng chi trả theo mức hưởng của thẻ BHYT và số tiền chênh lệch với đơn thuốc BHYT (nếu có). BN mua thuốc dịch vụ thanh toán tiền thuốc cho kế toán tại quầy thuốc dịch vụ. Đóng dấu đã thu tiền vào đơn thuốc.",
         "Kế toán", None),
    (12, "BN lĩnh thuốc / mua thuốc - kết thúc",
         "BN ký tên vào đơn thuốc. Nhân viên quầy thuốc kiểm tra (số lượng tương ứng liều dùng, ngày hẹn khám). Khoa Dược duyệt xuất thuốc BHYT. Phát thuốc theo đơn, đóng dấu đã phát thuốc. BN kết thúc quá trình khám và ra về.",
         "Nhà thuốc dịch vụ, quầy thuốc bảo hiểm", "BM.25.01.01"),
]


def sql_escape(s) -> str:
    if s is None:
        return "NULL"
    s = str(s).strip()
    if s == "":
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


out = [
    "-- =====================================================================",
    "-- V8__seed_procedures.sql",
    "-- MANUALLY CURATED from data/raw/QUY_TRINH_DON_TIEP_BENH_NHAN_KHU_TU_NGUYEN_1_CS1.txt",
    "-- (raw text has 12 numbered steps; docs/06 says 11 - we seed all 12 from source).",
    "-- =====================================================================",
    "",
    "-- procedures (QT.25.01)",
]
for step_no, name, desc, role, form in STEPS:
    out.append(
        "INSERT INTO hospital.procedures "
        "(code, title, step_no, name, description, responsible_role, related_form, source_doc) "
        f"VALUES ('QT.25.01', {sql_escape(TITLE)}, {step_no}, {sql_escape(name)}, "
        f"{sql_escape(desc)}, {sql_escape(role)}, {sql_escape(form)}, "
        f"{sql_escape(SOURCE_DOC)});"
    )

out.append("")
out.append(f"-- stats: procedures=12 (QT.25.01)")

OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"OK -> {OUT}  (12 steps)")
