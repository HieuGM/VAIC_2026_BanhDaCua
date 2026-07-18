"""Per-file parser dispatch.

Each data file has its own structure, so each has a dedicated parser (keyed by
`meta["parser"]` from the loader registry). Each parser takes (text, base_meta)
and returns partial chunks (dicts with at least "content", optionally "title" /
"category" overrides). chunker.finalize_chunks() then enforces the payload schema.
"""

from rag.ingest.parsers.booking_guide_parser import parse_booking_guide
from rag.ingest.parsers.crawled_json_parser import (
    parse_bhyt_policy,
    parse_channels,
    parse_departments,
    parse_doctors,
)
from rag.ingest.parsers.groundtruth_parser import parse_groundtruth
from rag.ingest.parsers.price_table_parser import parse_price_table
from rag.ingest.parsers.schedule_parser import parse_schedule
from rag.ingest.parsers.sop_parser import parse_sop
from rag.ingest.parsers.working_hours_parser import parse_working_hours

_PARSERS = {
    "groundtruth": parse_groundtruth,
    "booking_guide": parse_booking_guide,
    "sop": parse_sop,
    "price_table": parse_price_table,
    "schedule": parse_schedule,
    # Crawled seed data (data/seed/crawled/*)
    "doctors": parse_doctors,
    "departments": parse_departments,
    "bhyt_policy": parse_bhyt_policy,
    "channels": parse_channels,
    "working_hours": parse_working_hours,
}


def parse_source(text: str, meta: dict) -> list[dict]:
    parser = _PARSERS.get(meta.get("parser") or meta["source_type"])
    if parser is None:
        raise ValueError(f"No parser for {meta.get('parser') or meta['source_type']!r}")
    return parser(text, meta)
