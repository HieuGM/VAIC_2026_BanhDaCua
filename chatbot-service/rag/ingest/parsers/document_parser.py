"""Parser for free-text documents (gioi thieu, huong dan dat lich, quy trinh SOP).

Strategy: split on separator lines (=====...), detect UPPERCASE heading lines
as sub-section starts, then group paragraphs into ~TARGET-char sections so each
chunk stays citation-friendly. Section heading is prepended to the content.
"""

import re

SEPARATOR_RE = re.compile(r"^={10,}\s*$")
TARGET_CHARS = 900  # soft target per chunk; finalize_chunks enforces hard cap

# A heading = short line, no ending punctuation, mostly uppercase Vietnamese.
_LOWER_RE = re.compile(r"[a-zàáâãăằắẵặẳầấẫậẩèéêẽềếễệểìíĩỉòóôõơồốỗộổờớỡợởùúũụưừứữựửỳýỵỹỷđ]")


def _is_heading(line: str) -> bool:
    text = line.strip()
    if not (4 <= len(text) <= 90) or text.endswith((".", ":", ",", ";")):
        return False
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 4:
        return False
    return len(_LOWER_RE.findall(text)) <= len(letters) * 0.15


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Return [(heading, body)] using separator lines + uppercase headings."""
    sections: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []

    def flush() -> None:
        nonlocal body, heading
        content = "\n".join(body).strip()
        if content:
            sections.append((heading, content))
        body = []

    for line in text.splitlines():
        if SEPARATOR_RE.match(line):
            # Sandwiched headings (=====\nTITLE\n=====\nbody) must survive the
            # second separator: only reset when a body was actually flushed.
            had_body = bool("\n".join(body).strip())
            flush()
            if had_body:
                heading = ""
        elif _is_heading(line) and not body:
            heading = f"{heading} {line.strip()}".strip() if heading else line.strip()
        elif _is_heading(line) and body:
            flush()
            heading = line.strip()
        elif line.strip() or body:
            # Leading blank lines are not "body": they would break heading
            # merging for `=====\nTITLE\n=====\n\n[SUBHEADING]` layouts.
            body.append(line.rstrip())
    flush()
    return sections


def _group_paragraphs(body: str) -> list[str]:
    """Split an over-long section body into ~TARGET_CHARS pieces on blank lines."""
    if len(body) <= TARGET_CHARS:
        return [body]
    pieces, current = [], ""
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if current and len(current) + len(para) > TARGET_CHARS:
            pieces.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        pieces.append(current)
    return pieces


def parse_document(text: str, meta: dict) -> list[dict]:
    partials = []
    for heading, body in _split_sections(text):
        for piece in _group_paragraphs(body):
            content = f"{heading}\n{piece}" if heading else piece
            partials.append(
                {
                    "content": content,
                    # Keep the document title; heading becomes the category.
                    "title": meta["title"],
                    "category": heading or None,
                }
            )
    return partials
