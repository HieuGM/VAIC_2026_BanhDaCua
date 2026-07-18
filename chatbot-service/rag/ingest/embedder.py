"""Attach dense + sparse vectors to chunks and build Qdrant points.

Dense embeddings come from the shared rag.embedding.get_embedder() (same model
the retriever uses for queries). Sparse BM25 runs locally via fastembed.
Point ids are UUID5 of chunk_id so re-ingest overwrites instead of duplicating.
"""

import uuid

from fastembed import SparseTextEmbedding
from qdrant_client import models

from rag.config import RagSettings
from rag.embedding import get_embedder
from rag.kb_store import DENSE_VECTOR_NAME, SPARSE_VECTOR_NAME

_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-0000cafe0001")


def point_id_for_chunk(chunk_id: str) -> str:
    """Stable Qdrant point id: same chunk_id always maps to the same point."""
    return str(uuid.uuid5(_NAMESPACE, chunk_id))


def embed_chunks(chunks: list[dict], settings: RagSettings) -> list[models.PointStruct]:
    """Return payload-carrying points with named dense+sparse vectors."""
    if not chunks:
        return []
    embedder = get_embedder(settings)
    bm25 = SparseTextEmbedding(model_name=settings.sparse_model)

    texts = [chunk["content"] for chunk in chunks]
    dense = embedder.embed_documents(texts)
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
