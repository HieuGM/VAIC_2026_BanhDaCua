import re


SCRIPT_RE = re.compile(r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def normalize_user_text(value: str) -> str:
    cleaned = SCRIPT_RE.sub(" ", value or "")
    cleaned = TAG_RE.sub(" ", cleaned)
    cleaned = SPACE_RE.sub(" ", cleaned)
    return cleaned.strip()
