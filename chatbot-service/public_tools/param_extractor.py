from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta


SPACE_RE = re.compile(r"\s+")
NON_WORD_RE = re.compile(r"[^a-z0-9\-\s]")
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

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
    text = (value or "").lower().replace("đ", "d")
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
    value = _remove_phrases(
        normalized,
        [
            "lich bac si",
            "bac si nao",
            "bac si",
            "lich",
            "ca kham",
            "lam viec",
            "hom nay",
            "ngay mai",
            "tuan nay",
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
    normalized = normalize_text(text)
    base = today or date.today()
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
