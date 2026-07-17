# Folder `memory/`

`memory/` quản lý ngữ cảnh ngắn hạn của hội thoại.

Memory giúp chatbot hiểu các câu tiếp nối như:

- "Bác sĩ đó có khám thứ Hai không?"
- "Dịch vụ này giá bao nhiêu?"
- "Tôi cần mang giấy tờ gì cho lịch đó?"

## File Chính

- `session_memory.py`: cập nhật hoặc đọc memory theo session.

## Được Phép Lưu

- Intent gần nhất.
- Route gần nhất.
- Bác sĩ đang được hỏi.
- Khoa/phòng đang được hỏi.
- Dịch vụ đang được hỏi.
- Cơ sở đang được hỏi.
- Resource reference dạng compact, nếu thật sự cần.

## Không Được Lưu

- Toàn bộ hồ sơ bệnh án.
- Toàn bộ kết quả xét nghiệm.
- Đơn thuốc đầy đủ.
- Access token.
- Mật khẩu.
- CCCD dạng rõ.
- Raw FHIR.

## Contract Với Graph

`memory_node` gọi module này sau khi answer đã qua safety check.

Memory không được thay đổi câu trả lời đã sinh, chỉ cập nhật context cho lượt sau.

## Checklist

- Memory có TTL hoặc cơ chế xóa session.
- Chỉ lưu dữ liệu tối thiểu.
- Không lưu PII không cần thiết.
- Có thể xóa lịch sử theo yêu cầu người dùng.
