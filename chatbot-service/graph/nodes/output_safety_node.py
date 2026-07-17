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
        "answer": "Minh chua the tra loi noi dung nay mot cach an toan. Vui long lien he bac si hoac kenh ho tro chinh thuc cua benh vien.",
        "safety_flags": flags,
        "needs_handoff": True,
    }
