"""Measure retrieval design choices against the LIVE Qdrant collection.

Evidence for phase-4 decisions (don't assume — measure):
  - dense-only vs hybrid (dense+BM25 RRF) recall on the labeled eval set
  - dense cosine score distribution: gold top-1 vs an off-topic query
    -> calibrates the return-[] threshold (RAG_DENSE_MIN_SCORE)

Run (server stopped): cd chatbot-service && python -m rag.eval.measure_retrieval
"""

from fastembed import SparseTextEmbedding

import numpy as np

from rag.config import get_settings
from rag.embedding import get_embedder
from rag.eval._eval_data import by_group, load_eval_qa
from rag.kb_store import DENSE_VECTOR_NAME, KnowledgeBaseStore

K_LIST = (1, 3, 5, 10)
OFFTOPIC = ["cách nấu phở bò tái", "giá vé máy bay đi Đà Nẵng", "kết quả bóng đá ngoại hạng Anh"]


def _metrics(ranks: list[int | None]) -> dict:
    n = len(ranks) or 1
    hits = {k: sum(1 for r in ranks if r and r <= k) / n for k in K_LIST}
    mrr = sum(1.0 / r for r in ranks if r) / n
    return {**{f"Hit@{k}": round(hits[k], 3) for k in K_LIST}, "MRR@10": round(mrr, 3)}


def _first_gold_rank(points, gold: set[str]) -> int | None:
    for rank, p in enumerate(points, 1):
        if p.payload["chunk_id"] in gold:
            return rank
    return None


def main() -> None:
    qa = load_eval_qa()
    settings = get_settings()
    store = KnowledgeBaseStore(settings)
    embedder = get_embedder(settings)
    bm25 = SparseTextEmbedding(model_name=settings.sparse_model)

    for item in qa:  # annotate each item with dense/hybrid gold ranks + top cosine
        gold = set(item["gold_chunk_ids"])
        dvec = embedder.embed_query(item["question"])
        sp = next(bm25.query_embed(item["question"]))
        svec = {"indices": sp.indices.tolist(), "values": sp.values.tolist()}
        dense = store.client.query_points(
            settings.collection, query=dvec, using=DENSE_VECTOR_NAME,
            limit=10, with_payload=["chunk_id"],
        ).points
        hybrid = store.hybrid_search(dvec, svec, limit=10)
        item["_dense"] = _first_gold_rank(dense, gold)
        item["_hybrid"] = _first_gold_rank(hybrid, gold)
        item["_cos"] = dense[0].score if dense else 0.0

    off_cos = []
    for q in OFFTOPIC:
        pts = store.client.query_points(
            settings.collection, query=embedder.embed_query(q),
            using=DENSE_VECTOR_NAME, limit=1,
        ).points
        off_cos.append(round(pts[0].score, 3) if pts else 0.0)
    store.close()

    groups = by_group(qa)
    print("=== dense-only vs hybrid RRF (first gold rank), per group ===")
    for name, items in [("ALL", qa), *sorted(groups.items())]:
        d = _metrics([it["_dense"] for it in items])
        h = _metrics([it["_hybrid"] for it in items])
        print(f"\n[{name}] n={len(items)}")
        print(f"  dense : {d}")
        print(f"  hybrid: {h}")
    gc = np.array([it["_cos"] for it in qa])
    print("\n=== dense cosine calibration ===")
    print(f"in-domain top-1 cosine: min={gc.min():.3f} p25={np.percentile(gc,25):.3f} "
          f"median={np.median(gc):.3f}")
    print("off-topic top-1 cosine:", off_cos)


if __name__ == "__main__":
    main()
