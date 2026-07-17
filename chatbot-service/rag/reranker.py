from core.contracts import Evidence


async def rerank_evidence(items: list[Evidence], query: str) -> list[Evidence]:
    # TODO(RAG owner): implement reranking.
    return items
