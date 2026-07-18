"""Knowledge base store: embedded Qdrant with named dense + sparse vectors.

IMPORTANT — single-process lock: QdrantClient(path=...) locks the storage
directory. The ingest CLI (rag.ingest.run_ingest) and the API server must
NOT open the same path at the same time. Run ingest offline, then start
the server.

Chunk payload schema (written by rag/ingest/chunker.py in phase 2):
    {
      "chunk_id": str,          # stable id, e.g. "<source>:<section>:<n>"
      "title": str,
      "source": str,            # source file name
      "source_type": str,       # document | price_table | schedule
      "content": str,           # text sent to the LLM as evidence
      "snippet": str,           # short excerpt for the citation
      "approved": bool,
      "deprecated": bool,
      "effective_from": str | None,   # ISO "YYYY-MM-DD"
      "effective_to": str | None,
      "eff_from_int": int | None,     # YYYYMMDD for Qdrant range filters
      "eff_to_int": int | None,
      "updated_at": str | None,
      "document_code": str | None,
      "url": str | None,
      "category": str | None,   # e.g. price list section name
    }

Note: Evidence.source_type is always SourceType.RAG; the payload
"source_type" above is the chunk classification, a separate concept.
"""

import threading

from qdrant_client import QdrantClient, models

from rag.config import RagSettings, get_settings

# Named vectors used by the collection; retriever/embedder must use the same names.
DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


class KnowledgeBaseStore:
    def __init__(self, settings: RagSettings | None = None):
        self.settings = settings or get_settings()
        self._client: QdrantClient | None = None

    @property
    def client(self) -> QdrantClient:
        # Lazy init so importing this module never touches the filesystem.
        if self._client is None:
            self._client = QdrantClient(path=self.settings.qdrant_path)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def ensure_collection(self, recreate: bool = False) -> None:
        """Create the collection if missing; recreate=True drops existing data.

        Windows local-mode quirk (qdrant-client 1.18): delete_collection can leave
        the locked storage.sqlite behind, and re-creating the same name silently
        reloads the old points. So on recreate we clear points explicitly when the
        schema is unchanged, and verify emptiness when we must rebuild the schema.
        """
        exists = self.client.collection_exists(self.settings.collection)
        if exists and not recreate:
            return
        if exists:
            info = self.client.get_collection(self.settings.collection)
            current_dim = info.config.params.vectors[DENSE_VECTOR_NAME].size
            if current_dim == self.settings.embed_dim:
                # Same schema: clearing points is reliable on all platforms.
                self.client.delete(
                    collection_name=self.settings.collection,
                    points_selector=models.FilterSelector(filter=models.Filter()),
                )
                return
            self.client.delete_collection(self.settings.collection)
        self.client.create_collection(
            collection_name=self.settings.collection,
            vectors_config={
                DENSE_VECTOR_NAME: models.VectorParams(
                    size=self.settings.embed_dim,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                # IDF modifier lets Qdrant score BM25-style sparse vectors properly.
                SPARSE_VECTOR_NAME: models.SparseVectorParams(
                    modifier=models.Modifier.IDF
                )
            },
        )
        # Defensive check for the reload-old-points quirk described above.
        count = self.client.count(self.settings.collection).count
        if count != 0:
            raise RuntimeError(
                f"Collection '{self.settings.collection}' not empty after recreate "
                f"({count} stale points). Delete '{self.settings.qdrant_path}' and re-ingest."
            )

    def upsert(self, points: list[models.PointStruct]) -> None:
        self.client.upsert(collection_name=self.settings.collection, points=points)

    def dense_search(
        self,
        dense_vector: list[float],
        *,
        limit: int,
        query_filter: models.Filter | None = None,
    ) -> list[models.ScoredPoint]:
        """Dense-only search — returns calibrated COSINE scores (unlike RRF).
        Used for the relevance gate and per-evidence confidence."""
        if not self.client.collection_exists(self.settings.collection):
            return []
        return self.client.query_points(
            collection_name=self.settings.collection,
            query=dense_vector,
            using=DENSE_VECTOR_NAME,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        ).points

    def hybrid_search(
        self,
        dense_vector: list[float],
        sparse_vector: dict,
        *,
        limit: int,
        query_filter: models.Filter | None = None,
    ) -> list[models.ScoredPoint]:
        """Dense + sparse prefetch fused with RRF. Returns raw scored points;
        mapping to Evidence happens in retriever.py.

        sparse_vector: {"indices": [...], "values": [...]}
        """
        if not self.client.collection_exists(self.settings.collection):
            return []
        result = self.client.query_points(
            collection_name=self.settings.collection,
            prefetch=[
                models.Prefetch(
                    query=dense_vector,
                    using=DENSE_VECTOR_NAME,
                    limit=self.settings.prefetch_limit,
                    filter=query_filter,
                ),
                models.Prefetch(
                    query=models.SparseVector(**sparse_vector),
                    using=SPARSE_VECTOR_NAME,
                    limit=self.settings.prefetch_limit,
                    filter=query_filter,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            with_payload=True,
        )
        return result.points


_STORE: KnowledgeBaseStore | None = None
_STORE_LOCK = threading.Lock()


def get_store(settings: RagSettings | None = None) -> KnowledgeBaseStore:
    """Process-wide singleton for the serving side (holds the Qdrant lock once).

    Thread-safe: retriever calls this from asyncio.to_thread workers, so two
    concurrent first requests must not each open QdrantClient on the same path
    (the second would fail the single-process lock). The ingest CLI creates its
    own KnowledgeBaseStore instead — it must run offline, not while the server
    holds this singleton's lock.

    Note: the underlying local (sqlite) client is shared across worker threads;
    for the single-process demo/MVP concurrent reads are acceptable.
    """
    global _STORE
    if _STORE is None:
        with _STORE_LOCK:
            if _STORE is None:
                _STORE = KnowledgeBaseStore(settings)
    return _STORE


def reset_store() -> None:
    """Drop the cached store (test isolation)."""
    global _STORE
    if _STORE is not None:
        _STORE.close()
    _STORE = None
