UNSAFE_PHRASES = [
    "hay dung thuoc",
    "ngung thuoc",
    "tang lieu",
    "giam lieu",
    "ban bi benh",
]


def is_output_safe(answer: str) -> bool:
    normalized = answer.lower()
    return not any(phrase in normalized for phrase in UNSAFE_PHRASES)
