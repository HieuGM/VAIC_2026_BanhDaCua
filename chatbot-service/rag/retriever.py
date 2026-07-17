"""Public-knowledge retrieval entrypoint for the graph.

Pipeline (design backed by rag/eval/measure_retrieval.py on the real corpus):
  normalize query
  -> dense-only search  : calibrated cosine → relevance gate + confidence
  -> if top cosine < dense_min_score: return []  (safe fallback, no weak evidence)
  -> hybrid search (dense+BM25 RRF, filtered): recall into the candidate set
  -> map hits to Evidence (source_type ALWAYS RAG; chunk type lives in Citation)
  -> rerank (phase 5; passthrough today) → threshold → top_k

Never returns answer strings, never raises into the graph (any error → []).
"""

import asyncio
import logging
import threading
from datetime import date

from fastembed import SparseTextEmbedding
from qdrant_client import models

from core.contracts import Citation, Evidence
from core.enums import SourceType
from core.state import ChatState
from rag.config import RagSettings, get_settings
from rag.embedding import get_embedder
from rag.kb_store import get_store
from rag.reranker import rerank_evidence

_log = logging.getLogger(__name__)
_bm25: SparseTextEmbedding | None = None
_bm25_lock = threading.Lock()


def _sparse_query(settings: RagSettings, text: str) -> dict:
    # Thread-safe lazy init: _search runs in asyncio.to_thread worker threads,
    # so concurrent first requests could otherwise double-load the model.
    global _bm25
    if _bm25 is None:
        with _bm25_lock:
            if _bm25 is None:
                _bm25 = SparseTextEmbedding(model_name=settings.sparse_model)
    sp = next(_bm25.query_embed(text))
    return {"indices": sp.indices.tolist(), "values": sp.values.tolist()}


def warmup() -> None:
    """Prime singletons (store, embedder, BM25) before serving traffic — removes
    first-request latency spikes and the cold-start init race. Call at startup."""
    get_store(get_settings())
    get_embedder(get_settings())
    _sparse_query(get_settings(), "warmup")


def _today_int() -> int:
    return int(date.today().strftime("%Y%m%d"))


def build_filter(today_int: int) -> models.Filter:
    """approved & not deprecated & currently in effect.

    Effective dates use must_not ranges so chunks WITHOUT dates (documents) are
    kept — a Range only matches points that have the field, so a missing
    eff_to_int never matches the must_not and thus survives.
    """
    return models.Filter(
        must=[
            models.FieldCondition(key="approved", match=models.MatchValue(value=True)),
            models.FieldCondition(key="deprecated", match=models.MatchValue(value=False)),
        ],
        must_not=[
            models.FieldCondition(key="eff_to_int", range=models.Range(lt=today_int)),
            models.FieldCondition(key="eff_from_int", range=models.Range(gt=today_int)),
        ],
    )


def _hit_to_evidence(hit: models.ScoredPoint, confidence: float) -> Evidence:
    p = hit.payload
    return Evidence(
        source_type=SourceType.RAG,  # always RAG; chunk type is payload-only
        title=p["title"],
        content=p["content"],
        citation=Citation(
            source=p["source"],
            title=p["title"],
            chunk_id=p["chunk_id"],
            url=p.get("url"),
            snippet=p.get("snippet"),
            updated_at=p.get("updated_at"),
        ),
        # Cosine is [-1, 1] but Evidence.confidence is [0, 1]; clamp so a
        # low-ranked negative-cosine hit can't raise ValidationError and sink
        # the whole batch to [].
        confidence=max(0.0, min(1.0, confidence)),
        updated_at=p.get("updated_at"),
    )


def _search(query: str, settings: RagSettings) -> list[Evidence]:
    """Sync Qdrant work (run in a thread by the async entrypoint)."""
    store = get_store(settings)
    dense_vec = get_embedder(settings).embed_query(query)
    query_filter = build_filter(_today_int())

    dense_hits = store.dense_search(
        dense_vec, limit=settings.prefetch_limit, query_filter=query_filter
    )
    if not dense_hits or dense_hits[0].score < settings.dense_min_score:
        return []  # nothing relevant enough → safe fallback

    cosine = {h.payload["chunk_id"]: h.score for h in dense_hits}
    sparse_vec = _sparse_query(settings, query)
    hybrid_hits = store.hybrid_search(
        dense_vec, sparse_vec, limit=settings.prefetch_limit, query_filter=query_filter
    )
    # Confidence = calibrated dense cosine; sparse-only hits get the gate floor.
    return [
        _hit_to_evidence(h, cosine.get(h.payload["chunk_id"], settings.dense_min_score))
        for h in hybrid_hits
    ]


async def retrieve_public_knowledge(state: ChatState) -> list[Evidence]:
    try:
        query = (state.get("normalized_message") or state.get("message") or "").strip()
        if not query:
            return []
        settings = get_settings()
        candidates = await asyncio.to_thread(_search, query, settings)
        if not candidates:
            return []
        ranked = await rerank_evidence(candidates, query)
        ranked.sort(key=lambda e: e.confidence, reverse=True)
        return [e for e in ranked if e.confidence >= settings.rerank_min_score][
            : settings.rerank_top_k
        ]
    except Exception:  # never propagate into the graph
        _log.exception("retrieve_public_knowledge failed; returning no evidence")
        return []
