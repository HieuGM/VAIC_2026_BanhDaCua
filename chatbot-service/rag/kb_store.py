from core.contracts import Evidence


class KnowledgeBaseStore:
    async def search(self, query: str, *, limit: int = 8) -> list[Evidence]:
        # TODO(RAG owner): connect Qdrant/keyword index.
        return []
