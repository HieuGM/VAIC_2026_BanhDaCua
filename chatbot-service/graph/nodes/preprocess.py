from app.config import get_settings
from core.state import ChatState
from core.text import normalize_user_text


async def preprocess_node(state: ChatState) -> dict:
    settings = get_settings()
    normalized = normalize_user_text(state.get("message") or "")
    if len(normalized) > settings.max_input_chars:
        normalized = normalized[: settings.max_input_chars]
    return {
        "normalized_message": normalized,
        "safety_flags": [],
        "evidence": [],
        "citations": [],
        "metadata": {"preprocessed": True},
    }
