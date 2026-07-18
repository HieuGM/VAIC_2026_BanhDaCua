"""Parser for the SOP procedure QT.25.01 (Quy trình đón tiếp bệnh nhân).

Structure: an administrative header, then roman sections (I.–VI.) with numbered
subsections (4.1, 5.1, ...), delimited by `=====` separators. A heading is a
roman/numbered-prefixed SHORT label that does NOT end in a period — this keeps
real section titles ("I. MỤC ĐÍCH:", "5.1. Sơ đồ ...:") as boundaries while
leaving numbered body sentences ("1. Người có liên quan ... quy định này.") as
content.
"""

import re

from rag.ingest.parsers.heading_sections import group_long_body, split_into_sections

_SEPARATOR_RE = re.compile(r"^={5,}\s*$")
_SOP_HEADING_RE = re.compile(r"^([IVXLC]+|\d+(?:\.\d+)*)\.?\s+\S")


def _is_heading(line: str) -> bool:
    s = line.strip()
    if len(s) > 100 or s.endswith("."):  # numbered body sentences end with '.'
        return False
    return bool(_SOP_HEADING_RE.match(s))


def parse_sop(text: str, meta: dict) -> list[dict]:
    # Drop separator lines so they don't land inside chunk bodies.
    cleaned = "\n".join(l for l in text.splitlines() if not _SEPARATOR_RE.match(l))
    partials = []
    for heading, body in split_into_sections(cleaned, _is_heading, min_section_chars=150):
        for piece in group_long_body(body):
            content = f"{heading}\n{piece}" if heading else piece
            partials.append({
                "content": content,
                "title": meta["title"],
                "category": heading or None,
            })
    return partials
