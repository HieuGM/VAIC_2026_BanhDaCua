"""Measure retrieval design choices against the LIVE Qdrant collection.

Evidence for phase-4 decisions (don't assume — measure):
  - dense-only vs hybrid (dense+BM25 RRF) recall on the labeled eval set
  - dense cosine score distribution: gold top-1 vs an off-topic query
    -> calibrates the return-[] threshold (RAG_DENSE_MIN_SCORE)

Run (server stopped): cd chatbot-service && python -m rag.eval.measure_retrieval
"""

import json
from pathlib import Path

import numpy as np
from fastembed import SparseTextEmbedding
from qdrant_client import models

from rag.config import get_settings
from rag.embedding import get_embedder
from rag.kb_store import DENSE_VECTOR_NAME, SPARSE_VECTOR_NAME, KnowledgeBaseStore

DATA = Path(__file__).parent / "data"
K_LIST = (1, 3, 5, 10)
OFFTOPIC = ["cách nấu phở bò tái", "giá vé máy bay đi Đà Nẵng", "kết quả bóng đá ngoại hạng Anh"]


def _metrics(ranks: list[int | None], n: int) -> dict:
    hits = {k: sum(1 for r in ranks if r and r <= k) / n for k in K_LIST}
    mrr = sum(1.0 / r for r in ranks if r) / n
    return {**{f"Hit@{k}": round(hits[k], 3) for k in K_LIST}, "MRR@10": round(mrr, 3)}


def _first_gold_rank(points, gold: set[str]) -> int | None:
    for rank, p in enumerate(points, 1):
        if p.payload["chunk_id"] in gold:
            return rank
    return None


def main() -> None:
    qa = [json.loads(l) for l in (DATA / "qa_eval.jsonl").read_text(encoding="utf-8").splitlines()]
    settings = get_settings()
    store = KnowledgeBaseStore(settings)
    embedder = get_embedder(settings)
    bm25 = SparseTextEmbedding(model_name=settings.sparse_model)

    dense_ranks, hybrid_ranks, gold_top_cos = [], [], []
    for item in qa:
        gold = set(item["gold_chunk_ids"])
        q = item["question"]
        dvec = embedder.embed_query(q)
        sp = next(bm25.query_embed(q))
        svec = {"indices": sp.indices.tolist(), "values": sp.values.tolist()}

        dense = store.client.query_points(
            settings.collection, query=dvec, using=DENSE_VECTOR_NAME,
            limit=10, with_payload=["chunk_id"],
        ).points
        hybrid = store.hybrid_search(dvec, svec, limit=10)

        dense_ranks.append(_first_gold_rank(dense, gold))
        hybrid_ranks.append(_first_gold_rank(hybrid, gold))
        if dense:
            gold_top_cos.append(dense[0].score)  # cosine of top-1 (calibration)

    # Off-topic: top-1 cosine should be clearly lower than in-domain gold.
    off_cos = []
    for q in OFFTOPIC:
        pts = store.client.query_points(
            settings.collection, query=embedder.embed_query(q),
            using=DENSE_VECTOR_NAME, limit=1,
        ).points
        off_cos.append(round(pts[0].score, 3) if pts else 0.0)
    store.close()

    n = len(qa)
    print("=== Recall (first gold rank) over", n, "queries ===")
    print("dense-only:", _metrics(dense_ranks, n))
    print("hybrid RRF:", _metrics(hybrid_ranks, n))
    gc = np.array(gold_top_cos)
    print("\n=== dense cosine calibration ===")
    print(f"in-domain top-1 cosine: min={gc.min():.3f} p25={np.percentile(gc,25):.3f} "
          f"median={np.median(gc):.3f}")
    print("off-topic top-1 cosine:", off_cos)


if __name__ == "__main__":
    main()
