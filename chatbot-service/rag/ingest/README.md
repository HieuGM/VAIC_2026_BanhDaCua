# Folder `rag/ingest/`

Folder này chứa pipeline nạp tài liệu vào knowledge base.

Nói đơn giản: ingest biến tài liệu gốc như PDF, Markdown, HTML thành các chunk nhỏ có metadata và embedding để RAG tìm kiếm được.

## File Chính

- `loader.py`: đọc tài liệu từ thư mục, PDF, Markdown hoặc HTML.
- `chunker.py`: chia tài liệu thành chunk vừa đủ nhỏ để retrieval.
- `embedder.py`: tạo embedding và ghi vào vector store.

## Pipeline Mong Muốn

```text
raw document
  -> loader
  -> normalized document
  -> chunker
  -> chunks with metadata
  -> embedder
  -> vector store / keyword index
```

## Yêu Cầu Với Loader

Loader cần giữ metadata nguồn:

- Tên tài liệu.
- Đường dẫn file.
- Loại tài liệu.
- Ngày cập nhật nếu biết.
- Mã quy trình/form nếu có.
- Trạng thái phê duyệt nếu có.

## Yêu Cầu Với Chunker

Chunk phải:

- Không quá dài.
- Không mất tiêu đề cha.
- Có `chunk_id` ổn định.
- Có snippet dễ hiển thị citation.
- Không cắt nát bảng quan trọng nếu có thể tránh.

## Yêu Cầu Với Embedder

Embedder phải:

- Dùng model embedding thống nhất.
- Ghi vector kèm metadata.
- Không ghi chunk chưa được duyệt vào production collection.
- Có thể chạy lại ingest mà không tạo bản ghi trùng vô hạn.

## Checklist

- Chạy ingest trên một tài liệu nhỏ trước.
- Kiểm tra chunk có tiếng Việt đúng encoding.
- Kiểm tra citation hiển thị đúng.
- Kiểm tra query mẫu tìm được đúng chunk.
