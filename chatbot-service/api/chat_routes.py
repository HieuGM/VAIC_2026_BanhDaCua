from typing import Any

from fastapi import APIRouter

from api.chat_schemas import ChatRequest, ChatResponse
from graph.builder import build_chat_graph


router = APIRouter(tags=["chat"])
chat_graph = build_chat_graph()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    state: dict[str, Any] = {
        "session_id": request.session_id,
        "user_id": request.user_id,
        "user_role": request.user_role,
        "message": request.text,
        "allowed_patient_ids": request.allowed_patient_ids,
        "context": request.context,
        "lang": request.lang,
    }
    result = await chat_graph.ainvoke(state)
    return ChatResponse(
        answer=result.get("answer") or "",
        citations=result.get("citations") or [],
        confidence=float(result.get("confidence") or 0),
        guardrailFlags=result.get("safety_flags") or [],
        intent=result.get("intent") or "UNKNOWN",
        route=result.get("route") or "UNSUPPORTED",
        redirection=result.get("redirection"),
        needsHandoff=bool(result.get("needs_handoff")),
        metadata=result.get("metadata") or {},
    )
