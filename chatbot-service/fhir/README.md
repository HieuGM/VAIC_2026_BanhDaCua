# Folder `fhir/`

`fhir/` là module truy xuất dữ liệu cá nhân hoặc dữ liệu y tế có cấu trúc qua FHIR/HIS.

FHIR là phần nhạy cảm nhất về quyền riêng tư. Vì vậy module này phải chặt hơn RAG.

## Khi Nào Dùng FHIR

Dùng FHIR cho các câu hỏi như:

- Lịch hẹn cá nhân của tôi.
- Lịch tái khám của tôi.
- Kết quả xét nghiệm đã công bố.
- Đơn thuốc đã được bác sĩ kê.
- Lần khám gần đây.
- Chẩn đoán đã được bác sĩ ghi nhận trong hồ sơ.

Không dùng FHIR cho:

- FAQ bệnh viện.
- Quy trình khám chung.
- BHYT chung.
- Lịch bác sĩ công khai.
- Giá dịch vụ công khai.

## File Chính

- `client.py`: HTTP client gọi FHIR server.
- `tools.py`: tool nghiệp vụ mà graph gọi.
- `tool_registry.py`: allowlist tool FHIR.
- `normalizer.py`: chuẩn hóa raw FHIR thành `Evidence`.
- `access_control.py`: kiểm tra quyền truy cập patient scope.
- `schemas.py`: schema cho tool call hoặc payload FHIR.

## Rule Bảo Mật Bắt Buộc

- Không tin `patient_id` do người dùng nhập.
- Không tin `patient_id` do LLM sinh.
- Patient ID phải đến từ backend identity mapping, token hoặc `allowed_patient_ids`.
- USER chỉ được xem hồ sơ đã liên kết với chính mình.
- Không trả raw FHIR đầy đủ ra answer prompt.
- Không ghi raw medical data vào audit log.

## Contract Với Graph

Graph gọi:

```python
evidence = await retrieve_fhir_evidence(state)
```

Hàm này trả:

```python
list[Evidence]
```

Nếu thiếu quyền, raise `PermissionDenied`. Node `fhir_node.py` sẽ bắt lỗi và trả state an toàn.

## Tool Registry

Mọi tool FHIR phải nằm trong `FHIR_TOOL_ALLOWLIST`.

Ví dụ:

```python
FHIR_TOOL_ALLOWLIST = {
    "get_patient_appointments",
    "get_lab_results",
    "get_medications",
    "get_encounters",
}
```

Không cho LLM tự tạo tên tool mới.

## Normalizer

Normalizer nhận raw FHIR resource và trả `Evidence`.

Nên giữ các trường cần thiết:

- `resource_type`
- `id`
- `status`
- `effective_time`
- `issued`
- `medication`
- `dosage`
- `value`
- `unit`
- `reference_range`

Không nên đẩy toàn bộ raw resource vào prompt.

## Checklist Khi Code FHIR

- Có kiểm tra quyền trước khi gọi tool.
- Tool nằm trong allowlist.
- Patient scope đúng.
- Có timeout khi gọi FHIR server.
- Có fallback khi FHIR lỗi.
- Có test USER không được truy cập patient ngoài scope.
- Có test thiếu `allowed_patient_ids`.
