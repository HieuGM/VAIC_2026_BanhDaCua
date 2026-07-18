"""Parser for the doctor schedule file.

Structure: `# PHẦN X: <facility>` blocks → `TUẦN n: ...` week headers (between
===== separators) → `--- KHU ... ---` sections → `Phòng khám số N | hours`
room blocks with per-day lines. One chunk per room per week keeps citations
precise ("which room, which week says doctor X").

effective_from/effective_to come from the file registry and are attached to
every chunk by finalize_chunks (query-time expiry filter relies on them).
"""

import re

HASH_BLOCK_RE = re.compile(r"^#{10,}\s*$")
FACILITY_RE = re.compile(r"^#\s+(.+?)\s*$")
SEPARATOR_RE = re.compile(r"^={10,}\s*$")
WEEK_RE = re.compile(r"^TUẦN\s+\d+.*$", re.IGNORECASE)
SECTION_RE = re.compile(r"^---\s*(.+?)\s*---\s*$")
# Match on the "name | HH.MM - HH.MM" time-slot shape, not the room name prefix:
# PHẦN C rooms are specialty-named ("RHM (P401)", "MẮT (P405.D)", ...).
ROOM_RE = re.compile(r"^([^|]+?)\s*\|\s*(\d{1,2}[.:]\d{2}\s*-\s*\d{1,2}[.:]\d{2})\s*$")


def parse_schedule(text: str, meta: dict) -> list[dict]:
    partials: list[dict] = []
    facility_lines: list[str] = []
    in_facility_block = False
    facility = week = section = ""
    room_header = ""
    day_lines: list[str] = []

    def flush_room() -> None:
        nonlocal room_header, day_lines
        if room_header and day_lines:
            header = " | ".join(x for x in (facility, week, section) if x)
            content = f"{header}\n{room_header}\n" + "\n".join(day_lines)
            partials.append(
                {
                    "content": content,
                    "title": f"{room_header.split('|')[0].strip()} — {section or facility}",
                    "category": section or facility or None,
                }
            )
        room_header, day_lines = "", []

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if HASH_BLOCK_RE.match(stripped):
            flush_room()
            # Toggle facility header block (#### ... # PHẦN X ... ####).
            in_facility_block = not in_facility_block
            if in_facility_block:
                facility_lines = []
            else:
                facility = " ".join(facility_lines)
                week = section = ""
            continue
        if in_facility_block:
            m = FACILITY_RE.match(stripped)
            if m:
                facility_lines.append(m.group(1))
            continue

        if SEPARATOR_RE.match(stripped):
            continue
        if WEEK_RE.match(stripped):
            flush_room()
            week = stripped
            continue
        m = SECTION_RE.match(stripped)
        if m:
            flush_room()
            section = m.group(1)
            continue
        m = ROOM_RE.match(stripped)
        if m:
            flush_room()
            room_header = stripped
            continue
        if room_header and stripped:
            day_lines.append(stripped)
        # Preamble lines (hotline, website) are covered by the booking guide
        # document; skipping them here avoids duplicate evidence.

    flush_room()
    return partials
