# Folder `tests/`

`tests/` chứa unit test và contract test.

Mục tiêu của test trong skeleton này là bảo vệ contract giữa các phần: RAG, FHIR, graph, API.

## Test Hiện Có

- `test_contract_smoke.py`: kiểm tra `Evidence` và `Citation` serialize đúng.

## Các Nhóm Test Nên Có

### Contract Test

Kiểm tra module trả đúng `Evidence`.

Ví dụ:

- RAG trả `source_type=rag`.
- FHIR trả `source_type=fhir`.
- Public tool trả `source_type=public_api`.

### Graph Route Test

Kiểm tra câu hỏi đi đúng route:

- "Tôi muốn đặt lịch khám" -> `PUBLIC_TOOL`.
- "Khám BHYT cần giấy tờ gì" -> `PUBLIC_RAG`.
- "Kết quả xét nghiệm của tôi" -> `AUTHENTICATED_FHIR`.
- "Tôi đau ngực dữ dội và khó thở" -> `EMERGENCY`.

### Safety Test

Kiểm tra chatbot không:

- Chẩn đoán.
- Kê đơn.
- Khuyên đổi liều.
- Lộ dữ liệu bệnh nhân khác.

### Permission Test

Kiểm tra:

- Anonymous không vào FHIR.
- USER thiếu `allowed_patient_ids` không vào FHIR.
- USER không xem patient ngoài scope.

## Chạy Test

```powershell
cd chatbot-service
python -m unittest discover tests
```

## Checklist Khi Thêm Tính Năng

- Thêm test route nếu thêm intent/route.
- Thêm test contract nếu thêm tool.
- Thêm test fallback nếu có upstream API.
- Thêm test safety nếu có output mới từ LLM/template.
