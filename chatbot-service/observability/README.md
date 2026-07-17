# Folder `observability/`

`observability/` chứa audit log và metrics.

Trong chatbot bệnh viện, quan sát hệ thống không chỉ để debug mà còn để chứng minh hệ thống an toàn: có chặn emergency, có fallback, có kiểm quyền, có audit truy cập dữ liệu cá nhân.

## File Chính

- `audit.py`: ghi audit event tối thiểu.
- `metrics.py`: ghi metric như latency, route count, fallback rate.

## Audit Nên Có

Audit log tối thiểu:

- Thời gian.
- Session ID.
- User ID đã mask hoặc pseudonym nếu có.
- User role.
- Intent.
- Route.
- Tool đã gọi.
- Kết quả kiểm quyền.
- Trạng thái phản hồi.
- Error code nếu có.

Không ghi:

- Raw hồ sơ bệnh án.
- Raw kết quả xét nghiệm.
- Raw đơn thuốc.
- CCCD rõ.
- Access token.

## Metrics Nên Có

- Số request.
- Intent distribution.
- Route distribution.
- Emergency detection count.
- Fallback rate.
- Human handoff rate.
- Tool error rate.
- Cache hit rate.
- p50/p95/p99 latency.

## Checklist

- Audit không làm fail request nếu logging backend lỗi.
- Không log dữ liệu nhạy cảm.
- Có correlation/session id.
- Metrics đủ để demo chất lượng và safety.
