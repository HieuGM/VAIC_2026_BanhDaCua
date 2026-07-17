#!/usr/bin/env python3
"""
seed-crawled.py — Emit Flyway SQL for crawled ground-truth data:
  V2__seed_departments.sql       (data/seed/crawled/departments.json)
  V3__seed_doctors.sql           (crawled/doctors.json + schedule-only extras)
  V6__seed_bhyt_policies.sql     (crawled/bhyt-policies.json)
  V7__seed_support_channels.sql  (crawled/channels.json)

Departments and doctors are authoritative. Schedule-only doctors (parsed from
the raw schedule but absent in the crawled roster) are appended as additional
rows with source='schedule-derived'.
"""
from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CRAWLED = REPO / "data" / "seed" / "crawled"
MIGR = REPO / "data-api" / "src" / "main" / "resources" / "db" / "migration"
SCHEDULE_ONLY = REPO / "data-api" / "scripts" / "_schedule-only-doctors.json"

# Canonical campus tag per department code (crawled JSON does not include this).
CAMPUS_BY_CODE = {
    "kham-benh-tu-nguyen": "CS1+CS2",
    "kham-benh-tu-nguyen-1": "CS1",
    "kham-benh-tu-nguyen-3": "CS1",
    "phong-kham-da-khoa-cs2": "CS2",
    "don-vien-tim-mach-can-thiep-cs2": "CS2",
}
# Sort order for departments (lower = earlier in listings).
DEPT_SORT = {
    "kham-benh-tu-nguyen": 1,
    "kham-benh-tu-nguyen-1": 2,
    "kham-benh-tu-nguyen-3": 3,
    "phong-kham-da-khoa-cs2": 4,
}


def slugify(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    a = "".join(c for c in nfkd if not unicodedata.combining(c))
    a = a.lower()
    return re.sub(r"[^a-z0-9]+", "-", a).strip("-") or "x"


def sql_escape(s) -> str:
    if s is None:
        return "NULL"
    s = str(s)
    if s == "":
        return "NULL"
    return "'" + s.replace("'", "''").replace("\\", "\\\\") + "'"


def json_or_die(path: Path):
    if not path.exists():
        print(f"ERROR: missing {path}", file=sys.stderr); sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------- departments ----------------
def emit_departments() -> int:
    deps = json_or_die(CRAWLED / "departments.json")
    out = [
        "-- =====================================================================",
        "-- V2__seed_departments.sql",
        "-- Source: data/seed/crawled/departments.json (crawled from official site).",
        "-- =====================================================================",
        "",
        "-- departments",
    ]
    # Sort: by explicit DEPT_SORT, then by code for determinism.
    def sort_key(d):
        return (DEPT_SORT.get(d["code"], 100), d["code"])
    for d in sorted(deps, key=sort_key):
        campus = CAMPUS_BY_CODE.get(d["code"], "")
        wh = d.get("workingHours") or ""
        floor = d.get("floor") or ""
        phone = d.get("phone") or ""
        sort_order = DEPT_SORT.get(d["code"], 100)
        out.append(
            "INSERT INTO hospital.departments "
            "(code, name, description, campus, floor, working_hours, phone, sort_order, is_active) "
            f"VALUES ({sql_escape(d['code'])}, {sql_escape(d['name'])}, "
            f"{sql_escape(d.get('description'))}, {sql_escape(campus)}, {sql_escape(floor)}, "
            f"{sql_escape(wh)}, {sql_escape(phone)}, {sort_order}, TRUE) "
            "ON CONFLICT (code) DO NOTHING;"
        )
    target = MIGR / "V2__seed_departments.sql"
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"OK -> {target}  ({len(deps)} rows)")
    return len(deps)


