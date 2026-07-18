"""Semantic chunking variant — split prose where the meaning shifts.

Approach (à la LangChain SemanticChunker): segment into sentences, embed each
with bge-m3, and cut between consecutive sentences whose cosine similarity falls
below a percentile threshold (a "semantic valley"). Compared against the
structural per-file parsers via rag/eval/compare_chunking.py.

Note: best for continuous prose. Our corpus is mostly structured (FACT blocks,
tables, numbered steps), so this is an experiment to measure, not assume.
"""

import re

import numpy as np

from rag.config import RagSettings
from rag.embedding import get_embedder

_SENT_SPLIT_RE = re.compile(r"(?<=[.!?:])\s+|\n+")


def _segments(text: str) -> list[str]:
    segs = [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]
    return [s for s in segs if len(s) > 1]


def semantic_chunk(
    text: str, meta: dict, settings: RagSettings,
    breakpoint_percentile: int = 85, max_chars: int = 1000,
) -> list[dict]:
    """Return partial chunks. Cut at similarity drops below the (100-pct)
    percentile, or when a chunk would exceed max_chars."""
    segments = _segments(text)
    if len(segments) <= 1:
        return [{"content": text.strip(), "title": meta["title"], "category": None}]

    embedder = get_embedder(settings)
    emb = np.asarray(embedder.embed_documents(segments), dtype=np.float32)
    # embeddings are already normalized → dot product = cosine
    sims = np.sum(emb[:-1] * emb[1:], axis=1)
    cutoff = float(np.percentile(sims, 100 - breakpoint_percentile))

    chunks: list[str] = []
    current = [segments[0]]
    for i, sim in enumerate(sims):
        joined = " ".join(current)
        if sim < cutoff or len(joined) + len(segments[i + 1]) > max_chars:
            chunks.append(joined)
            current = [segments[i + 1]]
        else:
            current.append(segments[i + 1])
    chunks.append(" ".join(current))

    return [
        {"content": c.strip(), "title": meta["title"], "category": None}
        for c in chunks if c.strip()
    ]
