"""Parser dispatch: source_type -> parser.

Each parser takes (text, base_meta) and returns partial chunks:
dicts with at least "content", optionally "title" / "category" overrides.
chunker.finalize_chunks() merges base_meta and enforces the payload schema.
"""

from rag.ingest.parsers.document_parser import parse_document
from rag.ingest.parsers.price_table_parser import parse_price_table
from rag.ingest.parsers.schedule_parser import parse_schedule

_PARSERS = {
    "document": parse_document,
    "price_table": parse_price_table,
    "schedule": parse_schedule,
}


def parse_source(text: str, meta: dict) -> list[dict]:
    parser = _PARSERS.get(meta["source_type"])
    if parser is None:
        raise ValueError(f"No parser for source_type={meta['source_type']!r}")
    return parser(text, meta)
