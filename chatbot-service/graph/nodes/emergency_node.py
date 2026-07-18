from app.config import get_settings
from core.enums import Intent, Route, SafetyFlag
from core.state import ChatState
from guardrails.emergency import detect_emergency


async def emergency_node(state: ChatState) -> dict:
    result = detect_emergency(state.get("normalized_message") or state.get("message") or "")
    if not result.detected:
        return {}

    flags = list(state.get("safety_flags") or [])
    if SafetyFlag.EMERGENCY.value not in flags:
        flags.append(SafetyFlag.EMERGENCY.value)

    metadata = dict(state.get("metadata") or {})
    metadata["emergency"] = {
        "detected": True,
        "reason": result.reason,
        "matched_keyword": result.matched_keyword,
        "confidence": result.confidence,
    }

    return {
        "intent": Intent.EMERGENCY.value,
        "route": Route.EMERGENCY.value,
        "safety_flags": flags,
        "confidence": result.confidence,
        "answer": emergency_answer_text(),
        "needs_handoff": True,
        "metadata": metadata,
    }


def emergency_answer_text() -> str:
    settings = get_settings()
    lines = [
        (
            "Day co the la tinh huong can cap cuu. "
            f"Hay goi {settings.emergency_number} ngay hoac den co so cap cuu gan nhat."
        ),
        "Chatbot khong chan doan, khong ke don va khong huong dan tu dieu tri trong tinh huong nay.",
    ]
    if settings.hotline:
        lines.append(f"Neu can ho tro tu benh vien, vui long lien he hotline {settings.hotline}.")
    return " ".join(lines)
