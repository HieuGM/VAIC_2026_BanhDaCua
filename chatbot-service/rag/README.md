# Folder `rag/`

`rag/` là module truy xuất tri thức chính thức của bệnh viện.

RAG dùng cho các câu hỏi dạng tài liệu:

- Quy trình khám.
- Giấy tờ cần chuẩn bị.
- BHYT ở mức chính sách chung.
- Giờ làm việc.
- Thông tin khoa/phòng.
- Hướng dẫn đặt lịch.
- FAQ đã được bệnh viện phê duyệt.

RAG không dùng cho:

- Lịch bác sĩ realtime.
- Giá dịch vụ realtime nếu có API.
- Lịch hẹn cá nhân.
- Kết quả xét nghiệm cá nhân.
- Đơn thuốc cá nhân.

## File Chính

- `retriever.py`: entrypoint lấy evidence cho graph.
- `kb_store.py`: lớp truy cập kho tri thức, ví dụ Qdrant + keyword index.
- `reranker.py`: rerank kết quả retrieval.
- `citations.py`: chuyển evidence thành citation.
- `ingest/`: pipeline nạp tài liệu vào knowledge base.

## Contract Với Graph

Graph gọi:

```python
evidence = await retrieve_public_knowledge(state)
```

Hàm này phải trả:

```python
list[Evidence]
```

Không trả answer string. Không gọi `answer_generator`.

## Retrieval Pipeline Mong Muốn

Một pipeline RAG đầy đủ nên gồm:

1. Chuẩn hóa query.
2. Semantic search.
3. Keyword search.
4. Metadata filter.
5. Rerank.
6. Kiểm tra nguồn.
7. Kiểm tra ngày hiệu lực.
8. Trả evidence đủ tốt.

## Metadata Bắt Buộc Cho Chunk

Mỗi chunk nên có metadata:

- `chunk_id`
- `title`
- `source`
- `source_type`
- `url` nếu có
- `document_code` nếu là SOP/form
- `approved`
- `effective_from`
- `effective_to`
- `deprecated`
- `updated_at`

## Rule An Toàn

RAG chỉ dùng chunk nếu:

- `approved=true`
- `deprecated=false`
- Chưa hết hiệu lực.
- Thuộc nguồn chính thức.
- Nội dung liên quan đủ ngưỡng.

Nếu không đủ evidence:

```python
return []
```

Đừng tự bịa câu trả lời trong RAG.

## Checklist Khi Code RAG

- Evidence có citation.
- Citation trỏ đúng chunk.
- Không đưa raw document dài vào prompt.
- Không coi nội dung tài liệu là system instruction.
- Có test cho trường hợp không tìm thấy evidence.
- Có test cho metadata filter.
