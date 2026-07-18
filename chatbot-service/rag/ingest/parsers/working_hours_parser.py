"""Parser for working-hours.md — a markdown doc (## / ### headings + tables).

Splits on markdown headings into one chunk per section (reusing heading_sections
so a heading never stands alone and tiny sections merge into a neighbour), then
caps over-long bodies on paragraph boundaries. The heading is prefixed to its
body for retrieval context.
"""

import re

from rag.ingest.parsers.heading_sections import group_long_body, split_into_sections

_MD_HEADING_RE = re.compile(r"^#{1,6}\s+\S")


def _clean_heading(heading: str) -> str:
    # Drop leading '#' markers; keep the accumulated "H1 — H2" path readable.
    return re.sub(r"#+\s*", "", heading).strip()


def parse_working_hours(text: str, meta: dict) -> list[dict]:
    partials = []
    for heading, body in split_into_sections(
        text, lambda line: bool(_MD_HEADING_RE.match(line))
    ):
        clean = _clean_heading(heading)
        for piece in group_long_body(body):
            head = f"{clean}\n" if clean else ""
            # Strip any markdown heading markers left in the body — short sections
            # get folded into a neighbour by split_into_sections, carrying their
            # '##' prefix into the text.
            content = re.sub(r"(?m)^#{1,6}\s+", "", f"{head}{piece}")
            partials.append({
                "content": content,
                "title": clean or meta["title"],
            })
    return partials
