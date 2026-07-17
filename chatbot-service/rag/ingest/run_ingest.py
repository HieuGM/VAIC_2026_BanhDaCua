"""Offline ingest CLI: load → parse → chunk → embed → upsert into Qdrant.

Run with the API server STOPPED (embedded Qdrant is single-process):

    cd chatbot-service && python -m rag.ingest.run_ingest [--recreate] [--limit-source NAME]
"""

import argparse
import logging

from qdrant_client import models

from rag.config import get_settings
from rag.ingest.chunker import finalize_chunks
from rag.ingest.embedder import embed_chunks
from rag.ingest.loader import load_sources, missing_sources
from rag.ingest.parsers import parse_source
from rag.kb_store import KnowledgeBaseStore


def _delete_stale_points(store: KnowledgeBaseStore, source: str) -> None:
    """Chunk ids shift when a source file changes; drop its old points first."""
    store.client.delete(
        collection_name=store.settings.collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[models.FieldCondition(key="source", match=models.MatchValue(value=source))]
            )
        ),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Ingest hospital documents into the RAG KB.")
    parser.add_argument("--recreate", action="store_true", help="drop and rebuild the collection")
    parser.add_argument("--limit-source", help="only ingest files whose name contains this text")
    args = parser.parse_args()

    settings = get_settings()
    for name in missing_sources(settings.data_dir):
        print(f"WARNING: missing data file, skipping: {name}")

    sources = load_sources(settings.data_dir)
    if args.limit_source:
        sources = [s for s in sources if args.limit_source in s["meta"]["source"]]
    if not sources:
        raise SystemExit("No data files found — check RAG_DATA_DIR")

    store = KnowledgeBaseStore(settings)
    try:
        store.ensure_collection(recreate=args.recreate)
        total = 0
        for src in sources:
            chunks = finalize_chunks(parse_source(src["text"], src["meta"]), src["meta"])
            points = embed_chunks(chunks, settings)
            if not args.recreate:
                _delete_stale_points(store, src["meta"]["source"])
            store.upsert(points)
            total += len(points)
            print(f"  {src['meta']['source']}: {len(points)} points")
        count = store.client.count(settings.collection).count
        print(f"Done: upserted {total} points; collection '{settings.collection}' now has {count}.")
    finally:
        store.close()


if __name__ == "__main__":
    main()
