#!/usr/bin/env python3
"""
parse-services.py — Parse service + price data and emit V5__seed_services_and_prices.sql.

Sources:
  BHYT ceiling prices:  data/raw/banggiaBHYT.txt        (audience=BHYT)
  No-BHYT service prices: data/raw/GiaDVBV_tim_HN.txt   (audience=no_bhyt, NQ45/2024)

GiaDVBV structure (page-scrambled PDF text, ~24K lines, 200 pages, 4 sections):
  Section 1 (line ~62):   KHÁM BỆNH VÀ NGÀY GIƯỜNG ĐIỀU TRỊ      -> consultation
  Section 2 (line ~170):  DỊCH VỤ KỸ THUẬT VÀ XÉT NGHIỆM          -> mixed (code-prefix routed)
  Section 3 (line ~23791): KHÁM SỨC KHỎE LAO ĐỘNG/LÁI XE         -> consultation (health check)
  Section 4 (line ~23819): VÔ CẢM GÂY TÊ                          -> procedure

Each entry: STT line -> mã+name (multi-line) -> price CS1 -> price CS2 (optional) -> note.
We capture: code, name, price CS1, price CS2, section, page-number for confidence tracking.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC_BHYT = REPO / "data" / "raw" / "banggiaBHYT.txt"
SRC_NOBHYT = REPO / "data" / "raw" / "GiaDVBV_tim_HN.txt"
OUT = (REPO / "data-api" / "src" / "main" / "resources" / "db" / "migration"
       / "V5__seed_services_and_prices.sql")

SOURCE_URL = "https://benhvientimhanoi.vn/vn/huong-dan-kham-benh/bang-gia-dich-vu"
EFFECTIVE_DATE = "2026-07-17"
NOBHYT_LAW = "Phụ lục 06 NQ 45/2024/NQ-HĐND Hà Nội (10/12/2024)"

CATEGORY_BY_BHYT_SECTION = {
    "1": "consultation", "2": "lab", "3": "procedure",
    "4": "mri", "5": "ct", "6": "intervention",
}


def parse_price(s: str) -> int | None:
    s = s.strip().replace(".", "").replace(",", "").replace(" ", "")
    if not s.isdigit():
        return None
    return int(s)


def sql_escape(s) -> str:
    if s is None:
        return "NULL"
    s = str(s).strip()
    if s == "":
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


def category_from_code(code: str, section: str) -> str:
    """Best-effort category routing for section 2 entries (mixed)."""
    if section in {"consultation", "consultation_checkup"}:
        return "consultation"
    if section == "procedure_anesthesia":
        return "procedure"
    prefix = code.split(".")[0] if code else ""
    if prefix in {"22", "23", "24", "25", "26", "27", "28"}:
        return "lab"
    if prefix == "18":
        sub = code.split(".")[1] if "." in code else ""
        if sub and sub[:2] in {"05", "06"}:
            return "intervention"
        if sub and sub[:2] == "02":
            return "mri"
        return "ct"
    return "procedure"


# ============================ BHYT parser ============================
def parse_bhyt(path: Path) -> list[dict]:
    if not path.exists():
        print(f"ERROR: missing {path}", file=sys.stderr); sys.exit(1)
    text = path.read_text(encoding="utf-8")
    services: list[dict] = []
    current_cat = None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        up = s.upper()
        m_sec = re.match(r"^(\d)\.\s*BẢNG GIÁ BẢO HIỂM Y TẾ", up)
        if m_sec:
            current_cat = CATEGORY_BY_BHYT_SECTION.get(m_sec.group(1))
            continue
        parts = [p.strip() for p in re.split(r"\s*\|\s*", s)]
        if not parts or parts[0].upper().startswith("STT") or "---" in s:
            continue
        if not re.match(r"^\d+$", parts[0]):
            continue
        if current_cat == "consultation":
            if len(parts) < 3:
                continue
            name = parts[1]; price = parse_price(parts[2])
            note = parts[3] if len(parts) >= 4 else ""
            code = f"KB-{int(parts[0]):04d}"
        else:
            if len(parts) < 4:
                continue
            code = parts[1] or f"{current_cat.upper()}-{int(parts[0]):04d}"
            name = parts[2]; price = parse_price(parts[3])
            note = parts[4] if len(parts) >= 5 else ""
        if price is None or not name:
            continue
        services.append({"code": code, "name": name, "category": current_cat,
                         "price_vnd": price, "note": note, "audience": "BHYT"})
    return services


# ============================ No-BHYT parser ============================
NOBHYT_SECTION_STARTS = [
    (62,    "consultation",          "KHÁM BỆNH VÀ NGÀY GIƯỜNG ĐIỀU TRỊ"),
    (170,   "dvkt_xn",               "DỊCH VỤ KỸ THUẬT VÀ XÉT NGHIỆM"),
    (23791, "consultation_checkup",  "KHÁM SỨC KHỎE LAO ĐỘNG/LÁI XE"),
    (23819, "procedure_anesthesia",  "VÔ CẢM GÂY TÊ"),
]


def parse_no_bhyt_full(path: Path) -> tuple[list[dict], list[dict]]:
    """Return (new_services, prices). new_services carries services whose code
    is NOT already in the BHYT set (caller dedupes). prices has all no_bhyt rows."""
    if not path.exists():
        return [], []
    lines = path.read_text(encoding="utf-8").splitlines()

    def section_for(line_no: int) -> str:
        cur = "consultation"
        for start, sid, _ in NOBHYT_SECTION_STARTS:
            if line_no >= start:
                cur = sid
        return cur

    page_no = 1
    entries: list[dict] = []
    buf: dict | None = None
    name_buf: list[str] = []
    expect = "stt"

    def flush():
        nonlocal buf, name_buf
        # Accept entries with or without code; code-less ones get a synthetic
        # code in the emit pass (for KHÁM BỆNH/giường section-1 rows).
        if buf and buf.get("price_cs1") is not None and (buf.get("code") or name_buf):
            full_name = re.sub(r"\s+", " ", " ".join(name_buf).strip())
            buf["name"] = full_name
            entries.append(buf)
        buf = None
        name_buf = []

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if not line.strip():
            if buf and expect == "note":
                flush(); expect = "stt"
            continue
        m_page = re.match(r"^--- Page (\d+) ---", line.strip())
        if m_page:
            page_no = int(m_page.group(1))
            continue
        up = line.upper().strip()
        if up.startswith("BẢNG GIÁ DỊCH VỤ KỸ THUẬT"):
            flush(); expect = "stt"; continue
        if (up.startswith("ĐƠN VỊ TÍNH") or up.startswith("GHI CHÚ: BẢNG GIÁ")
                or up.startswith("SỞ Y TẾ") or up.startswith("BỆNH VIỆN TIM")
                or up == "STT" or up.startswith("STT ") or up.startswith("MÃ TƯƠNG")
                or up == "DỊCH VỤ KỸ THUẬT" or up == "CƠ SỞ 1"
                or up == "CƠ SỞ 2" or up == "GHI CHÚ" or up.startswith("MỤC LỤC")
                or up.startswith("DANH MỤC") or up.startswith("CHỈ MÀU")):
            continue
        s = line.strip()

        # Lone number = STT (flush previous entry, start new)
        if re.match(r"^\d{1,4}$", s):
            flush()
            buf = {"stt": int(s), "code": None, "price_cs1": None,
                   "price_cs2": None, "note": "", "page": page_no,
                   "section": section_for(i)}
            name_buf = []
            expect = "name_or_code"
            continue

        # Compact form: "<STT>  <code>  <name-part>" all on one line
        m_compact = re.match(r"^(\d{1,4})\s+(\d{2}\.\d{4}\.\d{4}(?:\.[A-Z0-9]+)?)\s*(.*)$", s)
        if m_compact:
            flush()
            buf = {"stt": int(m_compact.group(1)), "code": m_compact.group(2),
                   "price_cs1": None, "price_cs2": None, "note": "",
                   "page": page_no, "section": section_for(i)}
            name_buf = []
            if m_compact.group(3):
                name_buf.append(m_compact.group(3))
            expect = "name"
            continue

        if buf is None:
            continue

        # Price line
        if re.match(r"^[\d\.]+$", s):
            price = parse_price(s)
            if price is None:
                continue
            if buf["price_cs1"] is None:
                buf["price_cs1"] = price
                expect = "price2_or_note"
            elif buf["price_cs2"] is None and expect == "price2_or_note":
                buf["price_cs2"] = price
                expect = "note"
            continue

        # Code at start of a name line
        m_code = re.match(r"^(\d{2}\.\d{4}\.\d{4}(?:\.[A-Z0-9]+)?)\s+(.*)$", s)
        if m_code and buf.get("code") is None:
            buf["code"] = m_code.group(1)
            if m_code.group(2):
                name_buf.append(m_code.group(2))
            expect = "name"
            continue

        # Continuation
        if expect in {"name", "name_or_code", "note", "price2_or_note"}:
            if expect == "note":
                buf["note"] = (buf["note"] + " " + s).strip()
            else:
                name_buf.append(s)

    flush()

    prices: list[dict] = []
    new_services: list[dict] = []
    seen_codes: set[str] = set()

    def synthetic_code(section: str, stt: int) -> str:
        """For section-1 entries that have no mã (KHÁM BỆNH/giường, KSK, gây tê)."""
        prefix = {
            "consultation": "NV-KB-",          # No_bhyt Khám/giường
            "consultation_checkup": "NV-KSK-", # Khám sức khỏe
            "procedure_anesthesia": "NV-GT-",  # Gây tê
            "dvkt_xn": "NV-DV-",               # DVKT fallback (rare)
        }.get(section, "NV-XX-")
        return f"{prefix}{stt:04d}"

    for e in entries:
        if e["price_cs1"] is None:
            continue
        code = e["code"] or synthetic_code(e["section"], e["stt"])
        cat = (category_from_code(code, e["section"])
               if e["code"] else
               {"consultation": "consultation",
                "consultation_checkup": "consultation",
                "procedure_anesthesia": "procedure"}.get(e["section"], "procedure"))
        if code not in seen_codes:
            seen_codes.add(code)
            new_services.append({"code": code, "name": e["name"] or f"(entry #{e['stt']})",
                                 "category": cat})
        confidence = "high" if (e["price_cs1"] and e["price_cs2"]) else "medium"
        note_prefix = (e["note"] + " ") if e["note"] else ""
        note_full = f"{note_prefix}[NQ45/2024; page {e['page']}; confidence={confidence}]"
        prices.append({"code": code, "price_vnd": e["price_cs1"], "audience": "no_bhyt",
                       "campus": "CS1", "note": note_full})
        if e["price_cs2"] is not None:
            prices.append({"code": code, "price_vnd": e["price_cs2"], "audience": "no_bhyt",
                           "campus": "CS2", "note": note_full})
    return new_services, prices


# ============================ main ============================
def main():
    bhyt = parse_bhyt(SRC_BHYT)
    new_svcs, nobhyt_prices = parse_no_bhyt_full(SRC_NOBHYT)

    services: dict[str, dict] = {}
    for r in bhyt:
        services[r["code"]] = {"code": r["code"], "name": r["name"], "category": r["category"]}
    new_only = 0
    for s in new_svcs:
        if s["code"] not in services:
            services[s["code"]] = s
            new_only += 1

    out = [
        "-- =====================================================================",
        "-- V5__seed_services_and_prices.sql",
        "-- AUTO-GENERATED by data-api/scripts/parse-services.py",
        "-- Sources:",
        "--   BHYT ceiling prices: data/raw/banggiaBHYT.txt (audience=BHYT)",
        "--   no_bhyt service prices: data/raw/GiaDVBV_tim_HN.txt (NQ45/2024;",
        "--     page-scrambled PDF; per-row page + confidence flag in note field).",
        f"-- Law basis (no_bhyt): {NOBHYT_LAW}",
        "-- Source URL: " + SOURCE_URL,
        "-- =====================================================================",
        "",
        "-- services",
    ]
    for s in sorted(services.values(), key=lambda x: (x["category"] or "", x["code"])):
        out.append(
            "INSERT INTO hospital.services "
            "(code, name, category, department_id, description, is_active) "
            f"VALUES ({sql_escape(s['code'])}, {sql_escape(s['name'])}, "
            f"{sql_escape(s['category'])}, NULL, NULL, TRUE) "
            "ON CONFLICT (code) DO NOTHING;"
        )

    out.append("")
    out.append("-- service_prices (BHYT)")
    for r in bhyt:
        out.append(
            "INSERT INTO hospital.service_prices "
            "(service_id, price_vnd, audience, campus, effective_date, source_url, note) "
            "VALUES ("
            f"(SELECT id FROM hospital.services WHERE code = {sql_escape(r['code'])}), "
            f"{r['price_vnd']}, 'BHYT', NULL, '{EFFECTIVE_DATE}', "
            f"{sql_escape(SOURCE_URL)}, {sql_escape(r['note'])});"
        )

    out.append("")
    out.append("-- service_prices (no_bhyt — NQ45/2024; page+confidence annotated)")
    for r in nobhyt_prices:
        out.append(
            "INSERT INTO hospital.service_prices "
            "(service_id, price_vnd, audience, campus, effective_date, source_url, note) "
            "VALUES ("
            f"(SELECT id FROM hospital.services WHERE code = {sql_escape(r['code'])}), "
            f"{r['price_vnd']}, 'no_bhyt', {sql_escape(r['campus'])}, '{EFFECTIVE_DATE}', "
            f"{sql_escape(SOURCE_URL)}, {sql_escape(r['note'])});"
        )

    out.append("")
    out.append(f"-- stats: services={len(services)} (bhyt={len(services) - new_only}, "
               f"no_bhyt_only={new_only})  bhyt_prices={len(bhyt)}  "
               f"no_bhyt_prices={len(nobhyt_prices)}")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"OK -> {OUT}")
    print(f"   services={len(services)} (bhyt={len(services)-new_only}, no_bhyt_only={new_only})  "
          f"bhyt_prices={len(bhyt)}  no_bhyt_prices={len(nobhyt_prices)}")


if __name__ == "__main__":
    main()
