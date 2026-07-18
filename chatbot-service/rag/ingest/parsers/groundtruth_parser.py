"""Parser for the hospital-intro groundtruth file.

Structure: roman sections (I.–XI.) delimited by `=====`, each containing atomic
`[FACT_xxx]` / `[SOURCE_xx]` / `[EVENT_xxx]` blocks (blank-line separated, with
"Chủ đề: / Giá trị: / Nguồn:" fields). Each block is a natural, self-contained
chunk → 1 chunk per block, prefixed with its roman section heading for context.
The block's bracket id becomes the category (used for citation + eval gold).

The file ends with meta sections (XII–XV: do-not-use data, Q&A eval samples,
chatbot rules, JSON/CSV notes) that must NOT be retrievable — truncated here.
"""

import re

SEPARATOR_RE = re.compile(r"^={10,}\s*$")
BLOCK_ID_RE = re.compile(r"^\[([A-Z]+(?:_[A-Z0-9]+)+)\]\s*$")
_ROMAN_HEADING_RE = re.compile(r"^\s*[IVXLC]+\.\s")
_META_TAIL_MARKERS = (
    "DỮ LIỆU KHÔNG NÊN DÙNG",
    "MẪU GROUNDTRUTH",
    "QUY TẮC SỬ DỤNG",
    "CẤU TRÚC GỢI Ý",
)


def _strip_meta_tail(text: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if _ROMAN_HEADING_RE.match(line) and any(m in line for m in _META_TAIL_MARKERS):
            return "\n".join(lines[:i])
    return text


def parse_groundtruth(text: str, meta: dict) -> list[dict]:
    partials: list[dict] = []
    section = ""  # current roman section heading (context)
    block_id = ""
    block_lines: list[str] = []
    prev_was_sep = False

    def flush_block() -> None:
        nonlocal block_id, block_lines
        content = "\n".join(block_lines).strip()
        if block_id and content:
            head = f"{section}\n" if section else ""
            partials.append({
                "content": f"{head}[{block_id}]\n{content}",
                "title": meta["title"],
                "category": f"[{block_id}]",  # bracket id → citation + eval gold
            })
        block_id, block_lines = "", []

    for raw in _strip_meta_tail(text).splitlines():
        line = raw.rstrip()
        if SEPARATOR_RE.match(line):
            prev_was_sep = not prev_was_sep
            continue
        # A roman heading sits alone between two ===== separators.
        if prev_was_sep and _ROMAN_HEADING_RE.match(line):
            flush_block()
            section = line.strip()
            continue
        m = BLOCK_ID_RE.match(line)
        if m:
            flush_block()
            block_id = m.group(1)
        elif block_id:
            block_lines.append(line)
    flush_block()
    return partials
