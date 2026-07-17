#!/usr/bin/env python3
"""
parse-schedule.py — Parse data/raw/Lich_kham_benh_29.6-19.7.2026.txt and emit
SQL seed (V4) for doctor_schedules only. Departments and doctors are sourced
from crawled JSON (see seed-crawled.py). Doctor FK is resolved by normalized
name → code (crawled). Unknown schedule-only doctors are inserted first into
the doctors table via a sibling migration (V3__seed_doctors.sql includes them).

Output: data-api/src/main/resources/db/migration/V4__seed_doctor_schedules.sql
"""
from __future__ import annotations
import json
import re
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "data" / "raw" / "Lich_kham_benh_29.6-19.7.2026.txt"
CRAWLED_DOCS = REPO / "data" / "seed" / "crawled" / "doctors.json"
OUT = (REPO / "data-api" / "src" / "main" / "resources" / "db" / "migration"
       / "V4__seed_doctor_schedules.sql")

# Map schedule-derived dept codes (granular exam-areas) → crawled canonical codes.
SCHEDULE_DEPT_MAP = {
    "KBTN1_CS1": "kham-benh-tu-nguyen-1",
    "KBTN3_CS1": "kham-benh-tu-nguyen-3",
    "KHTN_CS2":  "kham-benh-tu-nguyen",
    "RHM_CS2":   "phong-kham-da-khoa-cs2",
    "PHCN_CS2":  "phong-kham-da-khoa-cs2",
    "TMH_CS2":   "phong-kham-da-khoa-cs2",
    "PK_NHI_CS2":"phong-kham-da-khoa-cs2",
    "DA_LIEU_CS2":"phong-kham-da-khoa-cs2",
    "SAN_CS2":   "phong-kham-da-khoa-cs2",
    "YHCT_CS2":  "phong-kham-da-khoa-cs2",
    "NOI_HH_CS2":"phong-kham-da-khoa-cs2",
    "NOI_CXK_CS2":"phong-kham-da-khoa-cs2",
    "NTM_NT_CS2":"phong-kham-da-khoa-cs2",
    "MAT_CS2":   "phong-kham-da-khoa-cs2",
}

DEGREE_PATTERNS = [
    ("TS.BS",    re.compile(r"^TS\.?BS\.?(?=\s|$)", re.IGNORECASE)),
    ("ThS.BS",   re.compile(r"^ThS\.?BS\.?(?=\s|$)", re.IGNORECASE)),
    ("BSCKII",   re.compile(r"^BS\.?\s*CK\.?\s*II\.?(?=\s|$)", re.IGNORECASE)),
    ("BSCKI",    re.compile(r"^BS\.?\s*CK\.?\s*I\.?(?=\s|$)", re.IGNORECASE)),
    ("BSNT",     re.compile(r"^BS\.?NT\.?(?=\s|$)", re.IGNORECASE)),
    ("BS",       re.compile(r"^BS\.?(?=\s|$)", re.IGNORECASE)),
]
NOISE_NAMES = {"TC", "TMCH", "HC", "PK4", "TĂNG CƯỜNG", "HC.",
               "(TRỐNG)", "(KHÔNG CÓ LỊCH)", "(KHÔNG RÕ)", "N/A", ""}
SPECIALTY_MAP = [
    ("RHM",            "RHM_CS2"),
    ("PHCN",           "PHCN_CS2"),
    ("TMH",            "TMH_CS2"),
    ("PK NHI",         "PK_NHI_CS2"),
    ("DA LIỄU",        "DA_LIEU_CS2"),
    ("SẢN",            "SAN_CS2"),
    ("YHCT",           "YHCT_CS2"),
    ("Nội chung - Hô Hấp", "NOI_HH_CS2"),
    ("Nội chung - CXK",    "NOI_CXK_CS2"),
    ("PK NTM - NT",        "NTM_NT_CS2"),
    ("MẮT",           "MAT_CS2"),
]


