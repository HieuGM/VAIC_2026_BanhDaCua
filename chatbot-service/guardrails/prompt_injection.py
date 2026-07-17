SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "bo qua huong dan",
    "system prompt",
    "raw sql",
]


def has_prompt_injection_risk(text: str) -> bool:
    normalized = text.lower()
    return any(pattern in normalized for pattern in SUSPICIOUS_PATTERNS)
