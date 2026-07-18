"""Parsers for the crawled JSON seed data (data/seed/crawled/*.json).

Four record types, one JSON array each. Each parser turns the array into
self-contained Vietnamese chunks; the per-type formatter decides grouping +
wording:
  - doctors    : grouped by department (repeated people deduped) — 72 short,
                 near-duplicate records would otherwise pollute retrieval.
  - departments: one chunk per department (each description is distinct).
  - bhyt_policy: one chunk per policy; a non-"high" confidence keeps its caveat
                 in the text so the answer reflects the uncertainty (never
                 silently assert an inferred fact).
  - channels   : grouped by channel type (each record is tiny).

Per-record sourceUrl becomes the chunk url (citation); code/type becomes the
category. chunker.finalize_chunks() then enforces the payload schema.
"""

import json
from collections import OrderedDict


def _records(text: str) -> list[dict]:
    data = json.loads(text)
    return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []


# --- doctors: group by department, dedupe repeated (name, department, bio) ---

def parse_doctors(text: str, meta: dict) -> list[dict]:
    groups: "OrderedDict[str, list[dict]]" = OrderedDict()
    seen: set[tuple] = set()
    for d in _records(text):
        name = (d.get("fullName") or "").strip()
        dept = (d.get("department") or "Chưa rõ khoa").strip()
        key = (name, dept, (d.get("bio") or "").strip())
        if not name or key in seen:
            continue
        seen.add(key)
        groups.setdefault(dept, []).append(d)

    partials = []
    for dept, docs in groups.items():
        lines = [f"Danh sách bác sĩ - {dept}:"] + [_doctor_line(d) for d in docs]
        partials.append({
            "content": "\n".join(lines),
            "title": f"Bác sĩ - {dept}",
            "category": dept,
        })
    return partials


def _doctor_line(d: dict) -> str:
    label = " ".join(p for p in (d.get("degree"), d.get("fullName")) if p)
    extra = []
    if d.get("title"):
        extra.append(d["title"])
    if d.get("specialty"):
        extra.append(f"chuyên khoa {d['specialty']}")
    tail = f" ({', '.join(extra)})" if extra else ""
    bio = f" {d['bio'].strip()}" if d.get("bio") else ""
    return f"- {label}{tail}.{bio}"


# --- departments: one chunk per substantive department; thin administrative
# units (e.g. "Phòng chức năng.") are grouped so no bare-heading orphan chunk
# ranks #1 with no substance (see tests/test_rag_parsers::no_orphan). ---

_DEPT_MIN_CHARS = 80


def parse_departments(text: str, meta: dict) -> list[dict]:
    individual, thin = [], []
    for d in _records(text):
        name = (d.get("name") or "").strip()
        if not name:
            continue
        desc = (d.get("description") or "").strip()
        lines = [f"{name} — Bệnh viện Tim Hà Nội.", desc]
        if d.get("floor"):
            lines.append(f"Vị trí: {d['floor']}.")
        if d.get("workingHours"):
            lines.append(f"Giờ làm việc: {d['workingHours']}.")
        if d.get("phone"):
            lines.append(f"Điện thoại: {d['phone']}.")
        content = "\n".join(x for x in lines if x)
        if len(content) >= _DEPT_MIN_CHARS:
            individual.append({
                "content": content, "title": name,
                "category": d.get("code"), "url": d.get("sourceUrl"),
            })
        else:
            thin.append(f"- {name}: {desc}" if desc else f"- {name}")

    if thin:
        individual.append({
            "content": "Các đơn vị/phòng ban khác của Bệnh viện Tim Hà Nội:\n"
            + "\n".join(thin),
            "title": "Các đơn vị/phòng ban khác - Bệnh viện Tim Hà Nội",
        })
    return individual


# --- bhyt policies: one chunk per policy, keep low-confidence caveat ---

def parse_bhyt_policy(text: str, meta: dict) -> list[dict]:
    partials = []
    for p in _records(text):
        title = (p.get("title") or "").strip()
        body = "\n".join(b.strip() for b in (p.get("summary"), p.get("detailsMd")) if b)
        content = f"{title}\n{body}" if title else body
        conf = p.get("confidence")
        if conf and conf != "high":
            content += f"\n(Độ tin cậy: {conf} — cần đối chiếu văn bản chính thức của bệnh viện.)"
        partials.append({
            "content": content,
            "title": title or meta["title"],
            "category": p.get("code"),
            "url": p.get("sourceUrl"),
        })
    return partials


# --- channels: group by channel type ---

_CHANNEL_LABELS = {
    "hotline": "Hotline/Điện thoại", "web": "Website đặt lịch",
    "zalo": "Zalo", "fanpage": "Mạng xã hội", "email": "Email",
}


def parse_channels(text: str, meta: dict) -> list[dict]:
    groups: "OrderedDict[str, list[dict]]" = OrderedDict()
    for c in _records(text):
        groups.setdefault((c.get("channelType") or "khác").strip(), []).append(c)

    partials = []
    for ctype, items in groups.items():
        head = _CHANNEL_LABELS.get(ctype, ctype)
        lines = [f"Kênh liên hệ Bệnh viện Tim Hà Nội - {head}:"]
        for c in items:
            contact = c.get("phone") or c.get("url") or ""
            note = f" — {c['notes'].strip()}" if c.get("notes") else ""
            lines.append(f"- {(c.get('label') or '').strip()}: {contact}{note}")
        partials.append({
            "content": "\n".join(lines),
            "title": f"Liên hệ - {head}",
            "category": ctype,
        })
    return partials
