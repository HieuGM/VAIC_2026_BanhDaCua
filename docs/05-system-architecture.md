# 05 — System Architecture

> **STUB — chưa có nội dung.** Sẽ điền ở phase kiến trúc.
> Cập nhật: 2026-07-17 · Trạng thái: TODO.

## Mục tiêu tài liệu
Mô tả component diagram, data flow, deployment diagram + ADR (Architecture Decision Records).

## Khung cần điền
- [ ] **Component diagram** (Mermaid): Web FE → API Gateway/FastAPI → {RAG service, Guardrail service, LLM adapter, ASR/TTS adapter} → Vector DB (Qdrant) → KB store.
- [ ] **Data flow** (request): chat msg → intent router → emergency check → retrieve → rerank → LLM grounded → citation assemble → response.
- [ ] **KB ingest flow**: crawler → chunker → embedder → Qdrant (+ metadata source/type).
- [ ] **Deployment diagram**: Docker Compose (single node demo) + Caddy TLS; pilot path (on-prem, HA).
- [ ] **ADR**:
  - ADR-001 RAG thuần vs fine-tune → chọn RAG.
  - ADR-002 Cloud LLM (demo) vs on-prem (pilot) → hybrid.
  - ADR-003 Vector DB: Qdrant vs pgvector.
  - ADR-004 Guardrail: rule+LLM classifier, fail-safe emergency.
  - ADR-005 FE framework: Next.js.

## Tham chiếu input
- Stack cao cấp: `01-project-overview` §6 · NFR: `04-non-functional` · Deploy: `09-deployment`.

## Liên quan
- [[07-api-design]] · [[06-database-design]] · [[09-deployment-guide]]
