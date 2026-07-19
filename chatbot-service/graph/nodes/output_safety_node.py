from core.enums import SafetyFlag
from core.state import ChatState
from guardrails.medical_safety import is_output_safe


async def output_safety_node(state: ChatState) -> dict:
    answer = state.get("answer") or ""
    if is_output_safe(answer):
        return {}

    flags = list(state.get("safety_flags") or [])
    if SafetyFlag.MEDICAL_ADVICE.value not in flags:
        flags.append(SafetyFlag.MEDICAL_ADVICE.value)
    return {
        "answer": "Mình chưa thể trả lời nội dung này một cách an toàn. Vui lòng liên hệ bác sĩ hoặc kênh hỗ trợ chính thức của bệnh viện.",
        "safety_flags": flags,
        "needs_handoff": True,
    }
