# 06 — Database Design

> **STUB — chưa có nội dung.**
> Cập nhật: 2026-07-17 · Trạng thái: TODO.

## Khung cần điền
- [ ] **ERD** (Mermaid): entities từ `02-business-analysis` §3 (PatientQuery, KnowledgeChunk, RetrievalResult, Answer, GuardrailEvent, Redirection, Intent, Session).
- [ ] **Vector store schema** (Qdrant collection): point id, vector, payload {source, sourceType, title, text, chunkIndex, url, formCode}.
- [ ] **Metadata/relational** (Postgres nếu cần): sessions, eval_runs, feedback. Hoặc SQLite cho demo.
- [ ] **Index strategy**: HNSW (Qdrant), filter payload theo sourceType.
- [ ] **Migration**: seed KB + eval set script (không cần Flyway cho demo).

## Ghi chú
- Đa số state là vector + ephemeral session. Relational tối thiểu.
- PII KHÔNG lưu (R5).

## Liên quan
- [[02-business-analysis]] · [[05-system-architecture]]