# ---------------- doctors ----------------
def emit_doctors() -> int:
    docs = json_or_die(CRAWLED / "doctors.json")
    deps = json_or_die(CRAWLED / "departments.json")

    def norm_dept(s: str | None) -> str:
        # Canonicalize a department label for matching crawled doctor department
        # strings against department names. Reconciles three real inconsistencies
        # between the official "lich lam viec bac sy" page and the departments
        # page (both authoritative): (1) Vietnamese 'đ' is NOT decomposed by
        # NFKD, so force 'd'; (2) synonym "Khu"/"Khoa" for the same clinical
        # unit; (3) parenthetical qualifiers like "(Kham TN muc 3)". This is
        # label reconciliation only — no value invented.
        if not s:
            return ""
        s = re.sub(r"\([^)]*\)", " ", s)             # drop parentheticals
        nfkd = unicodedata.normalize("NFKD", s)
        plain = "".join(c for c in nfkd if not unicodedata.combining(c))
        plain = plain.lower().replace("đ", "d")       # NFKD does not split 'đ'
        plain = re.sub(r"\bkhu\b", "khoa", plain)     # unify synonym (same unit)
        return re.sub(r"\s+", " ", plain).strip(" -")

    # Build normalized name -> code index for departments.
    dept_name_to_code: dict[str, str] = {}
    for d in deps:
        dept_name_to_code[norm_dept(d["name"])] = d["code"]

    # Build canonical list, deduping by normalized name; preserve richest record.
    by_key: dict[str, dict] = {}

    def norm_name(s: str) -> str:
        nfkd = unicodedata.normalize("NFKD", s)
        a = "".join(c for c in nfkd if not unicodedata.combining(c))
        return re.sub(r"\s+", " ", a.lower()).strip()

    def dept_code_from_name(dept_str: str | None) -> str | None:
        if not dept_str:
            return None
        # crawled department may be compound, e.g.
        # "Ban Giám đốc / Khoa Khám bệnh Tự nguyện 1 / Tự nguyện 3 - Cơ sở 1".
        # Try the whole string, then each "/" segment, until one resolves.
        norm = norm_dept(dept_str)
        candidates = [norm] + [seg.strip() for seg in norm.split("/") if seg.strip()]
        for cand in candidates:
            if cand and cand in dept_name_to_code:
                return dept_name_to_code[cand]
        return None

    for d in docs:
        key = norm_name(d.get("fullName", ""))
        if not key:
            continue
        if key not in by_key:
            by_key[key] = {
                "code": slugify(d["fullName"]),
                "fullName": d["fullName"],
                "degree": d.get("degree") or "",
                "title": d.get("title"),
                "specialty": d.get("specialty"),
                "bio": d.get("bio"),
                "department": d.get("department"),
                "sourceUrl": d.get("sourceUrl"),
                "source": "crawled",
            }
        else:
            cur = by_key[key]
            if not cur["degree"] and d.get("degree"):
                cur["degree"] = d["degree"]
            if not cur["title"] and d.get("title"):
                cur["title"] = d["title"]
            if not cur.get("specialty") and d.get("specialty"):
                cur["specialty"] = d["specialty"]
            if not cur["bio"] and d.get("bio"):
                cur["bio"] = d["bio"]
            if not cur["sourceUrl"] and d.get("sourceUrl"):
                cur["sourceUrl"] = d["sourceUrl"]

    # Merge schedule-only doctors
    schedule_only = []
    if SCHEDULE_ONLY.exists():
        schedule_only = json.loads(SCHEDULE_ONLY.read_text(encoding="utf-8"))
    for e in schedule_only:
        key = norm_name(e["fullName"])
        if key in by_key:
            continue
        by_key[key] = {
            "code": e["code"],
            "fullName": e["fullName"],
            "degree": e.get("degree") or "",
            "title": None,
            "specialty": None,
            "bio": None,
            "department": None,
            "sourceUrl": None,
            "source": "schedule-derived",
            "dept_codes_from_schedule": e.get("departmentCodes", []),
        }

    out = [
        "-- =====================================================================",
        "-- V3__seed_doctors.sql",
        "-- Sources: data/seed/crawled/doctors.json (authoritative) + schedule-only",
        "--          doctors parsed from raw schedule (not in crawled roster).",
        "-- specialty: crawled chuyên ngành (Tim mạch, Tim mạch can thiệp, ...).",
        "-- department_id: resolved from crawled dept string via label reconciliation",
        "--   (đ→d, Khu=Khoa synonym, try each compound segment). See seed-crawled.py.",
        "-- No bio/avatar fabricated (R1). schedule-derived records flagged.",
        "-- =====================================================================",
        "",
        "-- doctors",
    ]
    # First pass: schedule-only doctors may carry schedule-derived department codes
    # (the SCHEDULE_DEPT_MAP canonical ones); pick the first as primary department.
    SCHED_DEPT_MAP = {
        "KBTN1_CS1": "kham-benh-tu-nguyen-1",
        "KBTN3_CS1": "kham-benh-tu-nguyen-3",
        "KHTN_CS2": "kham-benh-tu-nguyen",
        "RHM_CS2": "phong-kham-da-khoa-cs2", "PHCN_CS2": "phong-kham-da-khoa-cs2",
        "TMH_CS2": "phong-kham-da-khoa-cs2", "PK_NHI_CS2": "phong-kham-da-khoa-cs2",
        "DA_LIEU_CS2": "phong-kham-da-khoa-cs2", "SAN_CS2": "phong-kham-da-khoa-cs2",
        "YHCT_CS2": "phong-kham-da-khoa-cs2", "NOI_HH_CS2": "phong-kham-da-khoa-cs2",
        "NOI_CXK_CS2": "phong-kham-da-khoa-cs2", "NTM_NT_CS2": "phong-kham-da-khoa-cs2",
        "MAT_CS2": "phong-kham-da-khoa-cs2",
    }

    def sort_key(d):
        return (0 if d["source"] == "crawled" else 1, d["fullName"])

    for d in sorted(by_key.values(), key=sort_key):
        # Resolve department_id for this doctor.
        dept_id_sql = "NULL"
        if d.get("department"):
            code = dept_code_from_name(d["department"])
            if code:
                dept_id_sql = f"(SELECT id FROM hospital.departments WHERE code = '{code}')"
        elif d.get("dept_codes_from_schedule"):
            mapped = SCHED_DEPT_MAP.get(d["dept_codes_from_schedule"][0]) or d["dept_codes_from_schedule"][0]
            dept_id_sql = f"(SELECT id FROM hospital.departments WHERE code = '{mapped}')"
        out.append(
            "INSERT INTO hospital.doctors "
            "(code, full_name, degree, specialty, title, department_id, bio, avatar_url, is_active) "
            "VALUES ("
            f"{sql_escape(d['code'])}, {sql_escape(d['fullName'])}, "
            f"{sql_escape(d['degree'])}, {sql_escape(d.get('specialty'))}, "
            f"{sql_escape(d['title'])}, "
            f"{dept_id_sql}, "
            f"{sql_escape(d['bio'])}, NULL, TRUE) "
            "ON CONFLICT (code) DO NOTHING;"
        )

    target = MIGR / "V3__seed_doctors.sql"
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    n_crawled = sum(1 for d in by_key.values() if d["source"] == "crawled")
    n_sched = sum(1 for d in by_key.values() if d["source"] == "schedule-derived")
    print(f"OK -> {target}  ({len(by_key)} unique doctors, {n_crawled} crawled, {n_sched} schedule-only)")
    return len(by_key)


