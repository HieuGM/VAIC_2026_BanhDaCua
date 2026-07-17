# Folder `llm/`

`llm/` chứa logic liên quan tới model, prompt và sinh câu trả lời.

LLM không được tự quyết định quyền truy cập, không được tự gọi tool ngoài allowlist và không được bịa dữ liệu khi thiếu evidence.

## File Chính

- `answer_generator.py`: sinh câu trả lời từ evidence.
- `model_router.py`: chọn model đơn giản/phức tạp theo route.
- `prompts.py`: prompt dùng chung.

## Nguyên Tắc Sinh Câu Trả Lời

Answer generator chỉ được dùng:

- `message`
- `intent`
- `route`
- `evidence`
- `citations`
- context an toàn

Không được dùng:

- Kiến thức nội tại để thay thế evidence bệnh viện.
- Raw FHIR đầy đủ nếu không cần.
- Dữ liệu cá nhân ngoài scope.

## Khi Không Có Evidence

Phải fallback:

```text
Mình chưa có đủ thông tin chính thức để trả lời câu này...
```

Không được trả lời kiểu chắc chắn nếu không có nguồn.

## Template Và LLM

Nên dùng template cho dữ liệu đơn giản:

- Giờ làm việc.
- Hotline.
- Link đặt lịch.
- Giá dịch vụ có cấu trúc.
- Lịch bác sĩ có cấu trúc.

Dùng LLM khi cần:

- Tóm tắt nhiều evidence.
- Diễn đạt tự nhiên.
- Kết hợp RAG và API.
- Trả lời câu hỏi nhiều ý.

## Checklist Khi Sửa Prompt

- Nhắc model chỉ dùng evidence.
- Nhắc không chẩn đoán, không kê đơn.
- Không đưa document RAG vào vai trò system instruction.
- Có fallback khi LLM lỗi.
- Có test output không chứa lời khuyên điều trị.
