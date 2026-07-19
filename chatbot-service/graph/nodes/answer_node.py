from core.enums import Route
from core.state import ChatState
from graph.nodes.emergency_node import emergency_answer_text
from llm.answer_generator import generate_grounded_answer


async def answer_node(state: ChatState) -> dict:
    if state.get("answer"):
        return {}

    if state.get("route") == Route.HUMAN_HANDOFF.value:
        return {
            "answer": "Mình sẽ chuyển yêu cầu này sang kênh hỗ trợ phù hợp. Bạn có thể liên hệ hotline hoặc nhân viên CSKH.",
            "needs_handoff": True,
        }

    if state.get("route") == Route.EMERGENCY.value:
        return {
            "answer": emergency_answer_text(),
            "needs_handoff": True,
        }

    if state.get("route") == Route.UNSUPPORTED.value:
        return {
            "answer": "Mình chưa thể hỗ trợ yêu cầu này trong phạm vi chatbot bệnh viện.",
            "needs_handoff": True,
        }

    answer = await generate_grounded_answer(state)
    return {"answer": answer}
