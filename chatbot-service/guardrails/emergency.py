from dataclasses import dataclass


EMERGENCY_KEYWORDS = [
    "dau nguc du doi",
    "kho tho",
    "bat tinh",
    "ngat",
    "tim tai",
    "co giat",
    "chay mau nghiem trong",
    "choang",
]


@dataclass(frozen=True)
class EmergencyDetection:
    detected: bool
    confidence: float = 0.0
    reason: str | None = None


def detect_emergency(text: str) -> EmergencyDetection:
    normalized = text.lower()
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in normalized:
            return EmergencyDetection(True, 0.95, f"matched_keyword:{keyword}")
    return EmergencyDetection(False)
