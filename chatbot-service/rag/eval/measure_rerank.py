"""Compare rerankers on the labeled eval set (evidence before choosing phase-5).

For each query: take the top-N hybrid candidates from the LIVE collection, rerank
them with each method, measure how well gold is pushed to the top. The candidate
set is identical across methods, so differences are purely the reranker. Results
are broken down by group (document / price / schedule).

Methods: no-rerank baseline · bge-reranker-v2-m3 (local CE, GPU) ·
jina-reranker-v2-multilingual (local, fastembed) · LLM listwise (OpenAI).

Run (server stopped): cd chatbot-service && python -m rag.eval.measure_rerank
"""

import gc
import json
import math
import re

from fastembed import SparseTextEmbedding

from rag.config import get_settings
from rag.embedding import get_embedder, reset_embedder
from rag.eval._eval_data import load_eval_qa
from rag.kb_store import KnowledgeBaseStore

CAND_N = 20  # candidate pool handed to each reranker
K_LIST = (1, 3, 5)
LLM_SNIPPET = 400  # chars per candidate sent to the LLM (token control)
COLS = ("Hit@1", "Hit@3", "Hit@5", "MRR", "nDCG@10")


def _free_gpu():
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def _metrics(ranks):
    n = len(ranks) or 1
    hits = {k: sum(1 for r in ranks if r and r <= k) / n for k in K_LIST}
    mrr = sum(1.0 / r for r in ranks if r) / n
    ndcg = sum(1.0 / math.log2(r + 1) for r in ranks if r and r <= 10) / n
    return {**{f"Hit@{k}": round(hits[k], 3) for k in K_LIST},
            "MRR": round(mrr, 3), "nDCG@10": round(ndcg, 3)}


def _first_gold(order_ids, gold):
    for rank, cid in enumerate(order_ids, 1):
        if cid in gold:
            return rank
    return None


def _order_by_scores(cands, scores):
    return [cands[i][0] for i in sorted(range(len(cands)), key=lambda i: -scores[i])]


def load_candidates():
    """Per query: {question, gold set, cands [(id, content)], group}."""
    qa = load_eval_qa()
    s = get_settings()
    store = KnowledgeBaseStore(s)
    emb = get_embedder(s)
    bm25 = SparseTextEmbedding(model_name=s.sparse_model)
    rows = []
    for it in qa:
        dvec = emb.embed_query(it["question"])
        sp = next(bm25.query_embed(it["question"]))
        hits = store.hybrid_search(
            dvec, {"indices": sp.indices.tolist(), "values": sp.values.tolist()}, limit=CAND_N
        )
        rows.append({
            "question": it["question"],
            "gold": set(it["gold_chunk_ids"]),
            "cands": [(h.payload["chunk_id"], h.payload["content"]) for h in hits],
            "group": it["group"],
        })
    store.close()
    return rows


def rank_baseline(rows):
    return [_first_gold([c[0] for c in r["cands"]], r["gold"]) for r in rows]


def rank_cross_encoder(rows, model_name):
    from sentence_transformers import CrossEncoder
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ce = CrossEncoder(model_name, device=device, max_length=512)
    ranks = []
    for r in rows:
        scores = ce.predict([(r["question"], c[1]) for c in r["cands"]], batch_size=16)
        ranks.append(_first_gold(_order_by_scores(r["cands"], scores), r["gold"]))
    del ce
    _free_gpu()
    return ranks


def rank_fastembed(rows, model_name):
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    rr = TextCrossEncoder(model_name=model_name)
    ranks = []
    for r in rows:
        scores = list(rr.rerank(r["question"], [c[1] for c in r["cands"]]))
        ranks.append(_first_gold(_order_by_scores(r["cands"], scores), r["gold"]))
    return ranks


def rank_llm(rows):
    from openai import OpenAI
    s = get_settings()
    if not s.rerank_api_key:
        return None
    client = OpenAI(base_url=s.rerank_base_url, api_key=s.rerank_api_key)
    ranks = []
    for r in rows:
        listing = "\n".join(f"[{i}] {c[1][:LLM_SNIPPET]}" for i, c in enumerate(r["cands"]))
        prompt = (
            f"Câu hỏi: {r['question']}\n\nĐoạn tài liệu:\n{listing}\n\n"
            "Sắp xếp các đoạn theo mức độ liên quan với câu hỏi (liên quan nhất trước). "
            "Chỉ trả về JSON mảng chỉ số, ví dụ [3,0,7]."
        )
        try:
            resp = client.chat.completions.create(
                model=s.rerank_model, temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            idxs = json.loads(re.search(r"\[[\d,\s]*\]", resp.choices[0].message.content).group())
            order = [r["cands"][i][0] for i in idxs if 0 <= i < len(r["cands"])]
        except Exception:
            order = [c[0] for c in r["cands"]]  # fall back to retrieval order
        ranks.append(_first_gold(order, r["gold"]))
    return ranks


def _safe(ranks_by, name, fn):
    try:
        out = fn()
        if out is not None:
            ranks_by[name] = out
            print(f"{name} done")
    except Exception as e:
        print(f"{name} FAILED: {type(e).__name__}: {e}")


def main():
    rows = load_candidates()
    groups: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        groups.setdefault(r["group"], []).append(i)
    recall = sum(1 for r in rows if r["gold"] & {c[0] for c in r["cands"]}) / len(rows)
    print(f"pool N={CAND_N} | queries={len(rows)} | recall ceiling (gold in pool)={recall:.3f}\n")
    reset_embedder()  # free bge-m3 VRAM before loading rerankers
    _free_gpu()

    ranks_by: dict[str, list] = {}
    _safe(ranks_by, "1. no-rerank", lambda: rank_baseline(rows))
    _safe(ranks_by, "2. bge-reranker-v2-m3", lambda: rank_cross_encoder(rows, "BAAI/bge-reranker-v2-m3"))
    _safe(ranks_by, "3. jina-reranker-v2-multi",
          lambda: rank_fastembed(rows, "jinaai/jina-reranker-v2-base-multilingual"))
    _safe(ranks_by, "4. LLM listwise (OpenAI)", lambda: rank_llm(rows))

    for gname, idxs in [("ALL", list(range(len(rows))))] + sorted(groups.items()):
        print(f"\n=== {gname} (n={len(idxs)}) ===")
        print(f"{'method':26} " + "  ".join(f"{c:>7}" for c in COLS))
        for name, ranks in ranks_by.items():
            m = _metrics([ranks[i] for i in idxs])
            print(f"{name:26} " + "  ".join(f"{m[c]:7.3f}" for c in COLS))


if __name__ == "__main__":
    main()
