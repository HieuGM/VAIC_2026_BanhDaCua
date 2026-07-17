# Folder `core/`

`core/` là phần quan trọng nhất để nhiều người cùng code không bị lệch nhau.

Folder này chứa các contract, enum, state và lỗi dùng chung toàn service. Nếu ví toàn bộ chatbot là một hệ thống đường ống, thì `core/` định nghĩa kích thước và hình dạng của các đoạn ống.

## File Chính

- `contracts.py`: định nghĩa `Evidence`, `Citation`, `RouteDecision`, `ToolResult`.
- `enums.py`: định nghĩa `Route`, `Intent`, `SafetyFlag`, `SourceType`.
- `state.py`: định nghĩa `ChatState`, tức state đi qua LangGraph.
- `errors.py`: exception chung.
- `text.py`: hàm xử lý text cơ bản như strip HTML, bỏ script, chuẩn hóa khoảng trắng.

## Vì Sao `core/` Quan Trọng

RAG, FHIR, public tool và answer generator đều phải hiểu cùng một kiểu dữ liệu.

Nếu RAG trả kiểu riêng, FHIR trả kiểu riêng, graph sẽ phải viết logic đặc biệt cho từng nhánh. Điều đó làm dự án khó tích hợp. Vì vậy mọi nhánh đều phải trả `Evidence`.

## Contract `Evidence`

`Evidence` là một mẩu bằng chứng để chatbot dựa vào khi trả lời.

Các field chính:

- `source_type`: `rag`, `fhir`, hoặc `public_api`.
- `title`: tên nguồn hoặc tên resource.
- `content`: text evidence nếu là tài liệu.
- `data`: dữ liệu có cấu trúc nếu là FHIR/API.
- `citation`: nguồn trích dẫn nếu có.
- `confidence`: độ tin cậy.
- `updated_at`: thời gian cập nhật nếu có.

Ví dụ RAG evidence:

```python
Evidence(
    source_type=SourceType.RAG,
    title="Quy trình khám ngoại trú",
    content="Người bệnh lấy số tiếp nhận tại quầy...",
    citation=Citation(
        source="SOP QT.25.01",
        title="Quy trình đón tiếp và khám ngoại trú",
        chunk_id="qt-25-01-step-2",
    ),
    confidence=0.87,
)
```

Ví dụ FHIR evidence:

```python
Evidence(
    source_type=SourceType.FHIR,
    title="MedicationRequest/abc",
    data={
        "resource_type": "MedicationRequest",
        "id": "abc",
        "medication": "Aspirin",
        "authored_on": "2026-07-01",
    },
    confidence=1.0,
)
```

## Contract `ChatState`

`ChatState` là dữ liệu của một lượt chat trong graph.

Các field thường gặp:

- `message`: câu gốc.
- `normalized_message`: câu đã làm sạch.
- `intent`: intent đã phân loại.
- `route`: route graph sẽ đi.
- `evidence`: danh sách bằng chứng.
- `citations`: danh sách nguồn.
- `answer`: câu trả lời cuối.
- `safety_flags`: các flag an toàn.
- `needs_handoff`: có cần chuyển người thật không.

Mỗi node không cần trả toàn bộ state. Node chỉ trả patch:

```python
return {
    "intent": "BHYT_INFORMATION",
    "route": "PUBLIC_RAG",
}
```

## Quy Tắc Khi Sửa `core/`

Chỉ sửa `core/` khi thật sự cần.

Trước khi sửa:

- Hỏi người đang làm RAG/FHIR có bị ảnh hưởng không.
- Cập nhật README liên quan.
- Cập nhật test contract.

Không nên:

- Thêm field tùy tiện vào `Evidence` nếu có thể dùng `data`.
- Đổi tên enum đã có mà không sửa graph/tests.
- Đưa business logic vào `core/`.

## Checklist

- Contract có type rõ ràng.
- Enum có tên nghiệp vụ dễ hiểu.
- Không phụ thuộc vào FastAPI, Qdrant, FHIR client hay OpenAI.
- Test serialize/deserialize vẫn pass.
