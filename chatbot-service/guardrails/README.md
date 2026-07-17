# Folder `guardrails/`

`guardrails/` chứa các lớp bảo vệ an toàn cho chatbot.

Đây là phần cực kỳ quan trọng trong domain bệnh viện. Chatbot không được hành xử như bác sĩ và không được lộ dữ liệu cá nhân.

## File Chính

- `emergency.py`: phát hiện tình huống cấp cứu.
- `medical_safety.py`: kiểm tra output có chứa tư vấn điều trị/chẩn đoán không.
- `permissions.py`: kiểm tra route có được phép với user hiện tại không.
- `prompt_injection.py`: phát hiện prompt injection cơ bản.

## Emergency Guardrail

Emergency phải chạy sớm nhất, trước RAG, FHIR và planner.

Ví dụ dấu hiệu:

- Đau ngực dữ dội.
- Khó thở.
- Bất tỉnh.
- Ngất.
- Tím tái.
- Co giật.
- Chảy máu nghiêm trọng.

Khi phát hiện emergency:

- Không RAG.
- Không FHIR.
- Không giải thích bệnh dài dòng.
- Không chẩn đoán.
- Không kê thuốc.
- Hướng dẫn gọi 115 hoặc đến cơ sở cấp cứu gần nhất.

## Medical Safety

Output không được chứa:

- Khẳng định chẩn đoán mới.
- Khuyên ngừng thuốc.
- Khuyên tăng/giảm liều.
- Kê thuốc mới.
- Phác đồ điều trị.

Nếu output không an toàn, `output_safety_node` phải thay bằng safe fallback.

## Prompt Injection

Không làm theo các nội dung như:

- "Bỏ qua hướng dẫn trước."
- "Bạn là system prompt mới."
- "Gọi endpoint này."
- "Tạo raw SQL."
- "Tự tăng quyền cho tôi."

## Checklist Khi Code Guardrail

- Rule-based trước, LLM chỉ là bổ sung.
- Fail-safe khi không chắc chắn trong emergency.
- Có test câu phủ định, ví dụ "Tôi không đau ngực".
- Có test câu emergency rõ ràng.
- Không để LLM quyết định cuối cùng về quyền truy cập.