# ---------------- bhyt ----------------
def emit_bhyt() -> int:
    rows = json_or_die(CRAWLED / "bhyt-policies.json")
    out = [
        "-- =====================================================================",
        "-- V6__seed_bhyt_policies.sql",
        "-- Source: data/seed/crawled/bhyt-policies.json (verbatim from official site).",
        "-- =====================================================================",
        "",
        "-- bhyt_policies",
    ]
    cat_map = {
        "bhyt-bang-gia-cu-phap": "general",
        "bhyt-gia-kham-benh-giuong": "general",
        "bhyt-the-vssid-cccd-chip": "cardiac",
        "bhyt-giay-chuyen-tuyen": "cross_ref",
        "bhyt-dong-chi-tra": "copay",
        "bhyt-thu-tuc-hen-kham-lai": "copay",
        "bhyt-uu-tien": "general",
    }
    for r in rows:
        cat = cat_map.get(r["code"], "general")
        out.append(
            "INSERT INTO hospital.bhyt_policies "
            "(code, title, category, summary, details_md, source_url, effective_date) "
            f"VALUES ({sql_escape(r['code'])}, {sql_escape(r['title'])}, "
            f"{sql_escape(cat)}, {sql_escape(r.get('summary'))}, "
            f"{sql_escape(r.get('detailsMd'))}, {sql_escape(r.get('sourceUrl'))}, NULL) "
            "ON CONFLICT (code) DO NOTHING;"
        )
    target = MIGR / "V6__seed_bhyt_policies.sql"
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"OK -> {target}  ({len(rows)} rows)")
    return len(rows)


# ---------------- support_channels ----------------
def emit_channels() -> int:
    rows = json_or_die(CRAWLED / "channels.json")
    out = [
        "-- =====================================================================",
        "-- V7__seed_support_channels.sql",
        "-- Source: data/seed/crawled/channels.json (official URLs/phones, with Zalo).",
        "-- =====================================================================",
        "",
        "-- support_channels",
    ]
    for i, r in enumerate(rows):
        out.append(
            "INSERT INTO hospital.support_channels "
            "(channel_type, label, url, phone, campus, sort_order, is_active) "
            "VALUES ("
            f"{sql_escape(r['channelType'])}, {sql_escape(r.get('label'))}, "
            f"{sql_escape(r.get('url'))}, {sql_escape(r.get('phone'))}, "
            f"{sql_escape(r.get('campus'))}, {i + 1}, TRUE);"
        )
    target = MIGR / "V7__seed_support_channels.sql"
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"OK -> {target}  ({len(rows)} rows)")
    return len(rows)


if __name__ == "__main__":
    n1 = emit_departments()
    # emit doctors AFTER schedule-only sidecar exists. We attempt regardless;
    # if sidecar missing, only crawled doctors are emitted.
    if not SCHEDULE_ONLY.exists():
        print("NOTE: _schedule-only-doctors.json not yet generated — "
              "run parse-schedule.py first to include schedule-only doctors.",
              file=sys.stderr)
    n2 = emit_doctors()
    n3 = emit_bhyt()
    n4 = emit_channels()
    print(f"\nSummary: departments={n1} doctors={n2} bhyt={n3} channels={n4}")
