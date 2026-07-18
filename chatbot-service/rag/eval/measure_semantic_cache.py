"""Calibrate the semantic-cache similarity threshold on the REAL eval set.

The risk of a semantic cache is a FALSE POSITIVE: query B matches cached query A
by embedding similarity but actually needs a DIFFERENT answer, so we serve A's
answer for B. In a medical domain that is dangerous, so the threshold must sit
ABOVE the highest query-query cosine between questions with DISJOINT gold chunks.

Method (measure, don't guess):
  - embed every eval question with the LIVE embedder (NVIDIA bge-m3 query vectors)
  - all-pairs cosine
  - a pair is UNSAFE if cos >= t and their gold_chunk_ids are disjoint
    (caching one answer for the other would be wrong)
  - a pair is SAFE-REUSE if cos >= t and gold overlaps (correct to reuse)
  - sweep t; recommend the LOWEST t with zero unsafe collisions (max reuse while
    provably safe on this set), then add margin for the config default.

Only needs the embedder (no Qdrant) → safe to run while the server is up.

Run: cd chatbot-service && python -m rag.eval.measure_semantic_cache
"""

import numpy as np

from rag.config import get_settings
from rag.embedding import get_embedder
from rag.eval._eval_data import load_eval_qa


def _l2(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.where(norms > 0, norms, 1.0)


def main() -> None:
    qa = load_eval_qa()
    embedder = get_embedder(get_settings())

    questions = [it["question"] for it in qa]
    golds = [set(it["gold_chunk_ids"]) for it in qa]
    vecs = _l2(np.array([embedder.embed_query(q) for q in questions], dtype=np.float32))

    n = len(qa)
    sims = vecs @ vecs.T  # cosine, [-1, 1]

    # Collect upper-triangle pairs, tagged safe (gold overlaps) vs unsafe (disjoint).
    unsafe, safe = [], []  # (cos, i, j)
    for i in range(n):
        for j in range(i + 1, n):
            c = float(sims[i, j])
            (safe if golds[i] & golds[j] else unsafe).append((c, i, j))

    unsafe_cos = np.array([c for c, _, _ in unsafe]) if unsafe else np.array([0.0])
    safe_cos = np.array([c for c, _, _ in safe]) if safe else np.array([])

    print(f"questions={n}  pairs={n*(n-1)//2}  "
          f"(unsafe/disjoint-gold={len(unsafe)}, safe/shared-gold={len(safe)})")
    print(f"\nUNSAFE-pair cosine (different answers): "
          f"max={unsafe_cos.max():.4f} p99={np.percentile(unsafe_cos,99):.4f} "
          f"median={np.median(unsafe_cos):.4f}")
    if safe_cos.size:
        print(f"SAFE-pair   cosine (same answer)     : "
              f"max={safe_cos.max():.4f} median={np.median(safe_cos):.4f} "
              f"min={safe_cos.min():.4f}")

    print(f"\n{'thr':>6} {'unsafe_hits':>12} {'safe_reuse':>11}")
    safe_floor = None
    for t in np.arange(0.80, 0.991, 0.01):
        u = int((unsafe_cos >= t).sum())
        s = int((safe_cos >= t).sum()) if safe_cos.size else 0
        print(f"{t:6.2f} {u:12d} {s:11d}")
        if u == 0 and safe_floor is None:
            safe_floor = float(t)

    hard_max = float(unsafe_cos.max())
    print(f"\nHighest UNSAFE cosine on this set = {hard_max:.4f} "
          f"(any threshold <= this serves a wrong answer for >=1 pair)")
    if safe_floor is not None:
        print(f"Lowest zero-collision threshold  = {safe_floor:.2f}")
    print("Recommend cache_similarity_threshold >= "
          f"{max(hard_max, safe_floor or 0.0):.4f}; the 0.95 default keeps "
          "margin above the observed unsafe max.")

    # Show the most dangerous near-collisions so a human can eyeball them.
    print("\nTop unsafe near-collisions (cos, Qi | Qj):")
    for c, i, j in sorted(unsafe, reverse=True)[:5]:
        print(f"  {c:.4f}  {questions[i][:48]!r}  ||  {questions[j][:48]!r}")


if __name__ == "__main__":
    main()
