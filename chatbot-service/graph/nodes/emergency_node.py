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
            "Đây có thể là tình huống cần cấp cứu. "
            f"Hãy gọi {settings.emergency_number} ngay hoặc đến cơ sở cấp cứu gần nhất."
        ),
        "Chatbot không chẩn đoán, không kê đơn và không hướng dẫn tự điều trị trong tình huống này.",
    ]
    if settings.hotline:
        lines.append(f"Nếu cần hỗ trợ từ bệnh viện, vui lòng liên hệ hotline {settings.hotline}.")
    return " ".join(lines)
