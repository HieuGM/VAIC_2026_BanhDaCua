"""Finalize parser output into payload-ready chunks (schema in rag/kb_store.py).

Responsibilities: merge base metadata, stable chunk_id (idempotent re-ingest),
snippet, integer date fields for Qdrant range filters, hard length cap with
newline-aware splitting (never silently truncate).
"""

import hashlib

MIN_CONTENT_CHARS = 20
MAX_CONTENT_CHARS = 1200
SNIPPET_CHARS = 160


def _chunk_id(source: str, ordinal: int, content: str) -> str:
    raw = f"{source}:{ordinal}:{content[:64]}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _date_to_int(iso_date: str | None) -> int | None:
    """'2026-07-19' -> 20260719 (Qdrant-filterable). None passes through."""
    if not iso_date:
        return None
    return int(iso_date.replace("-", ""))


def _split_long(content: str) -> list[str]:
    """Split content over the cap at newline boundaries; keep pieces coherent."""
    if len(content) <= MAX_CONTENT_CHARS:
        return [content]
    pieces, current = [], ""
    for line in content.splitlines():
        # A single line over the cap (parser anomaly) is hard-wrapped so no
        # chunk can ever exceed the cap.
        while len(line) > MAX_CONTENT_CHARS:
            if current:
                pieces.append(current)
                current = ""
            pieces.append(line[:MAX_CONTENT_CHARS])
            line = line[MAX_CONTENT_CHARS:]
        if current and len(current) + len(line) + 1 > MAX_CONTENT_CHARS:
            pieces.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        pieces.append(current)
    return pieces


def finalize_chunks(partials: list[dict], base_meta: dict) -> list[dict]:
    """Merge base_meta into parser partials and enforce the payload schema.

    Parser fields (content/title/category) win over base_meta defaults.
    """
    chunks = []
    ordinal = 0
    for partial in partials:
        content = (partial.get("content") or "").strip()
        if len(content) < MIN_CONTENT_CHARS:
            continue
        for piece in _split_long(content):
            merged = {**base_meta, **{k: v for k, v in partial.items() if v is not None}}
            chunks.append(
                {
                    "chunk_id": _chunk_id(base_meta["source"], ordinal, piece),
                    "title": merged.get("title") or base_meta["source"],
                    "source": base_meta["source"],
                    "source_type": base_meta["source_type"],
                    "content": piece,
                    "snippet": piece[:SNIPPET_CHARS],
                    "approved": bool(merged.get("approved", True)),
                    "deprecated": bool(merged.get("deprecated", False)),
                    "effective_from": merged.get("effective_from"),
                    "effective_to": merged.get("effective_to"),
                    "eff_from_int": _date_to_int(merged.get("effective_from")),
                    "eff_to_int": _date_to_int(merged.get("effective_to")),
                    "updated_at": merged.get("updated_at"),
                    "document_code": merged.get("document_code"),
                    "url": merged.get("url"),
                    "category": merged.get("category"),
                }
            )
            ordinal += 1
    return chunks
