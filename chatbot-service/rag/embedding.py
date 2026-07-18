"""Shared dense embedding — ONE model for both ingest and query time.

The retriever (query) and the ingest embedder MUST embed with the same model,
or corpus and query vectors live in different spaces and retrieval breaks. This
module is the single source of truth; both sides call get_embedder().

Providers (RAG_EMBED_PROVIDER):
- sentence_transformers: local model (default BAAI/bge-m3), uses GPU if present.
- openai: OpenAI-compatible HTTP API (OpenAI / FPT Cloud).
"""

import logging
import threading
import time
from typing import Protocol

from rag.config import RagSettings, get_settings

_log = logging.getLogger(__name__)


class DenseEmbedder(Protocol):
    dim: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


class SentenceTransformerEmbedder:
    """Local model via sentence-transformers. bge-m3 is symmetric (no query/doc
    prefix). fp16 on CUDA; picks GPU automatically when available."""

    def __init__(self, settings: RagSettings):
        from sentence_transformers import SentenceTransformer
        import torch

        if settings.embed_device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = settings.embed_device
        # fp16 halves VRAM on GPU. Key is "dtype" on recent transformers
        # ("torch_dtype" is deprecated).
        model_kwargs = {"dtype": torch.float16} if device == "cuda" else {}
        self._model = SentenceTransformer(
            settings.embed_model, device=device, trust_remote_code=True,
            model_kwargs=model_kwargs,
        )
        self._model.max_seq_length = settings.embed_max_seq_length
        self._batch = settings.embed_batch_size
        # Method renamed across sentence-transformers versions; support both.
        get_dim = getattr(
            self._model, "get_embedding_dimension", None
        ) or self._model.get_sentence_embedding_dimension
        self.dim = get_dim()
        if self.dim != settings.embed_dim:
            # Localizes drift here instead of as an opaque Qdrant dimension error
            # at query time (collection was built with settings.embed_dim).
            _log.warning(
                "Model dim %d != RAG_EMBED_DIM %d — set RAG_EMBED_DIM=%d and re-ingest",
                self.dim, settings.embed_dim, self.dim,
            )
        _log.info("Loaded %s on %s (dim=%d)", settings.embed_model, device, self.dim)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vecs = self._model.encode(
            texts, batch_size=self._batch, normalize_embeddings=True,
            convert_to_numpy=True, show_progress_bar=len(texts) > 128,
        )
        return vecs.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class OpenAIEmbedder:
    """OpenAI-compatible embeddings API with rate-limit backoff + batching."""

    _MAX_RETRIES = 6

    def __init__(self, settings: RagSettings):
        from openai import OpenAI

        if not settings.embed_api_key:
            raise RuntimeError(
                "Missing embedding API key: set RAG_EMBED_API_KEY (or OPENAI_API_KEY)"
            )
        self._client = OpenAI(base_url=settings.embed_base_url, api_key=settings.embed_api_key)
        self._model = settings.embed_model
        self._batch = settings.embed_batch_size
        self.dim = settings.embed_dim

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        from openai import RateLimitError

        for attempt in range(self._MAX_RETRIES):
            try:
                resp = self._client.embeddings.create(model=self._model, input=batch)
                # Sort by index: provider order isn't guaranteed to match input.
                return [it.embedding for it in sorted(resp.data, key=lambda d: d.index)]
            except RateLimitError:
                if attempt == self._MAX_RETRIES - 1:
                    raise
                wait = 2.0 * (attempt + 1)
                _log.warning("Rate limited, retry in %.0fs (attempt %d)", wait, attempt + 1)
                time.sleep(wait)
        return []  # unreachable

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self._batch):
            out.extend(self._embed_batch(texts[i : i + self._batch]))
            if i + self._batch < len(texts):
                time.sleep(1.0)  # stay under tokens-per-minute limits
        return out

    def embed_query(self, text: str) -> list[float]:
        return self._embed_batch([text])[0]


def _build_embedder(settings: RagSettings) -> DenseEmbedder:
    if settings.embed_provider == "sentence_transformers":
        return SentenceTransformerEmbedder(settings)
    if settings.embed_provider == "openai":
        return OpenAIEmbedder(settings)
    raise ValueError(f"Unknown RAG_EMBED_PROVIDER: {settings.embed_provider!r}")


_EMBEDDER: DenseEmbedder | None = None
_EMBEDDER_LOCK = threading.Lock()


def get_embedder(settings: RagSettings | None = None) -> DenseEmbedder:
    """Process-wide singleton so the local model loads only once.

    Thread-safe: called from asyncio.to_thread workers, so concurrent first
    requests must not double-load the model. After the first call the cached
    embedder is returned and `settings` is ignored — call reset_embedder() to
    rebuild with a different config.
    """
    global _EMBEDDER
    if _EMBEDDER is None:
        with _EMBEDDER_LOCK:
            if _EMBEDDER is None:
                _EMBEDDER = _build_embedder(settings or get_settings())
    return _EMBEDDER


def reset_embedder() -> None:
    """Drop the cached embedder (test isolation / config change)."""
    global _EMBEDDER
    _EMBEDDER = None
