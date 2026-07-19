"""Rerank retrieved Evidence with bge-reranker-v2-m3.

Chosen over LLM listwise reranking on measured evidence (rag/eval/measure_rerank.py):
this cross-encoder dominates price/schedule queries and wins overall.

Two providers (RAG_RERANK_PROVIDER), same model, same [0,1] sigmoid scores:
- cross_encoder: local sentence-transformers CrossEncoder (GPU, offline, ~2.2GB RAM).
- fptcloud: FPT Cloud /v1/rerank hosted API (~0 local RAM — for low-RAM deploy).

Contract: rerank_evidence(items, query) -> list[Evidence] re-scored (confidence =
relevance in [0,1]) and sorted desc. Empty/disabled → items unchanged.
Never raises into the graph (any error → original order, graceful degrade).
"""

import asyncio
import logging
import threading
from typing import Protocol

from core.contracts import Evidence
from rag.config import RagSettings, get_settings

_log = logging.getLogger(__name__)


class Reranker(Protocol):
    def score(self, query: str, docs: list[str]) -> list[float]: ...


class ApiReranker:
    """FPT Cloud (Infinity) POST /rerank — returns results[{index, relevance_score}]
    sorted by score; we map back to the input order. A browser User-Agent is
    required (the gateway's Cloudflare rejects the default python client UA)."""

    _UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def __init__(self, settings: RagSettings):
        import httpx

        if not settings.rerank_api_key:
            raise RuntimeError(
                "Missing rerank API key: set RAG_RERANK_API_KEY (or FPT_CLOUD_KEY)"
            )
        self._url = settings.rerank_base_url.rstrip("/") + "/rerank"
        self._model = settings.rerank_model
        self._client = httpx.Client(
            timeout=settings.rerank_timeout_seconds,
            headers={
                "User-Agent": self._UA,
                "Authorization": f"Bearer {settings.rerank_api_key}",
                "Content-Type": "application/json",
            },
        )
        _log.info("Using API reranker %s at %s", self._model, self._url)

    def score(self, query: str, docs: list[str]) -> list[float]:
        resp = self._client.post(
            self._url,
            json={"model": self._model, "query": query, "documents": docs, "top_n": len(docs)},
        )
        resp.raise_for_status()
        scores = [0.0] * len(docs)
        for item in resp.json().get("results", []):
            idx = item.get("index")
            if isinstance(idx, int) and 0 <= idx < len(docs):
                scores[idx] = float(item.get("relevance_score", 0.0))
        return scores


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


def _build_reranker(settings: RagSettings) -> Reranker:
    if settings.rerank_provider == "cross_encoder":
        return CrossEncoderReranker(settings)
    if settings.rerank_provider in ("fptcloud", "api"):
        return ApiReranker(settings)
    raise ValueError(f"Unknown RAG_RERANK_PROVIDER: {settings.rerank_provider!r}")


_RERANKER: Reranker | None = None
_RERANKER_LOCK = threading.Lock()


def get_reranker(settings: RagSettings | None = None) -> Reranker:
    """Thread-safe process-wide singleton (builds the provider once)."""
    global _RERANKER
    if _RERANKER is None:
        with _RERANKER_LOCK:
            if _RERANKER is None:
                _RERANKER = _build_reranker(settings or get_settings())
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
