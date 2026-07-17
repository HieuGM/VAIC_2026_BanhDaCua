from core.enums import Route
from core.state import ChatState
from llm.answer_generator import generate_grounded_answer


async def answer_node(state: ChatState) -> dict:
    if state.get("answer"):
        return {}

    if state.get("route") == Route.HUMAN_HANDOFF.value:
        return {
            "answer": "Minh se chuyen yeu cau nay sang kenh ho tro phu hop. Ban co the lien he hotline hoac nhan vien CSKH.",
            "needs_handoff": True,
        }

    if state.get("route") == Route.UNSUPPORTED.value:
        return {
            "answer": "Minh chua the ho tro yeu cau nay trong pham vi chatbot benh vien.",
            "needs_handoff": True,
        }

    answer = await generate_grounded_answer(state)
    return {"answer": answer}
