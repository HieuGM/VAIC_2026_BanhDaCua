"""Export a labeled retrieval eval set for embedding-model comparison.

Reuses the REAL ingest pipeline (loader → parsers → chunker) so the corpus is
byte-identical to what is served in production, then parses the built-in
[QA_xxx] groundtruth block (question + gold Nguồn fact ids) and resolves each
gold id to the chunk(s) whose category carries that id.

Outputs two JSONL files that the Colab/Kaggle notebook consumes:
  - corpus.jsonl : {chunk_id, content, category, source, source_type}
  - qa_eval.jsonl: {qa_id, question, gold_answer, gold_ids, gold_chunk_ids}

Run:  cd chatbot-service && python -m rag.ingest... no — python -m rag.eval.export_eval_data
"""

import json
import re
from pathlib import Path

from rag.config import get_settings
from rag.ingest.chunker import finalize_chunks
from rag.ingest.loader import load_sources
from rag.ingest.parsers import parse_source

QA_FILE = "groundtruth_gioi_thieu_benh_vien_tim_ha_noi.txt"
OUT_DIR = Path(__file__).parent / "data"

_QA_BLOCK_RE = re.compile(
    r"\[QA_(\d+)\]\s*"
    r"Câu hỏi:\s*(?P<q>.+?)\s*"
    r"Câu trả lời chuẩn:\s*(?P<a>.+?)\s*"
    r"Nguồn:\s*(?P<src>.+?)\s*(?=\n\s*\n|\[QA_|\Z)",
    re.DOTALL,
)
_ID_RE = re.compile(r"[A-Z]+(?:_[A-Z0-9]+)+")
_BRACKET_ID_RE = re.compile(r"\[([A-Z]+(?:_[A-Z0-9]+)+)\]")

# Meta/eval sections of the groundtruth spec that must NOT sit in the retrievable
# corpus: the QA samples (their questions+answers would leak straight into
# retrieval), the "do-not-use" data, and the chatbot usage rules. Detected by
# content/category markers.
_EXCLUDE_MARKERS = (
    "Câu trả lời chuẩn:",
    "[QA_",
    "MẪU GROUNDTRUTH",
    "KHÔNG NÊN DÙNG",
    "QUY TẮC SỬ DỤNG",
)


def _is_eval_meta(chunk: dict) -> bool:
    blob = f"{chunk.get('category') or ''}\n{chunk['content']}"
    return any(marker in blob for marker in _EXCLUDE_MARKERS)


def _expand_source_ids(src_line: str) -> list[str]:
    """Parse a Nguồn line into concrete ids, expanding 'X_001 đến X_004' ranges."""
    ids: list[str] = []
    for part in re.split(r"[,;]", src_line):
        part = part.strip()
        if " đến " in part:  # inclusive numeric range over a shared prefix
            lo, hi = (p.strip() for p in part.split(" đến ", 1))
            m_lo, m_hi = _ID_RE.search(lo), _ID_RE.search(hi)
            if m_lo and m_hi:
                prefix, start = m_lo.group().rsplit("_", 1)
                end = m_hi.group().rsplit("_", 1)[1]
                width = len(start)
                for n in range(int(start), int(end) + 1):
                    ids.append(f"{prefix}_{n:0{width}d}")
                continue
        m = _ID_RE.search(part)
        if m:
            ids.append(m.group())
    return ids


def build_corpus() -> list[dict]:
    settings = get_settings()
    corpus, excluded = [], 0
    for src in load_sources(settings.data_dir):
        for chunk in finalize_chunks(parse_source(src["text"], src["meta"]), src["meta"]):
            row = {
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "category": chunk["category"],
                "source": chunk["source"],
                "source_type": chunk["source_type"],
            }
            if _is_eval_meta(row):
                excluded += 1
                continue
            corpus.append(row)
    if excluded:
        print(f"Excluded {excluded} eval/meta chunks from corpus (leakage guard)")
    return corpus


def build_qa(corpus: list[dict]) -> list[dict]:
    settings = get_settings()
    text = (Path(settings.data_dir) / QA_FILE).read_text(encoding="utf-8")

    # id -> [chunk_id, ...]; a chunk category may carry several bracketed ids
    # (e.g. "III. ĐỊA VỊ PHÁP LÝ [FACT_LEGAL_001]").
    id_to_chunks: dict[str, list[str]] = {}
    for chunk in corpus:
        for gid in _BRACKET_ID_RE.findall(chunk["category"] or ""):
            id_to_chunks.setdefault(gid, []).append(chunk["chunk_id"])

    qa_items, unresolved = [], []
    for m in _QA_BLOCK_RE.finditer(text):
        gold_ids = _expand_source_ids(m.group("src"))
        gold_chunks = sorted({cid for gid in gold_ids for cid in id_to_chunks.get(gid, [])})
        if not gold_chunks:
            unresolved.append((m.group(1), gold_ids))
            continue  # no resolvable gold → unusable for retrieval scoring
        qa_items.append(
            {
                "qa_id": f"QA_{m.group(1)}",
                "question": " ".join(m.group("q").split()),
                "gold_answer": " ".join(m.group("a").split()),
                "gold_ids": gold_ids,
                "gold_chunk_ids": gold_chunks,
            }
        )
    if unresolved:
        print(f"WARNING: {len(unresolved)} QA dropped (gold id not a chunk category):")
        for qid, gids in unresolved:
            print(f"  QA_{qid}: {gids}")
    return qa_items


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus = build_corpus()
    qa = build_qa(corpus)

    with (OUT_DIR / "corpus.jsonl").open("w", encoding="utf-8") as f:
        for row in corpus:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (OUT_DIR / "qa_eval.jsonl").open("w", encoding="utf-8") as f:
        for row in qa:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"corpus.jsonl: {len(corpus)} chunks")
    print(f"qa_eval.jsonl: {len(qa)} usable queries")
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
