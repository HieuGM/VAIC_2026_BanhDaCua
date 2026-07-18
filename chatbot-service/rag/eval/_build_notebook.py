"""Generator for embedding_benchmark.ipynb (kept in-repo so the notebook is
reproducible/reviewable as source instead of opaque JSON). Run once:
    python -m rag.eval._build_notebook
"""

import json
from pathlib import Path

MD = "markdown"
CODE = "code"

CELLS: list[tuple[str, str]] = [
    (MD, r"""# So sánh chất lượng Embedding — RAG Bệnh viện Tim Hà Nội

So sánh khả năng **truy hồi (retrieval)** của các model embedding trên chính
corpus + bộ câu hỏi có nhãn của dự án:

- `text-embedding-3-small` (OpenAI, 1536d) — model đang dùng ở production
- `BAAI/bge-m3` (1024d, đa ngôn ngữ)
- `Qwen/Qwen3-Embedding-0.6B` (1024d, đa ngôn ngữ)
- BM25 (baseline từ khóa, tham chiếu vì hệ thống thật là hybrid)

**Chỉ số**: Hit@1/3/5, MRR@10, nDCG@10 — trên 24 câu hỏi có gold chunk.

## Cách chạy
1. Chạy `python -m rag.eval.export_eval_data` ở máy để tạo `corpus.jsonl` + `qa_eval.jsonl`.
2. Upload 2 file đó vào Colab/Kaggle khi cell yêu cầu.
3. Bật GPU (Runtime → Change runtime type → T4) cho BGE-M3 / Qwen3.
4. OpenAI là tùy chọn — dán API key khi được hỏi, bỏ trống để bỏ qua.

> **Nếu gặp CUDA OOM**: chạy `Runtime → Restart runtime` rồi chạy lại từ đầu.
> Backend đã dùng fp16 + `max_seq_length=512` + giải phóng VRAM giữa các model;
> nếu vẫn OOM, giảm `batch` xuống 8 trong cell backend."""),

    (CODE, r"""# 1. Cài dependencies (Colab/Kaggle)
%pip install -q "sentence-transformers>=3.0" rank-bm25 openai numpy pandas"""),

    (CODE, r'''# 2. Nạp dữ liệu eval (corpus.jsonl + qa_eval.jsonl)
import json, os

def _load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

if not (os.path.exists("corpus.jsonl") and os.path.exists("qa_eval.jsonl")):
    try:
        from google.colab import files  # type: ignore
        print("Upload corpus.jsonl và qa_eval.jsonl:")
        files.upload()
    except ImportError:
        raise SystemExit("Đặt corpus.jsonl và qa_eval.jsonl cạnh notebook trước khi chạy.")

corpus = _load_jsonl("corpus.jsonl")
qa = _load_jsonl("qa_eval.jsonl")
corpus_texts = [c["content"] for c in corpus]
chunk_ids = [c["chunk_id"] for c in corpus]
id_pos = {cid: i for i, cid in enumerate(chunk_ids)}
print(f"corpus: {len(corpus)} chunks | queries: {len(qa)}")'''),

    (CODE, r'''# 3. Chỉ số retrieval (Hit@k, MRR@10, nDCG@10) từ ma trận điểm số
import numpy as np

K_LIST = (1, 3, 5, 10)

def evaluate(scores: np.ndarray) -> dict:
    """scores: [num_queries, num_corpus]; dùng gold_chunk_ids trong `qa`."""
    hits = {k: 0.0 for k in K_LIST}
    mrr = 0.0
    ndcg = 0.0
    for qi, item in enumerate(qa):
        gold = {id_pos[c] for c in item["gold_chunk_ids"] if c in id_pos}
        if not gold:
            continue
        order = np.argsort(-scores[qi])  # chỉ số corpus theo điểm giảm dần
        ranked = order.tolist()
        # rank (1-based) của gold đầu tiên
        first = next((r for r, idx in enumerate(ranked, 1) if idx in gold), None)
        if first:
            mrr += 1.0 / first
            for k in K_LIST:
                if first <= k:
                    hits[k] += 1.0
        # nDCG@10 nhị phân
        dcg = sum(1.0 / np.log2(r + 1) for r, idx in enumerate(ranked[:10], 1) if idx in gold)
        idcg = sum(1.0 / np.log2(i + 1) for i in range(1, min(10, len(gold)) + 1))
        ndcg += dcg / idcg if idcg else 0.0
    n = len(qa)
    out = {f"Hit@{k}": hits[k] / n for k in K_LIST}
    out["MRR@10"] = mrr / n
    out["nDCG@10"] = ndcg / n
    return out

def cosine_scores(q_emb: np.ndarray, d_emb: np.ndarray) -> np.ndarray:
    q = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-9)
    d = d_emb / (np.linalg.norm(d_emb, axis=1, keepdims=True) + 1e-9)
    return q @ d.T'''),

    (CODE, r'''# 4. Backend embedding
import gc
import numpy as np

def _free_gpu():
    """Giải phóng VRAM giữa các model — nếu không, T4 (~15GB) sẽ OOM khi
    nạp bge-m3 rồi Qwen3 liên tiếp."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass

def embed_sentence_transformers(model_name, queries, docs, query_prompt=None,
                                batch=16, max_seq_length=512):
    from sentence_transformers import SentenceTransformer
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # fp16 trên GPU: giảm nửa VRAM. max_seq_length nhỏ: chunk của ta ≤~400 token,
    # tránh bge-m3 cấp phát attention buffer cho 8192 token mặc định.
    model_kwargs = {"torch_dtype": torch.float16} if device == "cuda" else {}
    model = SentenceTransformer(model_name, device=device, trust_remote_code=True,
                                model_kwargs=model_kwargs)
    model.max_seq_length = max_seq_length
    enc = dict(batch_size=batch, show_progress_bar=True,
               normalize_embeddings=True, convert_to_numpy=True)
    d_emb = model.encode(docs, **enc)
    q_kwargs = {"prompt": query_prompt} if query_prompt else {}
    q_emb = model.encode(queries, **enc, **q_kwargs)
    del model
    _free_gpu()
    return q_emb, d_emb

def embed_openai(model_name, texts, api_key, batch=128):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    out = []
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=model_name, input=texts[i:i+batch])
        out.extend(d.embedding for d in sorted(resp.data, key=lambda x: x.index))
    return np.array(out, dtype=np.float32)

def bm25_scores(queries, docs):
    from rank_bm25 import BM25Okapi
    tok_docs = [d.lower().split() for d in docs]
    bm25 = BM25Okapi(tok_docs)
    return np.array([bm25.get_scores(q.lower().split()) for q in queries])'''),

    (CODE, r'''# 5. Chạy đánh giá cho từng model
import pandas as pd

questions = [q["question"] for q in qa]
results = {}

# --- BM25 baseline ---
results["BM25"] = evaluate(bm25_scores(questions, corpus_texts))
print("BM25 done")

# --- BGE-M3 ---
q_emb, d_emb = embed_sentence_transformers("BAAI/bge-m3", questions, corpus_texts)
results["bge-m3"] = evaluate(cosine_scores(q_emb, d_emb))
print("bge-m3 done")

# --- Qwen3-Embedding-0.6B (instruction cho query) ---
qwen_prompt = "Instruct: Given a question, retrieve passages that answer it\nQuery: "
q_emb, d_emb = embed_sentence_transformers(
    "Qwen/Qwen3-Embedding-0.6B", questions, corpus_texts, query_prompt=qwen_prompt)
results["qwen3-0.6b"] = evaluate(cosine_scores(q_emb, d_emb))
print("qwen3 done")

# --- OpenAI text-embedding-3-small (tùy chọn) ---
import getpass
key = getpass.getpass("OpenAI API key (Enter để bỏ qua): ").strip()
if key:
    d_emb = embed_openai("text-embedding-3-small", corpus_texts, key)
    q_emb = embed_openai("text-embedding-3-small", questions, key)
    results["openai-3-small"] = evaluate(cosine_scores(q_emb, d_emb))
    print("openai done")'''),

    (CODE, r'''# 6. Bảng so sánh + biểu đồ
import pandas as pd

df = pd.DataFrame(results).T
df = df[["Hit@1", "Hit@3", "Hit@5", "Hit@10", "MRR@10", "nDCG@10"]]
df = df.sort_values("nDCG@10", ascending=False).round(4)
display(df)

ax = df[["Hit@1", "Hit@5", "MRR@10", "nDCG@10"]].plot.bar(
    figsize=(10, 5), title="Embedding retrieval quality — Hanoi Heart Hospital")
ax.set_ylabel("score"); ax.set_ylim(0, 1)
ax.legend(loc="lower right"); ax.grid(axis="y", alpha=0.3)'''),

    (MD, r"""## Ghi chú diễn giải

- **24 câu hỏi** đều thuộc nhóm *giới thiệu bệnh viện* (document), truy hồi trên
  **762 chunk** (phần lớn là dòng bảng giá) → đo được khả năng phân biệt của model.
- Corpus đã **loại bỏ 11 chunk meta/leakage** (mục Q&A mẫu, "dữ liệu không nên dùng",
  "quy tắc chatbot") để tránh câu hỏi trùng khớp nguyên văn trong kho.
- BM25 là baseline từ khóa; hệ thống thật chạy **hybrid dense + BM25 + RRF**, nên
  điểm dense đơn lẻ thấp hơn hybrid thực tế.
- Nếu chọn đổi sang bge-m3 / Qwen3: cập nhật `RAG_EMBED_MODEL`, `RAG_EMBED_DIM=1024`,
  `RAG_EMBED_BASE_URL` (FPT Cloud) rồi chạy lại `run_ingest --recreate`.

**Câu hỏi mở**: bộ eval mới phủ nhóm *document*; cần bổ sung câu hỏi giá dịch vụ +
lịch bác sĩ để đánh giá nhóm price_table/schedule trước khi quyết định đổi model."""),
]


def build() -> dict:
    def cell(kind: str, text: str) -> dict:
        src = text.splitlines(keepends=True)
        base = {"cell_type": kind, "metadata": {}, "source": src}
        if kind == CODE:
            base["outputs"] = []
            base["execution_count"] = None
        return base

    return {
        "cells": [cell(k, t) for k, t in CELLS],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "accelerator": "GPU",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


if __name__ == "__main__":
    out = Path(__file__).parent / "embedding_benchmark.ipynb"
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out}")
