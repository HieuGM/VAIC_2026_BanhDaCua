#!/usr/bin/env python3
"""
parse-services.py — Parse service + price data from BHYT price table
(data/raw/banggiaBHYT.txt) and emit V5__seed_services_and_prices.sql.

Source: banggiaBHYT.txt is well-structured as `STT | mã | tên | giá | ghi chú`.
Six categories per the file's own section headers:
  1. Khám bệnh + ngày giường      -> consultation
  2. Xét nghiệm                    -> lab
  3. Thủ thuật & CĐHA              -> procedure
  4. Chụp cộng hưởng từ (CNT)      -> mri
  5. Chụp cắt lớp vi tính (CLVT)   -> ct
  6. Can thiệp tim mạch            -> intervention

The BHYT file is used because it has stable codes (mã tương đương) and a single
audience (BHYT ceiling). The no_bhyt price table (GiaDVBV_tim_HN.txt) lacks
codes and is harder to match row-for-row; we extract a few high-signal rows
(Khám bệnh, ngày giường) for audience=no_bhyt to demonstrate both audiences.
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

CATEGORY_BY_SECTION = {
    "1": "consultation",   # Khám bệnh + ngày giường
    "2": "lab",            # Xét nghiệm
    "3": "procedure",      # Thủ thuật & Chẩn đoán hình ảnh
    "4": "mri",            # Chụp cộng hưởng từ
    "5": "ct",             # Chụp cắt lớp vi tính
    "6": "intervention",   # Can thiệp tim mạch
}


def parse_price(s: str) -> int | None:
    """'42.100' -> 42100 ; '1.712.000' -> 1712000."""
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


# ---------------- BHYT ----------------
def parse_bhyt(path: Path) -> list[dict]:
    """Return list of {code, name, category, price_vnd, note} from banggiaBHYT."""
    if not path.exists():
        print(f"ERROR: missing {path}", file=sys.stderr); sys.exit(1)
    text = path.read_text(encoding="utf-8")
    services: list[dict] = []
    current_cat = None
    # Header lines like: "1. BẢNG GIÁ BẢO HIỂM Y TẾ - KHÁM BỆNH VÀ NGÀY GIƯỜNG ĐIỀU TRỊ"
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        up = s.upper()
        m_sec = re.match(r"^(\d)\.\s*BẢNG GIÁ BẢO HIỂM Y TẾ", up)
        if m_sec:
            current_cat = CATEGORY_BY_SECTION.get(m_sec.group(1))
            continue
        # Section 1 has no "mã tương đương" column: "STT | DỊCH VỤ | GIÁ | GHI CHÚ"
        # Sections 2..6: "STT | mã | DỊCH VỤ | GIÁ | GHI CHÚ"
        parts = [p.strip() for p in re.split(r"\s*\|\s*", s)]
        # skip header rows and separators
        if not parts or parts[0].upper().startswith("STT") or "---" in s:
            continue
        # Must start with a number (STT)
        if not re.match(r"^\d+$", parts[0]):
            continue
        if current_cat == "consultation":
            # parts: [STT, tên, giá, ghi chú]
            if len(parts) < 3:
                continue
            name = parts[1]
            price = parse_price(parts[2])
            note = parts[3] if len(parts) >= 4 else ""
            code = f"KB-{int(parts[0]):04d}"
        else:
            # parts: [STT, mã, tên, giá, ghi chú]
            if len(parts) < 4:
                continue
            code = parts[1] or f"{current_cat.upper()}-{int(parts[0]):04d}"
            name = parts[2]
            price = parse_price(parts[3])
            note = parts[4] if len(parts) >= 5 else ""
        if price is None or not name:
            continue
        services.append({"code": code, "name": name, "category": current_cat,
                         "price_vnd": price, "note": note, "audience": "BHYT"})
    return services


# ---------------- no_bhyt (subset) ----------------
def parse_no_bhyt_subset(path: Path) -> list[dict]:
    """Extract the 'Khám bệnh + ngày giường' rows from GiaDVBV for no_bhyt prices."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    out: list[dict] = []
    # These appear as "1 / Giá Khám bệnh / 50.600 / 50.600 /" patterns.
    # Walk lines and capture: STT, name (may span lines), price CS1, price CS2.
    # Simpler approach: scan for known service tokens.
    targets = [
        ("Giá Khám bệnh", "KB-0001", "Khám bệnh"),
        ("Hội chẩn để xác định ca bệnh khó", "KB-0002", "Hội chẩn ca bệnh khó"),
        ("Ngày điều trị Hồi sức tích cực", "KB-0003", "Ngày điều trị Hồi sức tích cực (ICU)"),
        ("Ngày giường bệnh Hồi sức cấp cứu", "KB-0004", "Ngày giường Hồi sức cấp cứu"),
    ]
    lines = text.splitlines()
    for needle, code, label in targets:
        for i, ln in enumerate(lines):
            if needle in ln:
                # next numeric token after the needle, scanning next ~5 lines
                window = " ".join(lines[i:i + 6])
                m = re.search(r"(\d[\d\.]{3,})", window)
                if m:
                    price = parse_price(m.group(1))
                    if price:
                        out.append({"code": code, "name": label,
                                    "category": "consultation",
                                    "price_vnd": price, "note": "",
                                    "audience": "no_bhyt",
                                    "campus": None})
                break
    return out


