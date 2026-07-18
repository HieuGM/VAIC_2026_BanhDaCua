"""Structural vs semantic chunking — measured on the labeled groundtruth QA.

Chunks the groundtruth file both ways, embeds each variant's chunks + the 24
questions with bge-m3, retrieves within that variant's chunk pool, and reports
Hit@k/MRR. Gold is chunking-agnostic: a chunk is gold if its content contains
"[<gold_fact_id>]" (the bracket id survives in the text under any chunking).

Run: cd chatbot-service && python -m rag.eval.compare_chunking
"""

import json
from pathlib import Path

import numpy as np

from rag.config import get_settings
from rag.embedding import get_embedder
from rag.ingest.chunker import finalize_chunks
from rag.ingest.loader import load_sources
from rag.ingest.parsers.groundtruth_parser import parse_groundtruth
from rag.ingest.semantic_chunker import semantic_chunk

DATA = Path(__file__).parent / "data"
K_LIST = (1, 3, 5)


def _metrics(ranks):
    n = len(ranks) or 1
    hits = {k: sum(1 for r in ranks if r and r <= k) / n for k in K_LIST}
    mrr = sum(1.0 / r for r in ranks if r) / n
    return {**{f"Hit@{k}": round(hits[k], 3) for k in K_LIST}, "MRR": round(mrr, 3)}


def _measure(chunks, qa, embedder):
    texts = [c["content"] for c in chunks]
    demb = np.asarray(embedder.embed_documents(texts), dtype=np.float32)
    qemb = np.asarray(embedder.embed_documents([q["question"] for q in qa]), dtype=np.float32)
    scores = qemb @ demb.T  # normalized → cosine
    ranks = []
    for qi, item in enumerate(qa):
        gold_ids = {f"[{g}]" for g in item["gold_ids"]}
        gold_idx = {i for i, t in enumerate(texts) if any(g in t for g in gold_ids)}
        order = np.argsort(-scores[qi]).tolist()
        ranks.append(next((r for r, idx in enumerate(order, 1) if idx in gold_idx), None))
    return _metrics(ranks)


def main():
    settings = get_settings()
    embedder = get_embedder(settings)
    qa = [json.loads(l) for l in (DATA / "qa_eval.jsonl").read_text(encoding="utf-8").splitlines()]
    src = next(s for s in load_sources(settings.data_dir) if s["meta"]["parser"] == "groundtruth")

    structural = finalize_chunks(parse_groundtruth(src["text"], src["meta"]), src["meta"])
    semantic = finalize_chunks(semantic_chunk(src["text"], src["meta"], settings), src["meta"])

    print(f"structural: {len(structural)} chunks | semantic: {len(semantic)} chunks")
    print(f"queries: {len(qa)} (gold = content contains [FACT_id])\n")
    print(f"{'chunking':14} " + "  ".join(f"{k:>6}" for k in ("Hit@1", "Hit@3", "Hit@5", "MRR")))
    for name, chunks in [("structural", structural), ("semantic", semantic)]:
        m = _measure(chunks, qa, embedder)
        print(f"{name:14} " + "  ".join(f"{m[k]:6.3f}" for k in ("Hit@1", "Hit@3", "Hit@5", "MRR")))


if __name__ == "__main__":
    main()
