"""Attach dense (OpenAI-compatible API) + sparse (local BM25) vectors to chunks.

Dense embeddings go through any OpenAI-compatible endpoint (OpenAI, FPT Cloud);
sparse BM25 runs locally via fastembed — tiny model, no GPU needed.
Point ids are UUID5 of chunk_id so re-ingest overwrites instead of duplicating.
"""

import logging
import time
import uuid

from fastembed import SparseTextEmbedding
from openai import OpenAI, RateLimitError
from qdrant_client import models

from rag.config import RagSettings
from rag.kb_store import DENSE_VECTOR_NAME, SPARSE_VECTOR_NAME

_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-0000cafe0001")
# Small batch + inter-batch pause keeps us under provider tokens-per-minute
# limits (OpenAI free tier: 40k TPM for text-embedding-3-small).
DENSE_BATCH_SIZE = 32
BATCH_PAUSE_SECONDS = 1.0
MAX_RATELIMIT_RETRIES = 6

_log = logging.getLogger(__name__)


def point_id_for_chunk(chunk_id: str) -> str:
    """Stable Qdrant point id: same chunk_id always maps to the same point."""
    return str(uuid.uuid5(_NAMESPACE, chunk_id))


def _embed_one_batch(client: OpenAI, model: str, batch: list[str]) -> list[list[float]]:
    """Embed a single batch, backing off on provider rate limits (HTTP 429)."""
    for attempt in range(MAX_RATELIMIT_RETRIES):
        try:
            response = client.embeddings.create(model=model, input=batch)
            # Sort by index: OpenAI-compatible providers don't all guarantee
            # response order matches input order.
            items = sorted(response.data, key=lambda d: d.index)
            return [item.embedding for item in items]
        except RateLimitError:
            if attempt == MAX_RATELIMIT_RETRIES - 1:
                raise
            wait = 2.0 * (attempt + 1)  # linear backoff; provider resets per minute
            _log.warning("Rate limited, retrying in %.0fs (attempt %d)", wait, attempt + 1)
            time.sleep(wait)
    return []  # unreachable


def _embed_dense_batched(client: OpenAI, model: str, texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for i in range(0, len(texts), DENSE_BATCH_SIZE):
        vectors.extend(_embed_one_batch(client, model, texts[i : i + DENSE_BATCH_SIZE]))
        if i + DENSE_BATCH_SIZE < len(texts):
            time.sleep(BATCH_PAUSE_SECONDS)
    return vectors


def embed_chunks(chunks: list[dict], settings: RagSettings) -> list[models.PointStruct]:
    """Return payload-carrying points with named dense+sparse vectors."""
    if not chunks:
        return []
    if not settings.embed_api_key:
        raise RuntimeError(
            "Missing embedding API key: set RAG_EMBED_API_KEY (or OPENAI_API_KEY) in .env"
        )
    client = OpenAI(base_url=settings.embed_base_url, api_key=settings.embed_api_key)
    bm25 = SparseTextEmbedding(model_name=settings.sparse_model)

    texts = [chunk["content"] for chunk in chunks]
    dense = _embed_dense_batched(client, settings.embed_model, texts)
    if dense and len(dense[0]) != settings.embed_dim:
        raise ValueError(
            f"embed_dim mismatch: RAG_EMBED_DIM={settings.embed_dim} but model "
            f"'{settings.embed_model}' returned {len(dense[0])} dims. "
            "Fix RAG_EMBED_DIM and re-run with --recreate."
        )
    sparse = list(bm25.embed(texts))

    # Guard against a provider returning fewer vectors than inputs: zip() would
    # silently drop trailing chunks, corrupting the KB with no error.
    if len(dense) != len(chunks) or len(sparse) != len(chunks):
        raise RuntimeError(
            f"vector count mismatch: chunks={len(chunks)} "
            f"dense={len(dense)} sparse={len(sparse)}"
        )

    return [
        models.PointStruct(
            id=point_id_for_chunk(chunk["chunk_id"]),
            vector={
                DENSE_VECTOR_NAME: dense_vec,
                SPARSE_VECTOR_NAME: models.SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist(),
                ),
            },
            payload=chunk,
        )
        for chunk, dense_vec, sparse_vec in zip(chunks, dense, sparse)
    ]
