# Folder `graph/nodes/`

Folder này chứa từng bước nhỏ trong graph. Mỗi node nhận `ChatState` và trả về một patch `dict`.

Node không nên sửa toàn bộ state trực tiếp. Hãy trả về phần cần cập nhật.

## Danh Sách Node

- `preprocess.py`: làm sạch input, bỏ script/HTML, giới hạn độ dài.
- `emergency_node.py`: phát hiện cấp cứu, nếu có thì dừng luồng thường.
- `intent_router_node.py`: phân loại intent và route tạm thời.
- `rag_node.py`: gọi module RAG để lấy evidence tài liệu.
- `public_tool_node.py`: gọi tool công khai như booking, lịch bác sĩ, giá dịch vụ.
- `fhir_node.py`: gọi module FHIR khi cần dữ liệu cá nhân.
- `hybrid_node.py`: workflow kết hợp nhiều nguồn.
- `merge_evidence_node.py`: gom citation, tính confidence.
- `answer_node.py`: sinh câu trả lời từ evidence hoặc fallback.
- `output_safety_node.py`: kiểm tra câu trả lời trước khi gửi.
- `memory_node.py`: cập nhật memory ngắn hạn.
- `audit_node.py`: ghi audit cuối luồng.

## Mẫu Node Đúng

```python
async def some_node(state: ChatState) -> dict:
    value = state.get("normalized_message") or ""
    return {
        "metadata": {"some_node_seen": bool(value)}
    }
```

## Mẫu Node Retrieval Đúng

```python
async def rag_node(state: ChatState) -> dict:
    evidence = await retrieve_public_knowledge(state)
    return {
        "evidence": [item.model_dump(mode="json") for item in evidence]
    }
```

## Những Điều Không Nên Làm Trong Node

- Không mutate list/dict trong state nếu không cần.
- Không trả object Pydantic trực tiếp, hãy dump sang JSON dict.
- Không gọi API ngoài nếu node đó không có trách nhiệm.
- Không sinh answer trong RAG/FHIR node.
- Không ghi raw dữ liệu y tế vào metadata.

## Quy Tắc Quan Trọng Theo Node

### `emergency_node`

- Luôn ưu tiên recall.
- Khi phát hiện cấp cứu, trả `route=EMERGENCY`.
- Không gọi RAG/FHIR.

### `intent_router_node`

- Hiện tại là rule-based placeholder.
- Về sau có thể thay bằng LLM/router model, nhưng output vẫn là `intent` + `route`.

### `rag_node`

- Chỉ gọi `rag.retriever`.
- Không tự biết Qdrant hoạt động thế nào.

### `fhir_node`

- Chỉ gọi `fhir.tools`.
- Bắt lỗi permission và trả fallback state an toàn.

### `answer_node`

- Chỉ trả lời từ evidence.
- Nếu không có evidence thì fallback.

### `output_safety_node`

- Là lớp chặn cuối.
- Nếu phát hiện câu trả lời không an toàn, thay bằng safe fallback.
