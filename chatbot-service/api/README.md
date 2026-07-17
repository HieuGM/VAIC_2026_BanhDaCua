# Folder `api/`

Folder này định nghĩa HTTP API để frontend hoặc backend khác gọi vào chatbot.

Nói đơn giản: `api/` là lớp ngoài cùng. Nó nhận request, chuyển thành `ChatState`, gọi graph, rồi trả response.

## File Chính

- `chat_routes.py`: endpoint `/api/v1/chat`.
- `chat_schemas.py`: schema request/response bằng Pydantic.
- `health_routes.py`: endpoint `/health`.
- `__init__.py`: đánh dấu package.

## Contract API Hiện Tại

Endpoint:

```text
POST /api/v1/chat
```

Request mẫu:

```json
{
  "sessionId": "demo-session",
  "text": "Tôi muốn đặt lịch khám",
  "lang": "vi",
  "userId": "user-1",
  "userRole": "ANONYMOUS",
  "allowedPatientIds": [],
  "context": {}
}
```

Response mẫu:

```json
{
  "answer": "...",
  "citations": [],
  "confidence": 0.8,
  "guardrailFlags": [],
  "intent": "APPOINTMENT_BOOKING",
  "route": "PUBLIC_TOOL",
  "redirection": null,
  "needsHandoff": false,
  "metadata": {}
}
```

## Vai Trò Của API Layer

API layer được phép:

- Validate input cơ bản.
- Map request thành graph state.
- Gọi graph.
- Map graph result thành response.

API layer không được:

- Tự retrieve RAG.
- Tự gọi FHIR.
- Tự sinh câu trả lời bằng LLM.
- Bỏ qua safety node.

## Khi Thêm Endpoint

Ví dụ sau này cần feedback:

```text
POST /api/v1/feedback
```

Hãy tạo file riêng nếu endpoint đủ lớn, ví dụ `feedback_routes.py`, rồi include router trong `app/main.py`.

## Checklist Khi Sửa API

- Schema request/response rõ ràng.
- Tên field dùng camelCase nếu trả cho frontend.
- Bên trong Python có thể dùng snake_case.
- Không trả raw exception cho người dùng.
- Không log raw dữ liệu y tế cá nhân.
