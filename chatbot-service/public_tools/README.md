# Folder `public_tools/`

`public_tools/` chứa các tool công khai không cần đăng nhập.

Dùng cho dữ liệu có cấu trúc nhưng không phải dữ liệu cá nhân.

## Ví Dụ Public Tool

- Kênh đặt lịch chính thức.
- Lịch bác sĩ công khai.
- Giá dịch vụ công khai.
- Slot khám còn trống nếu bệnh viện có API public.
- Trạng thái hoạt động của dịch vụ.

## File Chính

- `booking_channels.py`: link website, Zalo, hotline, kênh đặt lịch.
- `doctor_schedule.py`: lịch bác sĩ công khai.
- `service_price.py`: giá dịch vụ công khai.

## Contract Với Graph

Public tool node trả patch:

```python
return {
    "evidence": [...],
    "redirection": {...}
}
```

Evidence vẫn phải theo `core/contracts.py`.

## Khi Nào Không Dùng Public Tool

Không dùng public tool cho:

- Lịch hẹn cá nhân.
- Kết quả xét nghiệm cá nhân.
- Đơn thuốc.
- Hồ sơ bệnh án.

Các dữ liệu đó thuộc FHIR/HIS và cần xác thực.

## Checklist Khi Code Public Tool

- Tool không yêu cầu dữ liệu nhạy cảm nếu user chưa đăng nhập.
- Tham số ngày tháng hợp lệ.
- Có timeout nếu gọi API ngoài.
- Có timestamp hoặc `updated_at` nếu dữ liệu có thể thay đổi.
- Nếu API lỗi, trả fallback, không bịa.
