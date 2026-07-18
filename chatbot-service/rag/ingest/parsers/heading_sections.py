"""Shared heading-based section splitting for prose documents (booking + SOP).

Principles (per data-owner guidance):
- Never emit a chunk that is only a heading/title — headings are BUFFERED and
  only flushed together with real body content.
- Merge a too-short section into an adjacent one so tiny fragments don't become
  low-weight standalone chunks.
"""

import re
from typing import Callable

TARGET_CHARS = 1000  # soft target; we have token headroom (bge-m3 max ~501/512)


def split_into_sections(
    text: str, is_heading: Callable[[str], bool], min_section_chars: int = 120
) -> list[tuple[str, str]]:
    """Return [(heading, body)]. Consecutive headings with no body between them
    accumulate into one heading path, so a heading never stands alone."""
    sections: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []

    def flush() -> None:
        nonlocal heading, body
        content = "\n".join(body).strip()
        if content:
            sections.append((heading, content))
        body = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if is_heading(line):
            if "\n".join(body).strip():  # heading after a real body → new section
                flush()
                heading = line.strip()
            else:  # heading with no body yet → accumulate (never emit alone)
                heading = f"{heading} — {line.strip()}".strip(" —") if heading else line.strip()
        elif line.strip() or body:
            body.append(line)
    flush()
    return _merge_short(sections, min_section_chars)


def _merge_short(sections: list[tuple[str, str]], min_chars: int) -> list[tuple[str, str]]:
    """Fold a section whose body is thinner than min_chars into a neighbour."""
    merged: list[tuple[str, str]] = []
    for heading, body in sections:
        if merged and len(body) < min_chars:
            ph, pb = merged[-1]
            extra = f"{heading}\n{body}" if heading else body
            merged[-1] = (ph, f"{pb}\n{extra}".strip())
        else:
            merged.append((heading, body))
    # A short FIRST section has no previous to merge into → merge forward.
    if len(merged) >= 2 and len(merged[0][1]) < min_chars:
        (h0, b0), (h1, b1) = merged[0], merged[1]
        prefix = f"{h0}\n{b0}" if h0 else b0
        merged[1] = (h1, f"{prefix}\n{b1}".strip())
        merged.pop(0)
    return merged


def group_long_body(body: str, target: int = TARGET_CHARS) -> list[str]:
    """Split an over-long body on blank-line (paragraph) boundaries — never
    mid-paragraph — so an idea isn't cut in half."""
    if len(body) <= target:
        return [body]
    pieces, current = [], ""
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if current and len(current) + len(para) > target:
            pieces.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        pieces.append(current)
    return pieces