def main():
    bhyt = parse_bhyt(SRC_BHYT)
    nobhyt = parse_no_bhyt_subset(SRC_NOBHYT)

    # Build canonical services keyed by code (consultation rows from BHYT use
    # synthetic KB-0001..N which we mirror for no_bhyt).
    services: dict[str, dict] = {}
    for r in bhyt:
        services[r["code"]] = {
            "code": r["code"], "name": r["name"], "category": r["category"],
        }
    for r in nobhyt:
        if r["code"] not in services:
            services[r["code"]] = {
                "code": r["code"], "name": r["name"], "category": r["category"],
            }

    out = [
        "-- =====================================================================",
        "-- V5__seed_services_and_prices.sql",
        "-- AUTO-GENERATED by data-api/scripts/parse-services.py",
        "-- Sources:",
        "--   BHYT ceiling prices: data/raw/banggiaBHYT.txt (audience=BHYT)",
        "--   Service price (no BHYT) subset: data/raw/GiaDVBV_tim_HN.txt",
        "-- Source URL: " + SOURCE_URL,
        "-- =====================================================================",
        "",
        "-- services",
    ]
    for s in sorted(services.values(), key=lambda x: (x["category"], x["code"])):
        out.append(
            "INSERT INTO hospital.services "
            "(code, name, category, department_id, description, is_active) "
            f"VALUES ({sql_escape(s['code'])}, {sql_escape(s['name'])}, "
            f"{sql_escape(s['category'])}, NULL, NULL, TRUE) "
            "ON CONFLICT (code) DO NOTHING;"
        )

    out.append("")
    out.append("-- service_prices")
    # BHYT prices
    for r in bhyt:
        out.append(
            "INSERT INTO hospital.service_prices "
            "(service_id, price_vnd, audience, campus, effective_date, source_url, note) "
            "VALUES ("
            f"(SELECT id FROM hospital.services WHERE code = {sql_escape(r['code'])}), "
            f"{r['price_vnd']}, 'BHYT', NULL, '{EFFECTIVE_DATE}', "
            f"{sql_escape(SOURCE_URL)}, {sql_escape(r['note'])});"
        )
    # no_bhyt prices
    for r in nobhyt:
        out.append(
            "INSERT INTO hospital.service_prices "
            "(service_id, price_vnd, audience, campus, effective_date, source_url, note) "
            "VALUES ("
            f"(SELECT id FROM hospital.services WHERE code = {sql_escape(r['code'])}), "
            f"{r['price_vnd']}, 'no_bhyt', NULL, '{EFFECTIVE_DATE}', "
            f"{sql_escape(SOURCE_URL)}, {sql_escape(r.get('note', ''))});"
        )

    out.append("")
    out.append(f"-- stats: services={len(services)} bhyt_prices={len(bhyt)} "
               f"no_bhyt_prices={len(nobhyt)}")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"OK -> {OUT}")
    print(f"   services={len(services)}  bhyt_prices={len(bhyt)}  no_bhyt_prices={len(nobhyt)}")


if __name__ == "__main__":
    main()
