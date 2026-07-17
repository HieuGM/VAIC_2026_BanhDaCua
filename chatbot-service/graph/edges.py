from core.enums import Route
from core.state import ChatState


def route_after_emergency(state: ChatState) -> str:
    if state.get("route") == Route.EMERGENCY.value:
        return "answer"
    return "intent_router"


def route_after_intent(state: ChatState) -> str:
    route = state.get("route")
    if route == Route.PUBLIC_RAG.value:
        return "rag"
    if route == Route.PUBLIC_TOOL.value:
        return "public_tool"
    if route == Route.AUTHENTICATED_FHIR.value:
        return "fhir"
    if route == Route.FIXED_HYBRID.value:
        return "hybrid"
    return "answer"