def slugify(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    a = "".join(c for c in nfkd if not unicodedata.combining(c))
    a = a.lower()
    a = re.sub(r"[^a-z0-9]+", "-", a).strip("-")
    return a or "x"


def normalize_name(s: str) -> str:
    """Lowercased, no-diacritic, single-spaced key for fuzzy matching."""
    nfkd = unicodedata.normalize("NFKD", s)
    a = "".join(c for c in nfkd if not unicodedata.combining(c))
    a = a.lower()
    a = re.sub(r"[^a-z0-9]+", " ", a).strip()
    a = re.sub(r"\s+", " ", a)
    return a


def strip_annotations(s: str) -> str:
    s = re.sub(r"\([^)]*\)", "", s)
    s = s.strip().strip("/").strip()
    return re.sub(r"\s+", " ", s).strip()


def has_min_word_chars(s: str, min_chars: int = 4) -> bool:
    words = re.findall(r"[A-Za-zÀ-ỹ]+", s)
    if len(words) < 2:
        return False
    return sum(len(w) for w in words) >= min_chars


def parse_degree(cell: str) -> tuple[str, str]:
    cell = cell.strip().strip(".").strip()
    for canon, pat in DEGREE_PATTERNS:
        m = pat.match(cell)
        if m:
            name = re.sub(r"\s+", " ", cell[m.end():].strip().strip(".").strip())
            return canon, name
    return "", re.sub(r"\s+", " ", cell).strip()


def parse_time_range(s: str) -> tuple[str, str]:
    m = re.search(r"(\d{1,2})[.:](\d{2})\s*-\s*(\d{1,2})[.:](\d{2})", s)
    if not m:
        return "07:30:00", "16:30:00"
    h1, m1, h2, m2 = m.groups()
    return f"{int(h1):02d}:{m1}:00", f"{int(h2):02d}:{m2}:00"


def sql_escape(s) -> str:
    if s is None:
        return "NULL"
    s = str(s)
    if s == "":
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


# Load crawled doctor name → code map. The crawled JSON may not give an explicit
# code; we synthesize one from the slug so V3__seed_doctors.sql can emit the same.
CRAWLED_NAME_TO_SLUG: dict[str, str] = {}
if CRAWLED_DOCS.exists():
    for d in json.loads(CRAWLED_DOCS.read_text(encoding="utf-8")):
        key = normalize_name(d.get("fullName", ""))
        if key:
            CRAWLED_NAME_TO_SLUG.setdefault(key, slugify(d["fullName"]))
    # Seed a few extra aliases manually (crawled sometimes omits diacritics or has typos).
else:
    print("WARN: crawled/doctors.json not found; FK resolution will fall back to slug",
          file=sys.stderr)

EXTRA_DOCTORS: dict[str, dict] = {}  # slug -> {full_name, degree, dept_codes:set}


def resolve_doctor_code(degree: str, full_name: str, dept_code: str | None) -> str:
    name = strip_annotations(full_name)
    if not name or name.upper() in NOISE_NAMES:
        return ""
    if not has_min_word_chars(name, 4):
        return ""
    key = normalize_name(name)
    # Try crawled lookup first
    if key in CRAWLED_NAME_TO_SLUG:
        code = CRAWLED_NAME_TO_SLUG[key]
    else:
        code = slugify(name)
        if code not in EXTRA_DOCTORS:
            EXTRA_DOCTORS[code] = {
                "code": code, "full_name": name, "degree": degree,
                "dept_codes": set(), "source": "schedule-derived",
            }
        elif degree and not EXTRA_DOCTORS[code]["degree"]:
            EXTRA_DOCTORS[code]["degree"] = degree
    if dept_code:
        if code in EXTRA_DOCTORS:
            EXTRA_DOCTORS[code]["dept_codes"].add(dept_code)
    return code


schedules: list[dict] = []


def add_schedule(doctor_code: str, sched_dept_code: str | None, day_idx: int,
                 the_date: date | None, start: str, end: str,
                 shift: str, room: str | None):
    if not doctor_code:
        return
    schedules.append({
        "doctor_code": doctor_code,
        "dept_code": sched_dept_code,
        "day_of_week": day_idx + 1,
        "effective_date": the_date.isoformat() if the_date else None,
        "start_time": start, "end_time": end, "shift": shift, "room": room,
    })


def parse_cell(cell: str, day_idx: int, dept_code: str | None, room: str | None,
               start: str, end: str, the_date: date | None):
    cell = cell.strip()
    if not cell:
        return
    low = cell.lower()
    if low in ("nghỉ", "(nghỉ)", "nghi", "(trống)", "(trong)",
               "(không rõ)", "(không có lịch)"):
        return
    has_sang = bool(re.search(r"\bsáng\s*:", low))
    has_chieu = bool(re.search(r"\bchiều\s*:", low))
    if has_sang or has_chieu:
        parts = re.split(r"\s*/\s*", cell) if "/" in cell else [cell]
        for part in parts:
            plow = part.lower()
            shift = "morning" if re.search(r"\bsáng\s*:", plow) else (
                "afternoon" if re.search(r"\bchiều\s*:", plow) else None)
            if shift is None:
                continue
            part_clean = re.sub(r"\([^)]*nghỉ[^)]*\)", "", part, flags=re.IGNORECASE).strip()
            body = re.sub(r"^(sáng|chiều)\s*:\s*", "", part_clean, flags=re.IGNORECASE).strip()
            if not body or body.lower() == "nghỉ":
                continue
            body = re.sub(r"^(sat|khám tc|tc)\s*:\s*", "", body, flags=re.IGNORECASE).strip()
            if not body:
                continue
            m = re.search(r"(\d{1,2})[.:](\d{2})\s*-\s*(\d{1,2})[.:](\d{2})", body)
            if m:
                sh = f"{int(m.group(1)):02d}:{m.group(2)}:00"
                eh = f"{int(m.group(3)):02d}:{m.group(4)}:00"
                name = (body[:m.start()] + body[m.end():]).strip(" :-")
            else:
                sh = start if shift == "morning" else "13:00:00"
                eh = "12:00:00" if shift == "morning" else end
                name = body
            degree, fname = parse_degree(name)
            if not fname:
                continue
            dcode = resolve_doctor_code(degree, fname, dept_code)
            add_schedule(dcode, dept_code, day_idx, the_date, sh, eh, shift, room)
        return
    body = re.sub(r"^(sat|khám tc|tc)\s*:\s*", "", cell, flags=re.IGNORECASE).strip()
    if not body or body.lower() == "nghỉ":
        return
    degree, fname = parse_degree(body)
    if not fname:
        return
    dcode = resolve_doctor_code(degree, fname, dept_code)
    add_schedule(dcode, dept_code, day_idx, the_date, start, end, "fullday", room)


# ---------------------------------------------------------------- walk file
text = SRC.read_text(encoding="utf-8")
campus = None
campus_section = None
week_dates: list[date] = []
cur_area_code = None
cur_room: str | None = None
cur_time = ("07:30:00", "16:30:00")

for raw in text.splitlines():
    line = raw.rstrip()
    if not line.strip():
        continue
    up = line.upper()
    if "PHẦN A" in up and "CƠ SỞ 1" in up:
        campus = "CS1"; continue
    if "PHẦN B" in up and "CƠ SỞ 2" in up:
        campus = "CS2"; campus_section = "Khu TN"
        cur_area_code = "KHTN_CS2"; continue
    if "PHẦN C" in up and "CƠ SỞ 2" in up:
        campus = "CS2"; campus_section = "Chuyên khoa"
        cur_area_code = None; continue
    if up.startswith("TUẦN "):
        m = re.search(r"TỪ\s+NGÀY\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+ĐẾN(?:\s+NGÀY)?\s+(\d{1,2})/(\d{1,2})/(\d{4})", up)
        if m:
            d1 = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            week_dates = [d1 + timedelta(days=k) for k in range(7)]
        continue
    if line.strip().startswith("---") and "KHU KHÁM" in up:
        s = line.strip()
        if "1" in s and "3" not in s:
            cur_area_code = "KBTN1_CS1"
        elif "3" in s:
            cur_area_code = "KBTN3_CS1"
        continue
    if campus == "CS2" and campus_section == "Chuyên khoa":
        matched_sp = False
        for prefix, code in SPECIALTY_MAP:
            if line.strip().upper().startswith(prefix.upper()):
                cur_area_code = code
                cur_time = parse_time_range(line)
                m_room = re.search(r"P\d{3}(?:\.[A-Z])?", line)
                cur_room = m_room.group(0) if m_room else None
                matched_sp = True
                break
        if matched_sp:
            continue
    m_room = re.match(r"^\s*Phòng khám\s+(số\s+\d+|tăng cường\s+\d+\s*\([^)]+\))\s*\|\s*([0-9.\- ]+)", line)
    if m_room and cur_area_code:
        cur_room = re.sub(r"\s+", " ", m_room.group(1).strip())
        cur_time = parse_time_range(m_room.group(2))
        continue
    stripped = line.strip()
    mday = re.match(r"^(Thứ\s+[2-7]|CN|Chủ nhật)\s*\((\d{1,2})/(\d{1,2})\)\s*:\s*(.*)$", stripped)
    if mday and cur_area_code:
        tok = mday.group(1)
        idx_map = {"Thứ 2": 0, "Thứ 3": 1, "Thứ 4": 2, "Thứ 5": 3,
                   "Thứ 6": 4, "Thứ 7": 5, "CN": 6, "Chủ nhật": 6}
        day_idx = idx_map.get(tok)
        if day_idx is None:
            continue
        the_date = week_dates[day_idx] if day_idx < len(week_dates) else None
        parse_cell(mday.group(4), day_idx, cur_area_code, cur_room,
                   cur_time[0], cur_time[1], the_date)
        continue
    mrange = re.match(r"^(Thứ\s+[2-7]\s*-\s*Thứ\s+[2-7]|Thứ\s+[2-7],\s*CN|Thứ\s+[2-7]|CN|Chủ nhật)\s*:\s*(.*)$", stripped)
    if mrange and cur_area_code:
        tok = mrange.group(1)
        body = mrange.group(2)
        idx_map = {"Thứ 2": 1, "Thứ 3": 2, "Thứ 4": 3, "Thứ 5": 4,
                   "Thứ 6": 5, "Thứ 7": 6, "CN": 7, "Chủ nhật": 7}
        m_r = re.match(r"Thứ\s+(\d)\s*-\s*Thứ\s+(\d)", tok)
        if m_r:
            days = list(range(int(m_r.group(1)), int(m_r.group(2)) + 1))
        else:
            toks = re.split(r"\s*,\s*", tok)
            days = []
            for t in toks:
                m_s = re.match(r"Thứ\s+(\d)", t)
                if m_s:
                    days.append(int(m_s.group(1)))
                elif t.upper().startswith("CN") or "CHỦ NHẬT" in t.upper():
                    days.append(7)
        for d in days:
            iso = 7 if d == 7 else idx_map.get(f"Thứ {d}", d)
            arr_idx = iso - 1
            the_date = week_dates[arr_idx] if 0 <= arr_idx < len(week_dates) else None
            body_for_day = re.sub(r"\(TN mức 3\)\s*:\s*", "", body)
            parse_cell(body_for_day, arr_idx, cur_area_code, cur_room,
                       cur_time[0], cur_time[1], the_date)
        continue


# ---------------------------------------------------------------- emit SQL
def fmt_date_or_null(d):
    return "NULL" if d is None else f"'{d}'"


def map_dept_code(raw: str) -> str:
    return SCHEDULE_DEPT_MAP.get(raw, raw)


# Dedup
seen: set[tuple] = set()
deduped: list[dict] = []
for s in schedules:
    key = (s["doctor_code"], s["dept_code"], s["day_of_week"],
           s["effective_date"], s["room"], s["shift"])
    if key in seen:
        continue
    seen.add(key)
    deduped.append(s)

out = []
out.append("-- =====================================================================")
out.append("-- V4__seed_doctor_schedules.sql")
out.append("-- AUTO-GENERATED by data-api/scripts/parse-schedule.py")
out.append("-- Source: data/raw/Lich_kham_benh_29.6-19.7.2026.txt")
out.append("-- Doctor FKs resolve to V3 crawled doctor codes by normalized name.")
out.append("-- end_time 16:31:00 reflects source typo '16.31' in raw (faithful).")
out.append("-- =====================================================================")
out.append("")
out.append("-- doctor_schedules (deduped on doctor+dept+day+date+room+shift)")
for s in deduped:
    out.append(
        "INSERT INTO hospital.doctor_schedules "
        "(doctor_id, department_id, day_of_week, effective_date, start_time, end_time, shift, room, is_active) "
        "VALUES ("
        f"(SELECT id FROM hospital.doctors WHERE code = {sql_escape(s['doctor_code'])}), "
        f"(SELECT id FROM hospital.departments WHERE code = {sql_escape(map_dept_code(s['dept_code']))}), "
        f"{s['day_of_week']}, {fmt_date_or_null(s['effective_date'])}, "
        f"'{s['start_time']}', '{s['end_time']}', '{s['shift']}', {sql_escape(s['room'])}, TRUE);"
    )

out.append("")
out.append(f"-- stats: schedules_raw={len(schedules)} schedules_deduped={len(deduped)} "
           f"schedule_only_doctors={len(EXTRA_DOCTORS)}")

OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"OK -> {OUT}")
print(f"   schedules_raw={len(schedules)}  deduped={len(deduped)}  "
      f"schedule_only_doctors={len(EXTRA_DOCTORS)}")

# Also emit a sidecar JSON listing schedule-only doctors so V3 can include them.
sidecar = REPO / "data-api" / "scripts" / "_schedule-only-doctors.json"
sidecar.write_text(json.dumps([
    {"code": v["code"], "fullName": v["full_name"], "degree": v["degree"],
     "source": "schedule-derived (not in crawled roster)",
     "departmentCodes": sorted(v["dept_codes"])}
    for v in EXTRA_DOCTORS.values()
], ensure_ascii=False, indent=2), encoding="utf-8")
print(f"   schedule-only sidecar -> {sidecar}")
