"""Parser for the booking guide (Hướng dẫn đặt lịch khám): title + headings +
paragraphs/contact blocks. Heading = short standalone label (no sentence
punctuation, not a key:value/list line), so the leading title buffers with its
section instead of becoming an orphan chunk."""

from rag.ingest.parsers.heading_sections import group_long_body, split_into_sections


def _is_heading(line: str) -> bool:
    s = line.strip()
    if not (3 <= len(s) <= 80):
        return False
    if s[-1] in ".:,;":  # sentences / key:value end this way
        return False
    if s[0] in "-•*–" or s[0].isdigit():  # list item
        return False
    if ":" in s:  # "Địa chỉ: ...", "Website: ..." are data, not headings
        return False
    return True


def parse_booking_guide(text: str, meta: dict) -> list[dict]:
    partials = []
    for heading, body in split_into_sections(text, _is_heading, min_section_chars=120):
        for piece in group_long_body(body):
            content = f"{heading}\n{piece}" if heading else piece
            partials.append({
                "content": content,
                "title": meta["title"],
                "category": heading or None,
            })
    return partials
