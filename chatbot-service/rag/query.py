"""Try the RAG retrieval by hand — see the grounded Evidence for a question.

Runs the real pipeline (bge-m3 embed → hybrid + filter → bge-reranker rerank).
The knowledge base must be ingested first (python -m rag.ingest.run_ingest) and
the API server must be STOPPED (embedded Qdrant is single-process).

Usage:
    cd chatbot-service
    python -m rag.query "giá khám bệnh theo bảo hiểm y tế"   # one question
    python -m rag.query                                       # interactive loop
"""

import asyncio
import sys

from rag.retriever import retrieve_public_knowledge


async def ask(question: str) -> None:
    evidence = await retrieve_public_knowledge({"normalized_message": question})
    if not evidence:
        print("  → không có evidence (off-topic, hết hiệu lực, hoặc dưới ngưỡng)")
        return
    for i, e in enumerate(evidence, 1):
        cid = e.citation.chunk_id if e.citation else "?"
        print(f"  [{i}] conf={e.confidence:.3f} | {e.title}")
        print(f"      nguồn: {e.citation.source if e.citation else '?'} · chunk {cid}")
        print(f"      {(e.content or '')[:220].strip()}")


def main() -> None:
    if len(sys.argv) > 1:  # one-shot mode
        asyncio.run(ask(" ".join(sys.argv[1:])))
        return
    print("RAG query — nhập câu hỏi (Enter trống để thoát). Model tải ~10-20s lần đầu.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            break
        asyncio.run(ask(question))


if __name__ == "__main__":
    main()
