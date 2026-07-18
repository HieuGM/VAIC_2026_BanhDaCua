"""Rerank retrieved Evidence with a local cross-encoder (bge-reranker-v2-m3).

Chosen over LLM listwise reranking on measured evidence (rag/eval/measure_rerank.py):
the cross-encoder dominates price/schedule queries (exact service/doctor matching)
and wins overall, while running offline in ~50-100ms with no API dependency.

Contract: rerank_evidence(items, query) -> list[Evidence] re-scored (confidence =
cross-encoder relevance in [0,1]) and sorted desc. Empty/disabled → items unchanged.
Never raises into the graph (any error → original order, graceful degrade).
"""

import asyncio
import logging
import threading

from core.contracts import Evidence
from rag.config import RagSettings, get_settings

_log = logging.getLogger(__name__)


class CrossEncoderReranker:
    def __init__(self, settings: RagSettings):
        from sentence_transformers import CrossEncoder
        import torch

        if settings.rerank_device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = settings.rerank_device
        model_kwargs = {"dtype": torch.float16} if device == "cuda" else {}
        self._ce = CrossEncoder(
            settings.rerank_ce_model, device=device,
            max_length=settings.rerank_max_length, model_kwargs=model_kwargs,
        )
        self._batch = settings.rerank_batch_size
        _log.info("Loaded reranker %s on %s", settings.rerank_ce_model, device)

    def score(self, query: str, docs: list[str]) -> list[float]:
        """Relevance in [0,1]. CrossEncoder.predict already applies the model's
        default activation (Sigmoid for bge-reranker) — do NOT sigmoid again,
        that double-squashes scores into [0.5, 0.73] and kills the separation."""
        scores = self._ce.predict([(query, d) for d in docs], batch_size=self._batch)
        return [float(s) for s in scores]


_RERANKER: CrossEncoderReranker | None = None
_RERANKER_LOCK = threading.Lock()


def get_reranker(settings: RagSettings | None = None) -> CrossEncoderReranker:
    """Thread-safe process-wide singleton (loads the model once)."""
    global _RERANKER
    if _RERANKER is None:
        with _RERANKER_LOCK:
            if _RERANKER is None:
                _RERANKER = CrossEncoderReranker(settings or get_settings())
    return _RERANKER


def reset_reranker() -> None:
    """Drop the cached reranker (test isolation)."""
    global _RERANKER
    _RERANKER = None


async def rerank_evidence(items: list[Evidence], query: str) -> list[Evidence]:
    settings = get_settings()
    if not items or not settings.rerank_enabled or settings.rerank_provider == "none":
        return items
    try:
        docs = [(e.content or e.title or "") for e in items]
        scores = await asyncio.to_thread(get_reranker(settings).score, query, docs)
        for evidence, score in zip(items, scores):
            evidence.confidence = max(0.0, min(1.0, float(score)))
        items.sort(key=lambda e: e.confidence, reverse=True)
        return items
    except Exception:  # graceful degrade: keep retrieval order/scores
        _log.exception("rerank failed; keeping retrieval order")
        return items
