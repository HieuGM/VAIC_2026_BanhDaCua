from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta


SPACE_RE = re.compile(r"\s+")
NON_WORD_RE = re.compile(r"[^a-z0-9\-\s]")
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
DMY_DATE_RE = re.compile(r"\b(?P<day>\d{1,2})[/-](?P<month>\d{1,2})(?:[/-](?P<year>\d{2,4}))?\b")
NORMALIZED_DMY_DATE_RE = re.compile(r"\b\d{1,2}\s+\d{1,2}(?:\s+\d{2,4})?\b")

GENERIC_SERVICE_TERMS = {
    "bang",
    "bao",
    "bao nhieu",
    "chi",
    "chi phi",
    "dich",
    "dich vu",
    "gia",
    "hoi",
    "la",
    "phi",
    "the",
    "toi",
}


def normalize_text(value: str) -> str:
    text = (value or "").lower().replace("đ", "d").replace("Ä‘", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = NON_WORD_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()


def extract_service_category(text: str) -> str | None:
    normalized = normalize_text(text)
    if _contains_any(normalized, ["xet nghiem", "lab"]):
        return "lab"
    if _contains_any(normalized, ["sieu am", "x quang", "x-quang", "chup", "ct", "mri", "doppler"]):
        return "imaging"
    if _contains_any(normalized, ["phau thuat", "thu thuat", "can thiep"]):
        return "procedure"
    if _contains_any(normalized, ["kham", "tu van"]):
        return "consultation"
    return None


def extract_service_query(text: str) -> str | None:
    normalized = normalize_text(text)
    value = _remove_phrases(
        normalized,
        [
            "bang gia",
            "gia dich vu",
            "chi phi",
            "phi kham",
            "gia kham",
            "bao nhieu tien",
            "bao nhieu",
            "dich vu",
            "gia",
            "toi muon hoi",
            "cho toi hoi",
            "cho toi xem",
            "cua benh vien",
            "benh vien",
        ],
    )
    category = extract_service_category(normalized)
    if category == "consultation":
        value = _remove_phrases(value, ["kham", "tu van"])
    return _none_if_generic(value)


def extract_doctor_query(text: str) -> str | None:
    normalized = normalize_text(text)
    normalized = _remove_date_mentions(normalized)
    value = _remove_phrases(
        normalized,
        [
            "lich lam viec cua bac si",
            "lich kham cua bac si",
            "lich lam viec bac si",
            "lich kham bac si",
            "lich bac si",
            "lich chuyen khoa",
            "lich kham chuyen khoa",
            "lich lam viec chuyen khoa",
            "bac si nao",
            "bac si",
            "chuyen khoa",
            "lich kham",
            "lich",
            "ca kham",
            "lam viec",
            "ngay nao",
            "ngay",
            "hom nay",
            "ngay mai",
            "tuan nay",
            "kham",
            "co",
            "khong",
            "cua",
            "cho",
            "xem",
            "cho toi xem",
            "toi muon xem",
        ],
    )
    return _none_if_generic(value)


def extract_bhyt_category(text: str) -> str | None:
    normalized = normalize_text(text)
    if _contains_any(normalized, ["dong chi tra", "chi tra", "muc huong", "cung chi tra"]):
        return "copay"
    if _contains_any(normalized, ["tim mach", "tim"]):
        return "cardiac"
    if _contains_any(normalized, ["man tinh", "benh man"]):
        return "chronic"
    if _contains_any(normalized, ["chuyen tuyen", "trai tuyen", "thong tuyen"]):
        return "cross_ref"
    return None


def extract_procedure_code(text: str) -> str | None:
    normalized = normalize_text(text)
    if _contains_any(normalized, ["quy trinh kham", "thu tuc kham", "di kham", "dang ky kham", "can chuan bi"]):
        return "QT.25.01"
    return None


def extract_date_range(text: str, *, today: date | None = None) -> tuple[str | None, str | None]:
    base = today or date.today()
    date_text = _normalize_date_text(text)

    dmy_match = DMY_DATE_RE.search(date_text)
    if dmy_match:
        value = _coerce_dmy_date(
            dmy_match.group("day"),
            dmy_match.group("month"),
            dmy_match.group("year"),
            base,
        )
        if value:
            return value, value

    normalized = normalize_text(text)
    match = ISO_DATE_RE.search(normalized)
    if match:
        value = match.group(0)
        return value, value
    if "ngay mai" in normalized:
        value = (base + timedelta(days=1)).isoformat()
        return value, value
    if "hom nay" in normalized:
        value = base.isoformat()
        return value, value
    return None, None


def _normalize_date_text(value: str) -> str:
    text = (value or "").lower().replace("đ", "d").replace("Ä‘", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def _coerce_dmy_date(day_text: str, month_text: str, year_text: str | None, base: date) -> str | None:
    try:
        day = int(day_text)
        month = int(month_text)
        year = int(year_text) if year_text else base.year
        if year < 100:
            year += 2000
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _remove_date_mentions(value: str) -> str:
    without_iso = ISO_DATE_RE.sub(" ", value)
    without_dmy = NORMALIZED_DMY_DATE_RE.sub(" ", without_iso)
    return SPACE_RE.sub(" ", without_dmy).strip()


def _none_if_generic(value: str) -> str | None:
    normalized = normalize_text(value)
    if not normalized:
        return None
    tokens = set(normalized.split())
    generic_tokens = set()
    for item in GENERIC_SERVICE_TERMS:
        generic_tokens.update(item.split())
    if tokens and tokens.issubset(generic_tokens):
        return None
    return normalized


def _remove_phrases(text: str, phrases: list[str]) -> str:
    value = f" {text} "
    for phrase in sorted(phrases, key=len, reverse=True):
        value = value.replace(f" {normalize_text(phrase)} ", " ")
    return SPACE_RE.sub(" ", value).strip()


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
