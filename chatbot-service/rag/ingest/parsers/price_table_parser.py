"""Parser for the two price list files (dual format).

- banggiaBHYT.txt: clean pipe tables `STT | ... | GIÁ | GHI CHÚ` under
  `=====` category headers.
- GiaDVBV_tim_HN.txt: PDF extract, ONE field per line, `--- Page N ---`
  markers; rows reconstructed via STT detection (approximate by design —
  ambiguous rows are skipped, callers can report `skipped` count).
"""

import logging
import re

CHUNK_CHAR_BUDGET = 1100  # keeps content (header + rows) under the 1200 cap

SEPARATOR_RE = re.compile(r"^={10,}\s*$")
PAGE_RE = re.compile(r"^--- Page \d+ ---\s*$")
PRICE_RE = re.compile(r"^\d{1,3}(\.\d{3})+\s*$")  # e.g. 58.600 / 1.234.500
STT_RE = re.compile(r"^\d{1,4}(,\d{1,2})?\s*$")  # e.g. 4 / 5,1
# Some pages put STT + service code on ONE line: "326  18.0173.0043 ..."
STT_CODE_RE = re.compile(r"^(\d{1,4}(?:,\d{1,2})?)\s+(\d{2}\.\d{4}\.\d{4}.*)$")
MAX_PRICES_PER_ROW = 6  # more = runaway accumulation, treat row as parse failure
# Page furniture in the PDF extract, repeated on every page.
FURNITURE_RE = re.compile(
    r"^(SỞ Y TẾ|BỆNH VIỆN TIM|VÌ MỘT TRÁI TIM|Ghi chú:|Bảng giá áp dụng"
    r"|Thành phố Hà Nội|MỤC LỤC|DANH MỤC|CHỈ MÀU|STT\s*$|DỊCH VỤ KỸ THUẬT\s*$"
    r"|DỊCH VỤ\s*$|CƠ SỞ \d|GHI CHÚ\s*$|ĐVT|Đơn vị tính|MÃ TƯƠNG\s*$|ĐƯƠNG\s*$)"
)
# Furniture that may appear BETWEEN a "BẢNG GIÁ..." line and its category text.
PRE_CATEGORY_SKIP_RE = re.compile(
    r"^(SỞ Y TẾ|BỆNH VIỆN TIM|VÌ MỘT TRÁI TIM|Ghi chú:|Bảng giá áp dụng|Thành phố Hà Nội)"
)


def _emit_batches(rows: list[str], category: str, meta: dict, header: str = "") -> list[dict]:
    """Batch rows by char budget so EVERY chunk carries its category header."""
    head = f"{category}\n{header}".strip()
    partials, batch, size = [], [], len(head)

    def flush_batch() -> None:
        nonlocal batch, size
        if batch:
            partials.append(
                {
                    "content": f"{head}\n" + "\n".join(batch) if head else "\n".join(batch),
                    "title": f"{meta['title']} — {category}" if category else meta["title"],
                    "category": category or None,
                }
            )
        batch, size = [], len(head)

    for row in rows:
        if batch and size + len(row) + 1 > CHUNK_CHAR_BUDGET:
            flush_batch()
        batch.append(row)
        size += len(row) + 1
    flush_batch()
    return partials


def _parse_pipe_format(text: str, meta: dict) -> list[dict]:
    """banggiaBHYT branch: category from `=====` headers, rows are pipe lines."""
    partials: list[dict] = []
    category, header, rows = "", "", []
    prev_was_separator = False
    for line in text.splitlines():
        line = line.rstrip()
        if SEPARATOR_RE.match(line):
            prev_was_separator = not prev_was_separator
            continue
        if prev_was_separator and line.strip() and "|" not in line:
            # Line between two ===== separators = new category title.
            partials += _emit_batches(rows, category, meta, header)
            category, header, rows = line.strip(), "", []
            continue
        if "|" in line:
            if line.strip().upper().startswith("STT"):
                header = line.strip()
            else:
                rows.append(line.strip())
    partials += _emit_batches(rows, category, meta, header)
    return partials


def _flush_row(stt: str, name_parts: list[str], prices: list[str], notes: list[str]) -> str | None:
    name = " ".join(p.strip() for p in name_parts if p.strip())
    if not name or not prices or len(prices) > MAX_PRICES_PER_ROW:
        return None  # ambiguous/runaway row → skip, counted by caller
    row = f"{stt}. {name} — Giá: {' / '.join(prices)}"
    note = " ".join(n.strip() for n in notes if n.strip())
    return f"{row} — {note}" if note else row


def _parse_pdf_format(text: str, meta: dict) -> list[dict]:
    """GiaDVBV branch: reconstruct rows from one-field-per-line PDF extract."""
    partials: list[dict] = []
    category, rows = "", []
    stt, name_parts, prices, notes = "", [], [], []
    skipped = 0
    in_row = False
    expecting_category = False

    lines = text.splitlines()
    # Pages 1-2 are cover + table of contents: skip to page 3.
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("--- Page 3 ---"))
    except StopIteration:
        start = 0

    def close_row() -> None:
        nonlocal stt, name_parts, prices, notes, in_row, skipped
        if in_row:
            row = _flush_row(stt, name_parts, prices, notes)
            if row:
                rows.append(row)
            else:
                skipped += 1
        stt, name_parts, prices, notes, in_row = "", [], [], [], False

    for raw in lines[start:]:
        line = raw.strip()
        if not line or PAGE_RE.match(raw):
            continue
        # "BẢNG GIÁ DỊCH VỤ KỸ THUẬT..." announces a category on following line(s).
        if line.startswith("BẢNG GIÁ"):
            close_row()
            partials += _emit_batches(rows, category, meta)
            rows, category, expecting_category = [], "", True
            continue
        if expecting_category:
            if PRE_CATEGORY_SKIP_RE.match(line):
                continue  # page furniture between "BẢNG GIÁ" and its category text
            if STT_RE.match(line) or STT_CODE_RE.match(line) or PRICE_RE.match(line) or FURNITURE_RE.match(line):
                expecting_category = False  # category header ended
            elif len(category) < 120:
                category = f"{category} {line}".strip()
                continue
            else:
                expecting_category = False
        if FURNITURE_RE.match(line):
            continue
        if STT_RE.match(line):
            close_row()
            stt, in_row = line.replace(" ", ""), True
        elif m := STT_CODE_RE.match(line):
            close_row()
            stt, in_row = m.group(1), True
            name_parts.append(m.group(2))
        elif PRICE_RE.match(line):
            if in_row and line not in prices:  # CS1/CS2 duplicates collapse
                prices.append(line)
        elif in_row:
            (notes if prices else name_parts).append(line)
    close_row()
    partials += _emit_batches(rows, category, meta)
    if skipped:
        # Approximate parsing is expected for PDF extracts; surface the count.
        logging.getLogger(__name__).info(
            "price_table_parser: skipped %d ambiguous rows in %s", skipped, meta["source"]
        )
    return partials


def parse_price_table(text: str, meta: dict) -> list[dict]:
    if " | " in text:
        return _parse_pipe_format(text, meta)
    return _parse_pdf_format(text, meta)
