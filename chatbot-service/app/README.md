# Folder `app/`

Folder này chứa phần khởi tạo ứng dụng FastAPI và cấu hình runtime.

Người mới chỉ cần hiểu: `app/` là nơi service bắt đầu chạy.

## File Chính

- `main.py`: tạo FastAPI app, đăng ký router.
- `config.py`: đọc biến môi trường và cấu hình mặc định.
- `logger.py`: cấu hình logging.
- `__init__.py`: đánh dấu folder là Python package.

## Luồng Khởi Động

Khi chạy:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Python sẽ mở `app/main.py`, tạo object `app`, sau đó include các router:

- Health route.
- Chat route.

## Khi Nào Sửa Folder Này

Sửa `app/config.py` khi cần thêm cấu hình mới, ví dụ:

- URL FHIR server.
- URL Qdrant.
- Model name.
- Timeout.
- Hotline.
- Link đặt lịch.

Sửa `app/main.py` khi cần thêm router mới, ví dụ:

- `/api/v1/eval`
- `/api/v1/admin`
- `/api/v1/feedback`

## Không Nên Làm

- Không viết logic RAG trong `app/`.
- Không viết logic FHIR trong `app/`.
- Không gọi LLM trực tiếp trong `app/`.
- Không hard-code secret hoặc API key.

## Checklist Khi Thêm Config

- Thêm field vào `Settings`.
- Có default an toàn.
- Biến môi trường có tên rõ ràng.
- Không commit `.env` thật.
