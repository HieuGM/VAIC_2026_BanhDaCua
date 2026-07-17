from core.enums import Intent, Route, SafetyFlag
from core.state import ChatState
from guardrails.emergency import detect_emergency


async def emergency_node(state: ChatState) -> dict:
    result = detect_emergency(state.get("normalized_message") or "")
    if not result.detected:
        return {}

    return {
        "intent": Intent.EMERGENCY.value,
        "route": Route.EMERGENCY.value,
        "safety_flags": [SafetyFlag.EMERGENCY.value],
        "confidence": result.confidence,
        "answer": (
            "Day co the la tinh huong can cap cuu. Hay goi 115 hoac den co so cap cuu gan nhat. "
            "Chatbot khong chan doan, khong ke don va khong huong dan tu dieu tri trong tinh huong nay."
        ),
        "needs_handoff": True,
        "metadata": {"emergency_reason": result.reason},
    }
