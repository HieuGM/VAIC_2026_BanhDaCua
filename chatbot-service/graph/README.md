# Folder `graph/`

`graph/` là nơi điều phối toàn bộ workflow chatbot bằng LangGraph.

Nếu RAG là người tìm tài liệu và FHIR là người lấy dữ liệu cá nhân, thì graph là người quản lý luồng: câu hỏi này đi đâu, node nào chạy trước, khi nào fallback, khi nào dừng.

## File Chính

- `builder.py`: tạo `StateGraph`, đăng ký node và nối edge.
- `edges.py`: hàm quyết định route sau một số node.
- `nodes/`: từng bước xử lý cụ thể.

## Luồng Hiện Tại

```text
preprocess
  -> emergency
  -> intent_router
  -> rag/public_tool/fhir/hybrid
  -> merge_evidence
  -> answer
  -> output_safety
  -> memory
  -> audit
```

## Vai Trò Của Graph

Graph được phép:

- Chọn node tiếp theo dựa trên `route`.
- Đảm bảo emergency chạy trước mọi luồng khác.
- Gọi RAG/FHIR/public tool thông qua node wrapper.
- Gom evidence và citation.
- Chạy safety output trước khi trả lời.
- Gọi audit cuối luồng.

Graph không được:

- Tự viết logic truy vấn Qdrant.
- Tự viết logic gọi FHIR server.
- Tự tạo prompt dài trong builder.
- Bỏ qua permission check.
- Chạy planner động cho mọi câu hỏi đơn giản.

## Các Route Chính

Các route nằm trong `core/enums.py`:

- `EMERGENCY`: tình huống cấp cứu, dừng luồng thường.
- `PUBLIC_RAG`: hỏi tài liệu chính thức.
- `PUBLIC_TOOL`: lịch bác sĩ, giá dịch vụ, kênh đặt lịch.
- `AUTHENTICATED_FHIR`: dữ liệu cá nhân cần xác thực.
- `FIXED_HYBRID`: kết hợp RAG và API theo workflow cố định.
- `HUMAN_HANDOFF`: chuyển người thật.
- `UNSUPPORTED`: ngoài phạm vi.

## Khi Thêm Node Mới

Ví dụ muốn thêm `feedback_node`:

1. Tạo file trong `graph/nodes/feedback_node.py`.
2. Import node trong `builder.py`.
3. `graph.add_node("feedback", feedback_node)`.
4. Nối edge phù hợp.
5. Nếu cần route mới, sửa `core/enums.py`.
6. Thêm test route.

## Checklist Khi Sửa Graph

- Emergency vẫn là node đầu tiên sau preprocess.
- Route không bị vòng lặp vô hạn.
- Node retrieval vẫn đi qua `merge_evidence`.
- `answer_node` luôn đi qua `output_safety_node`.
- `audit_node` vẫn chạy cuối.
