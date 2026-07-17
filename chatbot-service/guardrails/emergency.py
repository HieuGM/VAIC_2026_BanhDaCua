from dataclasses import dataclass
import re
import unicodedata


SPACE_RE = re.compile(r"\s+")
NON_WORD_RE = re.compile(r"[^a-z0-9\s]")
NEGATION_RE = re.compile(
    r"(?:^|\s)(?:khong|ko|khong co|khong bi|khong thay|khong con|chua|chang)\s+(?:\w+\s+){0,3}$"
)
PAST_CONTEXT_RE = re.compile(r"(?:^|\s)(?:hom qua|toi qua|sang qua|chieu qua|luc truoc|truoc do)\b")
RESOLVED_CONTEXT_RE = re.compile(r"\b(?:gio da het|hien da het|bay gio da het|da het|het roi|khong con)\b")


@dataclass(frozen=True)
class EmergencyRule:
    keyword: str
    pattern: re.Pattern[str]
    confidence: float = 0.95


EMERGENCY_RULES = [
    EmergencyRule(
        "tim dap bat thuong kem choang",
        re.compile(r"\btim dap (?:nhanh|cham|bat thuong|loan nhip|hoi hop)(?:\s+\w+){0,6}\s+(?:choang|xay xam|ngat)\b"),
    ),
    EmergencyRule(
        "dau nguc lan tay/vai/ham",
        re.compile(r"\bdau nguc(?:\s+\w+){0,6}\s+lan(?:\s+\w+){0,3}\s+(?:tay|vai|ham|co|lung)\b"),
    ),
    EmergencyRule(
        "dau nguc du doi",
        re.compile(r"\bdau nguc(?:\s+\w+){0,2}\s+(?:du doi|rat dau|nang|khong chiu duoc)\b"),
    ),
    EmergencyRule("kho tho", re.compile(r"\bkho tho\b"), 0.93),
    EmergencyRule("bat tinh", re.compile(r"\bbat tinh\b")),
    EmergencyRule("ngat", re.compile(r"\bngat(?: xiu)?\b"), 0.93),
    EmergencyRule("tim tai", re.compile(r"\b(?:tim tai|tai xanh)\b")),
    EmergencyRule("co giat", re.compile(r"\bco giat\b")),
    EmergencyRule(
        "chay mau nghiem trong",
        re.compile(r"\b(?:chay mau nghiem trong|chay mau khong cam duoc|mat mau nhieu)\b"),
    ),
    EmergencyRule("choang/soc", re.compile(r"\b(?:choang|soc|xay xam)\b"), 0.9),
]


@dataclass(frozen=True)
class EmergencyDetection:
    detected: bool
    confidence: float = 0.0
    reason: str | None = None
    matched_keyword: str | None = None
    negated: bool = False


def detect_emergency(text: str) -> EmergencyDetection:
    normalized = normalize_emergency_text(text)
    skipped_match: EmergencyDetection | None = None

    for rule in EMERGENCY_RULES:
        for match in rule.pattern.finditer(normalized):
            if _is_negated(normalized, match.start()):
                skipped_match = EmergencyDetection(
                    False,
                    0.0,
                    f"negated_keyword:{rule.keyword}",
                    rule.keyword,
                    True,
                )
                continue
            if _is_resolved_past_context(normalized, match.start(), match.end()):
                skipped_match = EmergencyDetection(
                    False,
                    0.0,
                    f"resolved_past_keyword:{rule.keyword}",
                    rule.keyword,
                    False,
                )
                continue
            return EmergencyDetection(
                True,
                rule.confidence,
                f"matched_keyword:{rule.keyword}",
                rule.keyword,
                False,
            )

    return skipped_match or EmergencyDetection(False)


def normalize_emergency_text(value: str) -> str:
    text = (value or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = NON_WORD_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()


def _is_negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 48) : start]
    return bool(NEGATION_RE.search(prefix))


def _is_resolved_past_context(text: str, start: int, end: int) -> bool:
    prefix = text[max(0, start - 64) : start]
    suffix = text[end : min(len(text), end + 80)]
    return bool(PAST_CONTEXT_RE.search(prefix) and RESOLVED_CONTEXT_RE.search(suffix))
